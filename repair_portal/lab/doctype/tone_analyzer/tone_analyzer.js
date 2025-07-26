/**
 * @file Client-side controller for the Tone and Intonation Analyzer DocType.
 * @version 7.1
 * @copyright 2025, Artisan Clarinets AI Division
 *
 * @description
 * This script powers the real-time analysis tool within the DocType form.
 * It is fully self-contained, creating its AudioWorklet processor from a string
 * and dynamically injecting its own CSS for a zero-dependency setup. It is
 * designed for high performance, maintainability, and a professional user experience.
 */

frappe.ui.form.on('Tone and Intonation Analyzer', {
	/**
	 * Main entry point. Called when the form is loaded and ready.
	 * @param {object} frm - The Frappe form object.
	 */
	refresh: (frm) => {
		// Initialize the analyzer only once per form instance.
		if (!frm.analyzer) {
			frm.analyzer = new ToneAnalyzer(frm);
		}
		// Render the harmonics chart every time the form is refreshed,
		// as the underlying data may have changed after a save.
		frm.analyzer.renderHarmonicsChart();
	},

	/**
	 * When the reference pitch field is changed by the user, update the analyzer.
	 * @param {object} frm - The Frappe form object.
	 */
	reference_pitch: (frm) => {
		if (frm.analyzer) {
			frm.analyzer.updateReferencePitch();
		}
	},

	/**
	 * Clean up resources when the form is closed or navigated away from.
	 * This prevents the microphone from staying active in the background.
	 * @param {object} frm - The Frappe form object.
	 */
	on_close: (frm) => {
		if (frm.analyzer?.state.isRunning) {
			frm.analyzer.stop();
		}
	}
});

class ToneAnalyzer {
	// --- Static Configuration ---
	static CONFIG = {
		PITCH_TOLERANCE_CENTS: 5,
		MIN_CLARITY_THRESHOLD: 0.9,
		MIN_RMS_THRESHOLD: 0.01,
		GAUGE_NEEDLE_IN_TUNE_COLOR: '#28a745',
		GAUGE_NEEDLE_SHARP_COLOR: '#e67e22',
		GAUGE_NEEDLE_FLAT_COLOR: '#3498db',
	};

	// --- Self-contained AudioWorklet Processor ---
	// This code runs in a separate thread for non-blocking audio processing.
	// Embedding it as a string makes the entire component self-contained.
	static PITCH_PROCESSOR_CODE = `
        class Yin {
            constructor(sampleRate, threshold) { this.sampleRate = sampleRate; this.threshold = threshold; this.bufferSize = 1024; this.yinBuffer = new Float32Array(512); }
            getPitch(data) {
                let tauEstimate = -1;
                for (let tau = 0; tau < 512; tau++) { this.yinBuffer[tau] = 0; for (let i = 0; i < 512; i++) { const delta = data[i] - data[i + tau]; this.yinBuffer[tau] += delta * delta; } }
                let runningSum = 0; this.yinBuffer[0] = 1;
                for (let tau = 1; tau < 512; tau++) { runningSum += this.yinBuffer[tau]; this.yinBuffer[tau] *= tau / runningSum; }
                for (let tau = 1; tau < 512; tau++) { if (this.yinBuffer[tau] < this.threshold) { tauEstimate = tau; while (tau + 1 < 512 && this.yinBuffer[tau + 1] < this.yinBuffer[tau]) tauEstimate = ++tau; break; } }
                if (tauEstimate === -1) return { pitch: -1, clarity: 0 };
                const x0 = (tauEstimate < 1) ? tauEstimate : tauEstimate - 1; const x2 = (tauEstimate + 1 < 512) ? tauEstimate + 1 : tauEstimate;
                const s0 = this.yinBuffer[x0], s1 = this.yinBuffer[tauEstimate], s2 = this.yinBuffer[x2];
                const betterTau = tauEstimate + (s2 - s0) / (2 * (2 * s1 - s2 - s0));
                return { pitch: this.sampleRate / betterTau, clarity: 1 - this.yinBuffer[tauEstimate] };
            }
        }
        class ToneProcessor extends AudioWorkletProcessor {
            constructor(options) { super(); this.yin = new Yin(sampleRate, options.processorOptions.threshold); this.minRms = options.processorOptions.minRms; }
            process(inputs) {
                const channel = inputs[0][0];
                if (!channel) return true;
                const rms = Math.sqrt(channel.reduce((s, v) => s + v * v, 0) / channel.length);
                this.port.postMessage(rms > this.minRms ? this.yin.getPitch(channel) : { pitch: -1, clarity: 0 });
                return true;
            }
        }
        registerProcessor('tone-processor', ToneProcessor);
    `;

