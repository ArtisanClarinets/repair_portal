/** biome-ignore-all lint/correctness/noUnusedVariables: Legacy pattern for Frappe pages */
/** biome-ignore-all lint/complexity/useArrowFunction: Legacy pattern for Frappe pages */
frappe.pages['desk-tuner'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Desk Tuner'),
		single_column: true
	});

	frappe.breadcrumbs.add("Lab", "Desk Tuner");

	// --- UI and Styling ---
	const ui = `
        <style>
            .tuner-wrapper {
                max-width: 450px;
                margin: 40px auto;
                padding: 30px;
                background-color: var(--fg-color);
                border-radius: var(--border-radius-xl);
                box-shadow: var(--shadow-lg);
                text-align: center;
            }
            .tuner-display {
                margin-bottom: 30px;
            }
            .note-name {
                font-size: 5rem;
                font-weight: 700;
                line-height: 1;
                color: var(--text-color);
                transition: color 0.4s ease;
                height: 80px; /* Reserve space to prevent layout shift */
            }
            .note-details {
                font-size: 1.1rem;
                color: var(--text-muted);
                height: 25px; /* Reserve space */
            }
            .tuner-meter {
                position: relative;
                height: 60px;
                width: 100%;
                border-bottom: 2px solid var(--border-color);
                margin-bottom: 35px;
            }
            .tuner-needle {
                position: absolute;
                bottom: -2px;
                left: 50%;
                width: 4px;
                height: 100%;
                background-color: var(--red-500);
                transform-origin: bottom center;
                transform: translateX(-50%) rotate(0deg);
                transition: transform 0.2s ease-out, background-color 0.4s ease;
                border-radius: 4px 4px 0 0;
            }
            .in-tune .note-name, .in-tune .tuner-needle {
                color: var(--green-500);
                background-color: var(--green-500);
            }
            .meter-line {
                position: absolute;
                bottom: 0;
                width: 2px;
                background-color: var(--border-color);
            }
            .meter-line.center { left: 50%; height: 100%; transform: translateX(-50%); }
            .meter-line.side { height: 50%; }
            .meter-line.side.l-25 { left: 25%; }
            .meter-line.side.r-25 { right: 25%; }
            #tuner-error {
                display: none;
                margin-top: 15px;
            }
        </style>
        <div class="tuner-wrapper">
            <div class="tuner-display">
                <div id="note-name" class="note-name">--</div>
                <div id="note-details" class="note-details">
                    <span>A4 = 440 Hz</span>
                </div>
            </div>
            <div class="tuner-meter">
                <div class="meter-line center"></div>
                <div class="meter-line side l-25"></div>
                <div class="meter-line side r-25"></div>
                <div id="tuner-needle" class="tuner-needle"></div>
            </div>
            <div class="tuner-controls">
                <button id="tuner-toggle-button" class="btn btn-primary btn-lg" style="width: 200px;">
                    <i class="fa fa-microphone" style="margin-right: 8px;"></i>
                    <span>${__('Start Tuner')}</span>
                </button>
            </div>
            <div id="tuner-error" class="text-danger"></div>
        </div>
    `;
	$(wrapper).html(ui);

	// --- Tuner Logic ---
	const Tuner = {
		isInitialized: false,
		isRunning: false,
		audioContext: null,
		analyser: null,
		stream: null,
		source: null,
		dataArray: null,
		animationFrameId: null,
		noteStrings: ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
		A4: 440,
		minSamples: 0,
		goodCorrelation: 0.9,

		init: async function () {
			try {
				this.isInitialized = true;
				this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
				this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
				this.analyser = this.audioContext.createAnalyser();
				this.analyser.fftSize = 2048;
				this.dataArray = new Float32Array(this.analyser.fftSize);
				this.source = this.audioContext.createMediaStreamSource(this.stream);
				this.source.connect(this.analyser);
				this.isRunning = true;
				this.updateUIState('running');
				this.detectPitch();
			} catch (err) {
				frappe.log_error("Error initializing tuner:", err);
				this.showError(__('Microphone access denied. Please allow microphone access in your browser settings.'));
				this.isInitialized = false;
			}
		},

		start: function () {
			if (this.isInitialized && !this.isRunning) {
				// Resume if context was suspended
				this.audioContext.resume().then(() => {
					this.isRunning = true;
					this.updateUIState('running');
					this.detectPitch();
				});
			} else if (!this.isInitialized) {
				this.init();
			}
		},

		stop: function () {
			if (!this.isRunning) return;
			this.isRunning = false;
			cancelAnimationFrame(this.animationFrameId);
			this.updateUIState('stopped');
			// Suspend context instead of closing to allow quick restart
			if (this.audioContext) this.audioContext.suspend();
		},

		cleanup: function () {
			// Full cleanup for when the user leaves the page
			if (this.stream) {
				this.stream.getTracks().forEach(track => track.stop());
			}
			if (this.audioContext && this.audioContext.state !== 'closed') {
				this.audioContext.close();
			}
			this.isInitialized = false;
			this.isRunning = false;
		},

		detectPitch: function () {
			this.analyser.getFloatTimeDomainData(this.dataArray);
			const pitch = this.autoCorrelate(this.dataArray, this.audioContext.sampleRate);

			if (pitch !== -1) {
				this.updateDisplay(pitch);
			} else {
				this.resetDisplay();
			}

			if (this.isRunning) {
				this.animationFrameId = requestAnimationFrame(() => this.detectPitch());
			}
		},

		autoCorrelate: function (buf, sampleRate) {
			let SIZE = buf.length;
			let rms = 0;
			for (let i = 0; i < SIZE; i++) rms += buf[i] * buf[i];
			rms = Math.sqrt(rms / SIZE);
			if (rms < 0.01) return -1; // Not enough signal

			let r1 = 0, r2 = SIZE - 1, thres = 0.2;
			for (let i = 0; i < SIZE / 2; i++) if (Math.abs(buf[i]) < thres) { r1 = i; break; }
			for (let i = 1; i < SIZE / 2; i++) if (Math.abs(buf[SIZE - i]) < thres) { r2 = SIZE - i; break; }
			buf = buf.slice(r1, r2);
			SIZE = buf.length;

			const c = new Float32Array(SIZE).fill(0);
			for (let i = 0; i < SIZE; i++) {
				for (let j = 0; j < SIZE - i; j++) {
					c[i] = c[i] + buf[j] * buf[j + i];
				}
			}

			let d = 0; while (c[d] > c[d + 1]) d++;
			let maxval = -1, maxpos = -1;
			for (let i = d; i < SIZE; i++) {
				if (c[i] > maxval) { maxval = c[i]; maxpos = i; }
			}

			let T0 = maxpos;
			const x1 = c[T0 - 1], x2 = c[T0], x3 = c[T0 + 1];
			const a = (x1 + x3 - 2 * x2) / 2;
			const b = (x3 - x1) / 2;
			if (a) T0 = T0 - b / (2 * a);

			if (T0 === 0) return -1;
			return sampleRate / T0;
		},

		updateDisplay: function (pitch) {
			const noteNumber = 12 * (Math.log(pitch / this.A4) / Math.log(2));
			const roundedNoteNumber = Math.round(noteNumber);
			const targetFreq = this.A4 * Math.pow(2, roundedNoteNumber / 12);
			const cents = 1200 * Math.log2(pitch / targetFreq);
			const noteIndex = (roundedNoteNumber + 69) % 12;
			const noteName = this.noteStrings[noteIndex];

			// Update UI elements
			$('#note-name').text(noteName);
			$('#note-details').html(`
                <span>${pitch.toFixed(2)} Hz</span> | <span>${cents.toFixed(1)} cents</span>
            `);

			// Update meter
			const rotation = (cents / 50) * 45; // Max 45 degrees rotation for 50 cents
			$('#tuner-needle').css('transform', `translateX(-50%) rotate(${Math.max(-45, Math.min(45, rotation))}deg)`);

			// Update color for "in-tune" status
			if (Math.abs(cents) < 5) { // Threshold of +/- 5 cents
				$('.tuner-wrapper').addClass('in-tune');
			} else {
				$('.tuner-wrapper').removeClass('in-tune');
			}
		},

		resetDisplay: function () {
			$('#note-name').text('--');
			$('#note-details').html(`<span>A4 = ${this.A4} Hz</span>`);
			$('#tuner-needle').css('transform', `translateX(-50%) rotate(0deg)`);
			$('.tuner-wrapper').removeClass('in-tune');
		},

		showError: function (message) {
			$('#tuner-error').text(message).show();
			$('#tuner-toggle-button').prop('disabled', true);
		},

		updateUIState: function (state) {
			const $button = $('#tuner-toggle-button');
			const $icon = $button.find('i');
			const $text = $button.find('span');

			if (state === 'running') {
				$button.removeClass('btn-primary').addClass('btn-danger');
				$icon.removeClass('fa-microphone').addClass('fa-stop');
				$text.text(__('Stop Tuner'));
			} else { // stopped
				$button.removeClass('btn-danger').addClass('btn-primary');
				$icon.removeClass('fa-stop').addClass('fa-microphone');
				$text.text(__('Start Tuner'));
				this.resetDisplay();
			}
		}
	};

	// --- Event Handlers ---
	$('#tuner-toggle-button').on('click', function () {
		if (Tuner.isRunning) {
			Tuner.stop();
		} else {
			Tuner.start();
		}
	});

	// Cleanup resources when user navigates away
	page.wrapper.on('page-leave', function () {
		Tuner.cleanup();
	});
};