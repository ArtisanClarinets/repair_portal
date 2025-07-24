/**
 * @file Client-side controller for the Tone & Intonation Analyzer DocType.
 * @version 5.0
 * @date 2025-07-23
 * @description
 * This script provides a production-grade, real-time audio analysis interface.
 * It uses AudioWorklet for non-blocking audio processing and renders a dynamic
 * UI with baseline comparison capabilities.
 * @requires /assets/repair_portal/js/tone-processor.js
 */
'use strict';

frappe.ui.form.on("Tone & Intonation Analyzer", {
    onload(frm) {
        frm.analyzer = new ToneAnalyzer(frm);
        frm.analyzer.initializeUI();
    },
    refresh(frm) {
        frm.analyzer.renderControls();
        frm.analyzer.drawHarmonicsChart();
    },
    on_close(frm) {
        if (frm.analyzer) frm.analyzer.stop();
    }
});

class ToneAnalyzer {
    constructor(frm) {
        this.frm = frm;
        this.state = {
            isRunning: false,
            audioContext: null,
            workletNode: null,
            micStream: null,
            animationFrameId: null,
            cents: 0,
            noteName: '--',
            inTuneCounter: 0,
            pitchTolerance: 5,
            baseline: null
        };
        this.elements = {};
    }

    initializeUI() {
        const customHTML = this.frm.fields_dict.custom_html.wrapper;
        const harmonicsHTML = this.frm.fields_dict.harmonics_html.wrapper;
        $(harmonicsHTML).html('<div id="harmonics-chart" class="mt-4" style="height: 250px;"></div>');

        this.elements = {
            tunerArea: $(customHTML).find('#tuner-display-area'),
            canvas: $(customHTML).find('#tuner-canvas').get(0),
            noteDisplay: $(customHTML).find('#note-display'),
            inTuneIndicator: $(customHTML).find('#in-tune-indicator'),
            harmonicsChart: $(harmonicsHTML).find('#harmonics-chart').get(0)
        };
        this.elements.canvasContext = this.elements.canvas.getContext('2d');
    }

    renderControls() {
        this.frm.page.clear_custom_buttons();
        this.frm.add_custom_button(
            this.state.isRunning ? "■ Stop Live Analysis" : "▶ Analyze Live Tone",
            () => this.toggleAnalysis(),
            this.state.isRunning ? "btn-danger" : "btn-primary"
        );
        this.frm.add_custom_button("Load Baseline", () => this.fetchAndDisplayBaseline());
    }

    toggleAnalysis() {
        this.state.isRunning ? this.stop() : this.start();
    }