	constructor(frm) {
		this.frm = frm;
		this.state = this._getInitialState();
		this.noteNames = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
		this.harmonicsChart = null;

		this._injectCSS();
		this._setupUI();
		this._attachEventListeners();
		this._drawInitialUI();
	}

	_getInitialState() {
		return { isRunning: false, audioContext: null, workletNode: null, micStream: null, animationFrameId: null, noteName: '--', octave: '', cents: 0, a4: 440 };
	}

	_setupUI() {
		const container = this.frm.get_field("analyzer_html").$wrapper;
		this.elements = {
			container: container.find("#tone-analyzer-container")[0],
			canvas: container.find('#tuner-canvas')[0],
			noteNameDisplay: container.find('#note-display-name')[0],
			noteOctaveDisplay: container.find('#note-display-octave')[0],
			centsDisplay: container.find('#cents-display')[0],
			toggleBtn: container.find('#toggle-analysis-btn')[0],
			statusLight: container.find('#analyzer-status-light')[0],
			statusText: container.find('#analyzer-status-text')[0],
			messageArea: container.find('#analyzer-message-area')[0],
			harmonicsChartWrapper: this.frm.get_field("harmonics_chart_html").$wrapper,
		};
		this.elements.canvasContext = this.elements.canvas.getContext('2d');
	}

	_attachEventListeners() {
		this.elements.toggleBtn.addEventListener('click', () => this.toggleAnalysis());
		this.updateReferencePitch(); // Set initial value from form
	}

	async toggleAnalysis() {
		await (this.state.isRunning ? this.stop() : this.start());
	}

	async start() {
		if (this.state.isRunning) return;
		this._showMessage(null);

		try {
			this.updateReferencePitch();
			this.state.audioContext = new AudioContext();
			const processorBlob = new Blob([ToneAnalyzer.PITCH_PROCESSOR_CODE], { type: 'application/javascript' });
			const processorUrl = URL.createObjectURL(processorBlob);
			await this.state.audioContext.audioWorklet.addModule(processorUrl);
			URL.revokeObjectURL(processorUrl);

			this.state.micStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false } });

			const micSource = this.state.audioContext.createMediaStreamSource(this.state.micStream);
			this.state.workletNode = new AudioWorkletNode(this.state.audioContext, 'tone-processor', { processorOptions: { threshold: 0.15, minRms: ToneAnalyzer.CONFIG.MIN_RMS_THRESHOLD } });
			this.state.workletNode.port.onmessage = (e) => this._handleProcessorMessage(e);
			micSource.connect(this.state.workletNode);

			this.state.isRunning = true;
			this._updateUIForState('running');
			this._animationLoop();
		} catch (error) {
			frappe.log_error("Audio Analysis Error:", error);
			this._showMessage("Could not start audio. Please grant microphone permissions in your browser.", 'error');
			await this.stop();
		}
	}

	async stop() {
		if (this.state.micStream) this.state.micStream.getTracks().forEach(t => t.stop());
		if (this.state.audioContext && this.state.audioContext.state !== 'closed') await this.state.audioContext.close();
		if (this.state.animationFrameId) cancelAnimationFrame(this.state.animationFrameId);

		Object.assign(this.state, this._getInitialState());
		this.updateReferencePitch(); // Reset A4 to form value
		this._updateUIForState('idle');
		this._drawInitialUI();
	}

	_handleProcessorMessage({ data }) {
		if (!this.state.isRunning) return;
		if (data.pitch > 0 && data.clarity > ToneAnalyzer.CONFIG.MIN_CLARITY_THRESHOLD) {
			const { noteName, octave, cents } = this._frequencyToNote(data.pitch);
			this.state.noteName = noteName; this.state.octave = octave; this.state.cents = cents;
		} else {
			this.state.noteName = '--'; this.state.octave = ''; this.state.cents = 0;
		}
	}

	_animationLoop() {
		if (!this.state.isRunning) return;
		this._updateTextDisplays();
		this._drawGauge();
		this.state.animationFrameId = requestAnimationFrame(() => this._animationLoop());
	}

	_drawInitialUI() {
		this._updateTextDisplays();
		this._drawGauge();
	}

	_updateUIForState(state) {
		this.frm.toggle_enable("reference_pitch", state !== 'running');
		if (state === 'running') {
			this.elements.statusLight.className = 'status-light-on';
			this.elements.statusText.textContent = 'Active';
			this.elements.toggleBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#fff" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12"></rect></svg> <span>Stop Analysis</span>`;
			this.elements.toggleBtn.classList.replace('btn-primary', 'btn-danger');
		} else {
			this.elements.statusLight.className = 'status-light-off';
			this.elements.statusText.textContent = 'Idle';
			this.elements.toggleBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg> <span>Start Analysis</span>`;
			this.elements.toggleBtn.classList.replace('btn-danger', 'btn-primary');
		}
	}

	_updateTextDisplays() {
		this.elements.noteNameDisplay.textContent = this.state.noteName;
		this.elements.noteOctaveDisplay.textContent = this.state.octave;
		const cents = this.state.cents;
		this.elements.centsDisplay.textContent = `${cents.toFixed(1)} cents`;

		if (Math.abs(cents) < ToneAnalyzer.CONFIG.PITCH_TOLERANCE_CENTS) this.elements.centsDisplay.className = 'cents-display-in-tune';
		else if (cents > 0) this.elements.centsDisplay.className = 'cents-display-sharp';
		else this.elements.centsDisplay.className = 'cents-display-flat';
	}

	_drawGauge() {
		const ctx = this.elements.canvasContext;
		const { width, height } = this.elements.canvas;
		ctx.clearRect(0, 0, width, height);

		const centerX = width / 2;
		const centerY = height * 0.9;
		const radius = width * 0.4;

		// Draw Arc
		ctx.beginPath();
		ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
		ctx.strokeStyle = '#bdc3c7';
		ctx.lineWidth = 2;
		ctx.stroke();
		const zoneAngle = (ToneAnalyzer.CONFIG.PITCH_TOLERANCE_CENTS / 50) * (Math.PI / 2);
		ctx.beginPath();
		ctx.arc(centerX, centerY, radius, Math.PI * 1.5 - zoneAngle, Math.PI * 1.5 + zoneAngle);
		ctx.strokeStyle = 'rgba(40, 167, 69, 0.15)';
		ctx.lineWidth = 10;
		ctx.stroke();

		// Draw Needle
		const clampedCents = Math.max(-50, Math.min(50, this.state.cents));
		const angle = Math.PI + ((clampedCents + 50) / 100) * Math.PI;
		const isInTune = Math.abs(clampedCents) < ToneAnalyzer.CONFIG.PITCH_TOLERANCE_CENTS;
		const  needleColor = isInTune ? ToneAnalyzer.CONFIG.GAUGE_NEEDLE_IN_TUNE_COLOR : (clampedCents > 0 ? ToneAnalyzer.CONFIG.GAUGE_NEEDLE_SHARP_COLOR : ToneAnalyzer.CONFIG.GAUGE_NEEDLE_FLAT_COLOR);

		ctx.save();
		ctx.translate(centerX, centerY);
		ctx.rotate(angle);
		ctx.fillStyle = needleColor;
		ctx.beginPath();
		ctx.moveTo(0, -4);
		ctx.lineTo(radius, 0);
		ctx.lineTo(0, 4);
		ctx.closePath();
		ctx.fill();
		ctx.restore();
	}

	updateReferencePitch() {
		this.state.a4 = parseInt(this.frm.doc.reference_pitch.split(" ")[0]) || 440;
	}

	_frequencyToNote(frequency) {
		const noteNum = 12 * (Math.log2(frequency / this.state.a4)) + 69;
		const roundedNoteNum = Math.round(noteNum);
		const cents = 1200 * Math.log2(frequency / (this.state.a4 * Math.pow(2, (roundedNoteNum - 69) / 12)));
		return { noteName: this.noteNames[roundedNoteNum % 12], octave: (Math.floor(roundedNoteNum / 12) - 1).toString(), cents };
	}

	_showMessage(message, type = 'info') {
		this.elements.messageArea.style.display = message ? 'block' : 'none';
		this.elements.messageArea.textContent = message;
		this.elements.messageArea.className = `analyzer-message message-${type}`;
	}

	renderHarmonicsChart() {
		const jsonData = this.frm.doc.harmonics_json;
		if (!jsonData) {
			this.elements.harmonicsChartWrapper.hide();
			return;
		}
		this.elements.harmonicsChartWrapper.show();
		try {
			const values = JSON.parse(jsonData);
			if (!values || !Array.isArray(values) || values.length === 0) {
				this.elements.harmonicsChartWrapper.hide();
				return;
			}
			const data = {
				labels: Array.from({ length: values.length }, (_, i) => `H${i + 1}`),
				datasets: [{ values }]
			};
			if (!this.harmonicsChart) {
				this.harmonicsChart = new frappe.Chart(this.elements.harmonicsChartWrapper[0], {
					title: "Relative Harmonic Energy (from Batch Analysis)", data: data, type: 'bar', height: 250, colors: ['#0d6efd']
				});
			} else {
				this.harmonicsChart.update(data);
			}
		} catch (e) {
			frappe.log_error("Error Title", frappe.get_traceback());
			frappe.msgprint("Failed to parse or render harmonics chart", e);
			this.elements.harmonicsChartWrapper.hide();
		}
	}

	_injectCSS() {
		const css = `
            .tone-analyzer-wrapper { --border-color: #e0e0e0; --primary-text-color: #2c3e50; --secondary-text-color: #7f8c8d; --accent-color-success: #28a745; font-family: -apple-system, sans-serif; background-color: #ffffff; border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
            .analyzer-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px; }
            .header-title { display: flex; align-items: center; font-size: 1.1rem; font-weight: 600; color: var(--primary-text-color); }
            .header-title svg { margin-right: 10px; color: var(--secondary-text-color); }
            .status-indicator-wrapper { display: flex; align-items: center; font-size: 0.9rem; color: var(--secondary-text-color); }
            #analyzer-status-light { width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; transition: background-color 0.3s ease; }
            .status-light-off { background-color: #bdc3c7; }
            .status-light-on { background-color: var(--accent-color-success); box-shadow: 0 0 8px rgba(40, 167, 69, 0.7); }
            .analyzer-body { text-align: center; }
            .gauge-container { margin-bottom: 10px; }
            #tuner-canvas { max-width: 100%; height: auto; }
            .readout-container { margin-bottom: 25px; }
            .note-display-wrapper { line-height: 1; margin-bottom: 8px; color: var(--primary-text-color); }
            #note-display-name { font-size: 4.5rem; font-weight: 700; }
            #note-display-octave { font-size: 1.5rem; font-weight: 400; margin-left: 2px; color: var(--secondary-text-color); }
            .cents-display-neutral, .cents-display-in-tune, .cents-display-sharp, .cents-display-flat { font-size: 1.2rem; font-weight: 500; padding: 4px 12px; border-radius: 15px; display: inline-block; min-width: 120px; transition: background-color 0.2s, color 0.2s; }
            .cents-display-neutral { color: var(--primary-text-color); background-color: #ecf0f1; }
            .cents-display-in-tune { color: #fff; background-color: var(--accent-color-success); }
            .cents-display-sharp { color: #fff; background-color: #e67e22; }
            .cents-display-flat { color: #fff; background-color: #3498db; }
            .analyzer-controls .btn { display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 600; padding: 12px; border-radius: 5px; }
            .analyzer-message { font-size: 0.9rem; padding: 12px; border-radius: 4px; margin-top: 20px; text-align: center; }
            .message-error { background-color: #fbeae5; color: #e74c3c; border: 1px solid #e74c3c; }
        `;
		const styleId = 'tone-analyzer-styles';
		if (!document.getElementById(styleId)) {
			const style = document.createElement('style');
			style.id = styleId;
			style.innerHTML = css;
			document.head.appendChild(style);
		}
	}
}