    async start() {
        if (this.state.isRunning) return;
        try {
            this.state.audioContext = new AudioContext({ sampleRate: 44100 });
            const workletPath = frappe.get_asset_path('js/tone-processor.js');
            await this.state.audioContext.audioWorklet.addModule(workletPath);

            this.state.micStream = await navigator.mediaDevices.getUserMedia({
                audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false }
            });

            const micSource = this.state.audioContext.createMediaStreamSource(this.state.micStream);
            this.state.workletNode = new AudioWorkletNode(this.state.audioContext, 'tone-processor');
            this.state.workletNode.port.onmessage = this.handleProcessorMessage.bind(this);
            micSource.connect(this.state.workletNode);

            this.state.isRunning = true;
            this.elements.tunerArea.show();
            this.renderControls();
            this.animationLoop();
        } catch (error) {
            frappe.log_error("Failed to start audio analysis:", error);
            frappe.throw({ title: "Audio Error", message: `Could not start analysis. Please grant microphone permissions and ensure your browser is up to date. Error: ${error.name}` });
            this.stop();
        }
    }

    stop() {
        this.state.micStream?.getTracks().forEach(track => track.stop());
        this.state.audioContext?.state !== 'closed' && this.state.audioContext?.close();
        this.state.animationFrameId && cancelAnimationFrame(this.state.animationFrameId);
        this.state = { ...this.state, isRunning: false, audioContext: null, micStream: null, animationFrameId: null };
        this.elements.tunerArea.hide();
        this.renderControls();
    }

    handleProcessorMessage(event) {
        if (!this.state.isRunning) return;
        frappe.call({
            method: "repair_portal.lab.doctype.tone_intonation_analyzer.tone_intonation_analyzer.run_live_analysis",
            args: {
                chunk: Array.from(event.data),
                a_ref: parseInt(this.frm.doc.reference_pitch.split("=")[1]) || 440
            },
            callback: r => {
                if (r.message && this.state.isRunning) {
                    this.state.cents = r.message.cents_dev || 0;
                    this.state.noteName = r.message.note_name || '--';
                }
            }
        });
    }

    animationLoop() {
        if (!this.state.isRunning) return;
        this.updateDisplays();
        this.drawGauge();
        this.state.animationFrameId = requestAnimationFrame(this.animationLoop.bind(this));
    }

    updateDisplays() {
        this.elements.noteDisplay.text(this.state.noteName);
        const isInTune = Math.abs(this.state.cents) < this.state.pitchTolerance && this.state.noteName !== '--';
        this.state.inTuneCounter = isInTune ? this.state.inTuneCounter + 1 : 0;
        this.elements.inTuneIndicator.text(this.state.inTuneCounter > 15 ? '😊' : '');
    }

    drawGauge() {
        const ctx = this.elements.canvasContext;
        const { width, height } = this.elements.canvas;
        ctx.clearRect(0, 0, width, height);
        const cx = width / 2, cy = height * 0.9, r = width * 0.4;

        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI);
        ctx.strokeStyle = '#6c757d';
        ctx.lineWidth = 2;
        ctx.stroke();

        const zoneAngle = (this.state.pitchTolerance / 50) * (Math.PI / 2);
        ctx.beginPath();
        ctx.arc(cx, cy, r, Math.PI * 1.5 - zoneAngle, Math.PI * 1.5 + zoneAngle);
        ctx.strokeStyle = 'rgba(40, 167, 69, 0.5)';
        ctx.lineWidth = 6;
        ctx.stroke();
        ctx.restore();

        const clampedCents = Math.max(-50, Math.min(50, this.state.cents));
        const angle = Math.PI + ((clampedCents + 50) / 100) * Math.PI;
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(angle);
        ctx.beginPath();
        ctx.moveTo(0, -4);
        ctx.lineTo(r * 0.9, 0);
        ctx.lineTo(0, 4);
        ctx.closePath();
        ctx.fillStyle = Math.abs(clampedCents) < this.state.pitchTolerance ? '#28a745' : '#dc3545';
        ctx.fill();
        ctx.restore();
    }

    async fetchAndDisplayBaseline() {
        if (!this.frm.doc.instrument) {
            frappe.show_alert({ message: "Please select an instrument first.", indicator: "orange" });
            return;
        }
        try {
            const baselineData = await frappe.call({ doc: this.frm.doc, method: "get_baseline_for_instrument" });
            this.state.baseline = baselineData.message || null;
            if (this.state.baseline) {
                frappe.show_alert({ message: `Baseline from analysis ${this.state.baseline.name} loaded.`, indicator: "green" });
            } else {
                frappe.show_alert({ message: "No baseline found for this instrument.", indicator: "gray" });
            }
            this.drawHarmonicsChart();
        } catch (e) {
            frappe.log_error(e);
        }
    }

    drawHarmonicsChart() {
        if (!this.frm.doc.harmonics_json) {
            $(this.elements.harmonicsChart).hide();
            return;
        }
        $(this.elements.harmonicsChart).show();

        const values = JSON.parse(this.frm.doc.harmonics_json);
        if (!values?.length) return;

        const datasets = [{ name: "Current", values, chartType: 'bar' }];
        if (this.state.baseline?.harmonics_json) {
            datasets.push({ name: "Baseline", values: this.state.baseline.harmonics_json, chartType: 'line' });
        }
        const data = {
            labels: Array.from({ length: 10 }, (_, i) => `H${i + 1}`),
            datasets: datasets
        };

        if (!this.harmonicsChartInstance) {
            this.harmonicsChartInstance = new frappe.Chart(this.elements.harmonicsChart, {
                title: "Harmonic Energy vs. Baseline", data, type: 'axis-mixed', height: 250,
                colors: ['#0d6efd', '#6c757d'],
                tooltipOptions: { formatTooltipY: d => d?.toFixed(4) || "" }
            });
        } else {
            this.harmonicsChartInstance.update(data);
        }
    }
}

/**
 * @class ToneProcessor
 * @extends AudioWorkletProcessor
 *
 * This processor runs in a separate thread to receive audio data. It posts
 * the raw audio buffer to the main thread for analysis, preventing UI blocking.
 * It includes throttling to avoid overwhelming the main thread with messages.
 */
class ToneProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.lastUpdate = 0;
        this.updateInterval = 100; // ms
    }

    process(inputs) {
        const input = inputs[0];
        const channel = input[0];
        const now = currentTime * 1000;

        if (channel && now - this.lastUpdate > this.updateInterval) {
            // Post the Float32Array back to the main thread.
            // The second argument transfers ownership, avoiding a copy.
            this.port.postMessage(channel, [channel.buffer]);
            this.lastUpdate = now;
        }
        // Return true to keep the processor alive.
        return true;
    }
}

registerProcessor('tone-processor', ToneProcessor);