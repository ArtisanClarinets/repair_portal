/** biome-ignore-all lint/correctness/noUnusedVariables */
/** biome-ignore-all lint/complexity/useArrowFunction */
frappe.pages["desk-tuner"].on_page_load = function (wrapper) {
	// jQuery alias must come BEFORE any use of $ to avoid TDZ issues
	const $ = window.jQuery;

	// ---------------------------------------------------------------------------
	// Desk Tuner Pro (Frappe v15)
	// - Robust YIN pitch with smoothing & outlier handling (refactored loop)
	// - Concert/Written display with clarinet transpositions
	// - A4 calibration (430–446), persistence, device selection
	// - Needle + Strobe + level meter
	// - In-app FFT (radix-2) w/ Hann window + LOG-FREQUENCY spectrum
	// - Real-time console: Spectrum/Spectrogram/Harmonics/Cents/Autocorr/Waveform
	// - Metrics: mean/std/drift/vibrato/odd-even/attack/jitter/shimmer/hiss
	// ---------------------------------------------------------------------------

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Desk Tuner"),
		single_column: true
	});
	frappe.breadcrumbs.add("Lab", "Desk Tuner");

	// --- UI --------------------------------------------------------------------
	const ui = `
<style>
	.tuner-wrapper{max-width:1100px;margin:24px auto;padding:24px;background-color:var(--fg-color);border-radius:var(--border-radius-xl);box-shadow:var(--shadow-lg)}
	.grid-2{display:grid;grid-template-columns:1fr;gap:18px}
	@media (min-width:1000px){.grid-2{grid-template-columns:1fr 1fr}}
	.section{padding:16px;border:1px solid var(--border-color);border-radius:var(--border-radius-md)}
	.section h5{margin:0 0 12px 0}
	.tuner-display{text-align:center}
	.note-name{font-size:5rem;font-weight:700;line-height:1;color:var(--text-color);transition:color .2s ease;min-height:80px}
	.note-meta{color:var(--text-muted);min-height:24px;font-size:1rem}
	.in-tune .note-name{color:var(--green-500)}
	.meter-wrap{position:relative;height:68px;margin-top:10px}
	.meter-scale{position:absolute;left:0;right:0;bottom:8px;height:2px;background:var(--border-color)}
	.meter-ticks{position:absolute;left:0;right:0;bottom:0;height:100%}
	.tick{position:absolute;bottom:6px;width:2px;background:var(--border-color)}
	.tick.center{left:50%;height:100%;transform:translateX(-50%)}
	.tick.side{height:52%}
	.tick.l-25{left:25%}
	.tick.r-25{right:25%}
	.tick-label{position:absolute;bottom:0;transform:translateX(-50%);font-size:.75rem;color:var(--text-muted)}
	.tick-label.left{left:0%}
	.tick-label.mid{left:50%}
	.tick-label.right{left:100%}
	.needle{position:absolute;bottom:0;left:50%;width:4px;height:100%;background:var(--red-500);border-radius:4px 4px 0 0;transform-origin:bottom center;transform:translateX(-50%) rotate(0deg);transition:transform .12s ease-out,background-color .2s ease}
	.in-tune .needle{background:var(--green-500)}
	#strobe-canvas{width:100%;height:120px;display:none;border-radius:8px;border:1px solid var(--border-color);margin-top:10px}
	.level-bar{height:10px;border-radius:999px;background:var(--bg-color);border:1px solid var(--border-color);overflow:hidden}
	.level-fill{height:100%;width:0%;background:var(--blue-500);transition:width .1s linear}
	.controls-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
	@media (max-width:520px){.controls-row{grid-template-columns:1fr}}
	.form-inline{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
	.form-inline label{margin:0 6px 0 0;white-space:nowrap}
	.form-inline input[type="range"]{width:160px}
	.small{font-size:.875rem;color:var(--text-muted)}
	.helper{display:block;margin-top:6px;color:var(--text-muted);font-size:.85rem;line-height:1.35}
	.helper strong{color:var(--text-color)}
	.field{margin-bottom:8px}
	#error-box{display:none}

	/* analytics console */
	.console-grid{display:grid;grid-template-columns:1fr;gap:14px;margin-top:18px}
	@media (min-width:1100px){.console-grid{grid-template-columns:1fr 1fr}}
	.canvas-card{border:1px solid var(--border-color);border-radius:8px;padding:10px}
	.canvas-title{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
	.canvas-title h6{margin:0}
	canvas.analytics{width:100%;height:180px;border-radius:6px;background:var(--bg-color);display:block}
	canvas.analytics.tall{height:220px}
	.metric-row{display:flex;gap:10px;flex-wrap:wrap}
	.metric{border:1px dashed var(--border-color);border-radius:8px;padding:8px 10px;min-width:160px}
	.metric .val{font-weight:700}
	.console-help{margin:10px 0 6px 0}
	details.help-panel{margin-top:8px;border:1px solid var(--border-color);border-radius:8px;padding:10px;background:var(--bg-color)}
	details.help-panel summary{cursor:pointer;font-weight:600}
	ul.compact{margin:6px 0 0 18px;padding:0}
	ul.compact li{margin:4px 0}
</style>

<div class="tuner-wrapper">
	<div class="grid-2">
		<div class="section" aria-labelledby="pitch-title">
			<h5 id="pitch-title">${__("Pitch Display")}</h5>
			<div class="tuner-display" id="display-root">
				<div id="note-name" class="note-name" aria-live="polite">--</div>
				<div class="note-meta" id="note-meta">A4 = <span id="a4-label">440</span> Hz · <span id="mode-label">Concert</span></div>

				<div class="meter-wrap" id="needle-wrap" aria-label="${__("Tuning meter: -50 to +50 cents")}">
					<div class="meter-scale"></div>
					<div class="meter-ticks" aria-hidden="true">
						<div class="tick center"></div>
						<div class="tick side l-25"></div>
						<div class="tick side r-25"></div>
					</div>
					<div class="needle" id="needle"></div>
					<div class="tick-label left">−50¢</div>
					<div class="tick-label mid">0</div>
					<div class="tick-label right">+50¢</div>
				</div>

				<canvas id="strobe-canvas" aria-label="${__("Strobe visualization")}"></canvas>

				<div style="margin-top:12px;">
					<div class="level-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-label="${__("Input level")}">
						<div class="level-fill" id="level-fill"></div>
					</div>
					<div class="small" id="status-line" style="margin-top:6px;" aria-live="polite">—</div>
				</div>
			</div>
		</div>

		<div class="section" aria-labelledby="controls-title">
			<h5 id="controls-title">${__("Controls")}</h5>

			<div class="field">
				<div class="form-inline" style="margin-bottom:4px;">
					<label for="device-select">${__("Microphone")}</label>
					<select id="device-select" class="form-control" aria-label="${__("Select microphone")}"></select>
					<span class="small" id="device-info">—</span>
				</div>
				<span class="helper">${__("Choose your input device. For best results, disable OS-level noise suppression/AGC for this app.")}</span>
			</div>

			<div class="controls-row">
				<div class="field">
					<div class="form-inline">
						<label for="instrument-select">${__("Instrument")}</label>
						<select id="instrument-select" class="form-control">
							<option value="concert">${__("Concert (no transposition)")}</option>
							<option value="bb">${__("B♭ Clarinet")}</option>
							<option value="a">${__("A Clarinet")}</option>
							<option value="eb">${__("E♭ Clarinet")}</option>
							<option value="bb_bass">${__("Bass Clarinet (B♭)")}</option>
						</select>
					</div>
					<span class="helper">${__("Sets the transposition for written vs. concert pitch display.")}</span>
				</div>

				<div class="field">
					<div class="form-inline">
						<label for="display-mode">${__("Display")}</label>
						<select id="display-mode" class="form-control">
							<option value="concert">${__("Concert")}</option>
							<option value="written">${__("Written (transposed)")}</option>
						</select>
					</div>
					<span class="helper">${__("Switch between concert pitch and written (transposed) pitch.")}</span>
				</div>
			</div>

			<div class="controls-row">
				<div class="field">
					<div class="form-inline">
						<label for="a4-range">A4</label>
						<input id="a4-range" type="range" min="430" max="446" step="1" value="440" aria-label="${__("A4 reference (slider)")}">
						<input id="a4-input" type="number" class="form-control" style="width:90px" min="430" max="446" step="1" value="440" aria-label="${__("A4 reference (number)")}">
					</div>
					<span class="helper">${__("Calibrate reference pitch. Most orchestras use ")}<strong>440 Hz</strong>${__(", some use 441–443 Hz.")}</span>
				</div>

				<div class="field">
					<div class="form-inline">
						<label for="view-mode">${__("View")}</label>
						<select id="view-mode" class="form-control">
							<option value="needle">${__("Needle")}</option>
							<option value="strobe">${__("Strobe")}</option>
							<option value="both">${__("Both")}</option>
						</select>
					</div>
					<span class="helper">${__("Choose classic needle, moving strobe bars, or both.")}</span>
				</div>
			</div>

			<div class="controls-row">
				<div class="field">
					<div class="form-inline">
						<label for="gate-select">${__("Noise Gate")}</label>
						<select id="gate-select" class="form-control">
							<option value="0.005">Low</option>
							<option value="0.01" selected>Medium</option>
							<option value="0.02">High</option>
						</select>
					</div>
					<span class="helper"><strong>${__("What it does")}:</strong> ${__("Ignores very quiet input to avoid false detections.")} <strong>${__("Low")}</strong> = ${__("more sensitive")} · <strong>${__("High")}</strong> = ${__("more rejection in noisy rooms")}.</span>
				</div>

				<div class="field">
					<div class="form-inline">
						<label for="smoothing-select">${__("Smoothing")}</label>
						<select id="smoothing-select" class="form-control">
							<option value="0.2">Fast</option>
							<option value="0.4" selected>Medium</option>
							<option value="0.7">Slow</option>
						</select>
					</div>
					<span class="helper"><strong>${__("What it does")}:</strong> ${__("Applies exponential smoothing to pitch to stabilize the needle.")} <strong>${__("Fast")}</strong> = ${__("snappy")} · <strong>${__("Slow")}</strong> = ${__("steadier (slightly higher latency)")}</span>
				</div>
			</div>

			<div class="controls-row">
				<div class="field">
					<div class="form-inline">
						<label for="fft-select">${__("FFT Size")}</label>
						<select id="fft-select" class="form-control">
							<option value="2048">2048</option>
							<option value="4096" selected>4096</option>
							<option value="8192">8192</option>
						</select>
					</div>
					<span class="helper"><strong>${__("What it does")}:</strong> ${__("Controls frequency resolution vs. latency/CPU.")} ${__("Larger sizes")} = ${__("finer peaks, more CPU, slightly slower reaction")}.</span>
				</div>

				<div class="field">
					<div class="form-inline">
						<label for="dyn-range">${__("Dyn Range (dB)")}</label>
						<input id="dyn-range" type="number" class="form-control" style="width:90px" min="40" max="120" step="5" value="80">
					</div>
					<span class="helper"><strong>${__("What it does")}:</strong> ${__("Sets the vertical range for Spectrum/Spectrogram.")} ${__("Higher values reveal quieter harmonics; lower values increase contrast")}.</span>
				</div>
			</div>

			<div class="controls-row" style="margin-top:6px;">
				<button id="btn-toggle" class="btn btn-primary">
					<i class="fa fa-microphone" style="margin-right: 6px;"></i>${__("Start Tuner")}
				</button>
				<button id="btn-reset" class="btn btn-default">
					<i class="fa fa-refresh" style="margin-right: 6px;"></i>${__("Reset")}
				</button>
			</div>

			<div id="error-box" class="alert alert-danger" style="margin-top:12px;"></div>
		</div>
	</div>

	<!-- analytics console -->
	<div class="section" style="margin-top:18px;" aria-labelledby="console-title">
		<h5 id="console-title">${__("Real-Time Analysis Console")}</h5>
		<div class="console-help small">${__("Live DSP readouts for stability, timbre, and intonation. Hover charts to interpret shape and trend; use Dyn Range to reveal quieter content.")}</div>

		<div class="metric-row" id="metric-row" aria-label="${__("Key performance metrics")}">
			<div class="metric"><div class="small">${__("Mean Cents")}</div><div class="val" id="m-mean">—</div></div>
			<div class="metric"><div class="small">${__("Std Cents")}</div><div class="val" id="m-std">—</div></div>
			<div class="metric"><div class="small">${__("Drift (c/s)")}</div><div class="val" id="m-drift">—</div></div>
			<div class="metric"><div class="small">${__("Vibrato (Hz)")}</div><div class="val" id="m-vib-rate">—</div></div>
			<div class="metric"><div class="small">${__("Vibrato Depth (¢)")}</div><div class="val" id="m-vib-depth">—</div></div>
			<div class="metric"><div class="small">${__("Odd/Even (dB)")}</div><div class="val" id="m-odd-even">—</div></div>
			<div class="metric"><div class="small">${__("Attack (ms)")}</div><div class="val" id="m-attack">—</div></div>
			<div class="metric"><div class="small">${__("Jitter (%)")}</div><div class="val" id="m-jitter">—</div></div>
			<div class="metric"><div class="small">${__("Shimmer (%)")}</div><div class="val" id="m-shimmer">—</div></div>
			<div class="metric"><div class="small">${__("Hiss Index")}</div><div class="val" id="m-hiss">—</div></div>
		</div>

		<details class="help-panel">
			<summary>${__("What am I looking at?")}</summary>
			<ul class="compact">
				<li><strong>${__("Mean/Std Cents")}:</strong> ${__("Average tuning offset and its short-term variability")}.</li>
				<li><strong>${__("Drift")}:</strong> ${__("Trend of cents per second; positive means creeping sharp, negative means flat")}.</li>
				<li><strong>${__("Vibrato (Hz/Depth)")}:</strong> ${__("Estimated vibrato rate and approximate depth in cents")}.</li>
				<li><strong>${__("Odd/Even (dB)")}:</strong> ${__("Relative strength of odd vs. even harmonics; timbre proxy")}.</li>
				<li><strong>${__("Attack")}:</strong> ${__("Time for level to reach ~90% from onset (articulation responsiveness)")}</li>
				<li><strong>${__("Jitter/Shimmer")}:</strong> ${__("Cycle-to-cycle frequency (%) and amplitude (%) variability; stability proxies")}.</li>
				<li><strong>${__("Hiss Index")}:</strong> ${__("High-frequency content ratio; proxy for mechanical/noise floor")}.</li>
			</ul>
			<hr>
			<ul class="compact">
				<li><strong>${__("Spectrum (dB) [Log Freq]")}:</strong> ${__("Hann-windowed FFT shown on a logarithmic frequency axis for better peak separation")}.</li>
				<li><strong>${__("Spectrogram [Log Freq]")}:</strong> ${__("Time-scrolling log-frequency heatmap (vertical = log f, color = level)")}</li>
				<li><strong>${__("Harmonics H1–H10")}:</strong> ${__("Peak-picked near multiples of f0 for robust harmonic levels")}.</li>
				<li><strong>${__("Cents Timeline")}:</strong> ${__("Recent tuning error history with mean/std/drift")}.</li>
				<li><strong>${__("Autocorrelation (Cents)")}:</strong> ${__("Periodicity in cents over time; peaks in 4–8 Hz region indicate vibrato")}.</li>
				<li><strong>${__("Waveform (Level)")}:</strong> ${__("Raw time-domain view; good for onset/attack inspection")}.</li>
			</ul>
		</details>

		<div class="console-grid" style="margin-top:10px;">
			<div class="canvas-card">
				<div class="canvas-title"><h6>${__("Spectrum (dB)")}</h6><div class="small" id="info-spectrum">—</div></div>
				<canvas id="c-spectrum" class="analytics"></canvas>
			</div>
			<div class="canvas-card">
				<div class="canvas-title"><h6>${__("Spectrogram")}</h6><div class="small" id="info-gram">—</div></div>
				<canvas id="c-gram" class="analytics tall"></canvas>
			</div>
			<div class="canvas-card">
				<div class="canvas-title"><h6>${__("Harmonics H1–H10")}</h6><div class="small" id="info-harm">—</div></div>
				<canvas id="c-harm" class="analytics"></canvas>
			</div>
			<div class="canvas-card">
				<div class="canvas-title"><h6>${__("Cents Timeline")}</h6><div class="small" id="info-cents">—</div></div>
				<canvas id="c-cents" class="analytics"></canvas>
			</div>
			<div class="canvas-card">
				<div class="canvas-title"><h6>${__("Autocorrelation (Cents)")}</h6><div class="small" id="info-ac">—</div></div>
				<canvas id="c-ac" class="analytics"></canvas>
			</div>
			<div class="canvas-card">
				<div class="canvas-title"><h6>${__("Waveform (Level)")}</h6><div class="small" id="info-wave">—</div></div>
				<canvas id="c-wave" class="analytics"></canvas>
			</div>
		</div>
	</div>
</div>
`;
	$(wrapper).html(ui);

	// --- Elements ---------------------------------------------------------------
	const byId = (id) => document.getElementById(id);
	const UI = {
		root: byId("display-root"),
		noteName: byId("note-name"),
		noteMeta: byId("note-meta"),
		a4Label: byId("a4-label"),
		modeLabel: byId("mode-label"),
		needle: byId("needle"),
		strobe: byId("strobe-canvas"),
		levelFill: byId("level-fill"),
		status: byId("status-line"),
		deviceInfo: byId("device-info"),
		errorBox: byId("error-box"),
		btnToggle: byId("btn-toggle"),
		btnReset: byId("btn-reset"),
		deviceSelect: byId("device-select"),
		instrumentSelect: byId("instrument-select"),
		displayMode: byId("display-mode"),
		viewMode: byId("view-mode"),
		a4Range: byId("a4-range"),
		a4Input: byId("a4-input"),
		gateSelect: byId("gate-select"),
		smoothingSelect: byId("smoothing-select"),
		fftSelect: byId("fft-select"),
		dynRange: byId("dyn-range"),
		needleWrap: byId("needle-wrap"),
		// analytics canvases
		cWave: byId("c-wave"),
		cSpectrum: byId("c-spectrum"),
		cGram: byId("c-gram"),
		cHarm: byId("c-harm"),
		cCents: byId("c-cents"),
		cAC: byId("c-ac"),
		infoSpectrum: byId("info-spectrum"),
		infoGram: byId("info-gram"),
		infoHarm: byId("info-harm"),
		infoCents: byId("info-cents"),
		infoAC: byId("info-ac"),
		infoWave: byId("info-wave"),
		m: {
			mean: byId("m-mean"),
			std: byId("m-std"),
			drift: byId("m-drift"),
			vibRate: byId("m-vib-rate"),
			vibDepth: byId("m-vib-depth"),
			oddEven: byId("m-odd-even"),
			attack: byId("m-attack"),
			jitter: byId("m-jitter"),
			shimmer: byId("m-shimmer"),
			hiss: byId("m-hiss"),
		}
	};

	// --- Constants --------------------------------------------------------------
	const NOTE_STR = ["C","C♯","D","D♯","E","F","F♯","G","G♯","A","A♯","B"];
	const TRANSPOSE_SEMITONES = { concert:0, bb:+2, a:+3, eb:-3, bb_bass:+14 };
	const SETTINGS_KEY = "desk_tuner_settings_v3";
	const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
	const mean = (arr) => arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : 0;
	const std = (arr) => {
		if (!arr.length) return 0;
		const m = mean(arr);
		return Math.sqrt(mean(arr.map(x => (x - m) * (x - m))));
	};
	const polyfit1 = (xs, ys) => {
		const n = Math.min(xs.length, ys.length);
		if (n < 2) return 0;
		let sx=0, sy=0, sxx=0, sxy=0;
		for (let i=0;i<n;i++){ sx+=xs[i]; sy+=ys[i]; sxx+=xs[i]*xs[i]; sxy+=xs[i]*ys[i]; }
		const denom = (n*sxx - sx*sx) || 1e-9;
		return (n*sxy - sx*sy) / denom;
	};

	// --- Settings ---------------------------------------------------------------
	const loadSettings = () => {
		try {
			const s = JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}");
			return {
				a4: clamp(Number(s.a4) || 440, 430, 446),
				instrument: s.instrument || "concert",
				displayMode: s.displayMode || "concert",
				viewMode: s.viewMode || "needle",
				gate: Number(s.gate) || 0.01,
				smoothing: Number(s.smoothing) || 0.4,
				deviceId: s.deviceId || "",
				fftSize: Number(s.fftSize) || 4096,
				dynRange: clamp(Number(s.dynRange) || 80, 40, 120)
			};
		} catch {
			return { a4:440,instrument:"concert",displayMode:"concert",viewMode:"needle",gate:0.01,smoothing:0.4,deviceId:"",fftSize:4096,dynRange:80 };
		}
	};
	const saveSettings = (s) => localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));

	// --- FFT (Radix-2, in-place) -----------------------------------------------
	function bitReverseIndices(n){
		const rev = new Uint32Array(n);
		const bits = Math.log2(n)|0;
		for (let i=0;i<n;i++){
			let x=i, y=0;
			for (let b=0;b<bits;b++){ y=(y<<1)|(x&1); x>>=1; }
			rev[i]=y>>>0;
		}
		return rev;
	}
	function fftInPlace(re, im){
		const n = re.length;
		const rev = fftInPlace._revCache.get(n) || bitReverseIndices(n);
		if (!fftInPlace._revCache.has(n)) fftInPlace._revCache.set(n, rev);
		for (let i=0;i<n;i++){
			const j = rev[i];
			if (j>i){ const tr=re[i]; re[i]=re[j]; re[j]=tr; const ti=im[i]; im[i]=im[j]; im[j]=ti; }
		}
		for (let len=2; len<=n; len<<=1){
			const half = len>>1;
			const ang = -2*Math.PI/len;
			for (let i=0;i<n;i+=len){
				for (let j=0;j<half;j++){
					const k=i+j, m=k+half;
					const wr = Math.cos(ang*j), wi = Math.sin(ang*j);
					const xr = wr*re[m] - wi*im[m];
					const xi = wr*im[m] + wi*re[m];
					const ur = re[k], ui = im[k];
					re[m] = ur - xr; im[m] = ui - xi;
					re[k] = ur + xr; im[k] = ui + xi;
				}
			}
		}
	}
	fftInPlace._revCache = new Map();

	function hannWindow(N){
		const w = new Float32Array(N);
		const f = 2*Math.PI/(N-1);
		for (let n=0;n<N;n++){ w[n] = 0.5*(1 - Math.cos(f*n)); }
		return w;
	}

	// --- DSP Helpers ------------------------------------------------------------
	function dbAmp(x){ return 20 * Math.log10(x + 1e-12); }
	function ampFromFFT(re, im, N, i){
		// single-sided amplitude spectrum scaling
		const mag = Math.hypot(re[i], im[i]);
		const scale = (i===0 || i===N/2) ? 1/N : 2/N;
		return mag * scale;
	}
	function interp1(x, x0, dx, arr){
		// arr indexed by i: value at x = x0 + i*dx, linear interpolation
		const t = (x - x0) / dx;
		const i = Math.floor(t);
		const frac = t - i;
		if (i < 0) return arr[0];
		if (i >= arr.length-1) return arr[arr.length-1];
		return arr[i]*(1-frac) + arr[i+1]*frac;
	}
	function buildLogAxis(fmin, fmax, bins){
		const out = new Float32Array(bins);
		const logMin = Math.log10(fmin), logMax = Math.log10(fmax);
		for (let i=0;i<bins;i++){
			const t = i/(bins-1);
			out[i] = Math.pow(10, logMin + t*(logMax - logMin));
		}
		return out;
	}

	// --- Tuner Core -------------------------------------------------------------
	const Tuner = {
		ac:null, analyser:null, stream:null, source:null, data:null, freqData:null, rAF:0,
		settings: loadSettings(),
		running:false, initialised:false, lastFreq:null, emaFreq:null, emaAlpha:0.4,
		strobeCtx:null, strobePhase:0, lastFrameTs:0,
		deviceList:[],
		fftBins:0,

		// spectra
		hann:null,
		spec:{
			linAmp:null, // Float32 N/2+1 amplitudes
			db:null,     // Float32 N/2+1 dB
			logDb:null,  // Float32 M
			logFreqs:null,
			binHz:0,
			M: 256,      // log bins for display
			fmin: 20
		},

		// histories (ring buffers)
		hist: {
			time: [],
			freq: [],
			cents: [],
			rms: [],
			harmonics: [],
			hfRms: [],
		},
		maxHist: 1200,

		// canvases
		ctx: {},

		async init(){
			if (this.initialised) return;

			// seed UI with settings
			UI.a4Input.value = String(this.settings.a4);
			UI.a4Range.value = String(this.settings.a4);
			UI.instrumentSelect.value = this.settings.instrument;
			UI.displayMode.value = this.settings.displayMode;
			UI.viewMode.value = this.settings.viewMode;
			UI.gateSelect.value = String(this.settings.gate);
			UI.smoothingSelect.value = String(this.settings.smoothing);
			UI.fftSelect.value = String(this.settings.fftSize);
			UI.dynRange.value = String(this.settings.dynRange);
			UI.a4Label.textContent = String(this.settings.a4);
			UI.modeLabel.textContent = this.settings.displayMode === "concert" ? __("Concert") : __("Written");

			this.ac = new (window.AudioContext || window.webkitAudioContext)();
			this.strobeCtx = UI.strobe.getContext("2d", { alpha:false });

			// analytics canvas contexts
			this.ctx.wave = UI.cWave.getContext("2d");
			this.ctx.spectrum = UI.cSpectrum.getContext("2d");
			this.ctx.gram = UI.cGram.getContext("2d");
			this.ctx.harm = UI.cHarm.getContext("2d");
			this.ctx.cents = UI.cCents.getContext("2d");
			this.ctx.ac = UI.cAC.getContext("2d");

			this.initialised = true;
			this.resizeAllCanvases();
			window.addEventListener("resize", () => this.resizeAllCanvases());
		},

		async start(){
			try{
				if (!this.initialised) await this.init();
				if (this.ac.state !== "running") await this.ac.resume();

				const constraints = {
					audio:{
						deviceId: this.settings.deviceId ? { exact:this.settings.deviceId } : undefined,
						channelCount:1, echoCancellation:false, noiseSuppression:false, autoGainControl:false
					}, video:false
				};

				this.stream = await navigator.mediaDevices.getUserMedia(constraints);
				this.source = this.ac.createMediaStreamSource(this.stream);
				this.analyser = this.ac.createAnalyser();
				this.analyser.fftSize = this.settings.fftSize || 4096;
				this.analyser.smoothingTimeConstant = 0;
				this.data = new Float32Array(this.analyser.fftSize);
				this.freqData = new Float32Array(this.analyser.frequencyBinCount);
				this.fftBins = this.analyser.frequencyBinCount;
				this.source.connect(this.analyser);

				// Prepare spectrum buffers
				this.onFftSizeChanged();

				await this.refreshDevices();

				this.running = true;
				UI.btnToggle.classList.remove("btn-primary");
				UI.btnToggle.classList.add("btn-danger");
				UI.btnToggle.innerHTML = `<i class="fa fa-stop" style="margin-right:6px;"></i>${__("Stop Tuner")}`;
				UI.errorBox.style.display = "none";

				this.resetHist();
				this.loop();
			}catch(err){
				this.stop();
				this.showError(err);
			}
		},

		stop(){
			this.running = false;
			cancelAnimationFrame(this.rAF);
			this.rAF = 0;
			if (this.stream){ for (const t of this.stream.getTracks()) t.stop(); this.stream=null; }
			if (this.ac && this.ac.state !== "closed"){ this.ac.suspend().catch(()=>{}); }

			UI.btnToggle.classList.add("btn-primary");
			UI.btnToggle.classList.remove("btn-danger");
			UI.btnToggle.innerHTML = `<i class="fa fa-microphone" style="margin-right:6px;"></i>${__("Start Tuner")}`;
			this.resetDisplay();
		},

		onFftSizeChanged(){
			const N = this.analyser?.fftSize || this.settings.fftSize || 4096;
			this.hann = hannWindow(N);
			this.spec.linAmp = new Float32Array(N/2 + 1);
			this.spec.db = new Float32Array(N/2 + 1);
			this.spec.binHz = (this.ac?.sampleRate || 48000) / N;
			const nyq = (this.ac?.sampleRate || 48000) / 2;
			this.spec.logFreqs = buildLogAxis(this.spec.fmin, nyq, this.spec.M);
			this.spec.logDb = new Float32Array(this.spec.M);
		},

		async refreshDevices(){
			const devices = await navigator.mediaDevices.enumerateDevices();
			this.deviceList = devices.filter((d)=>d.kind==="audioinput");
			const currentId = this.settings.deviceId;
			UI.deviceSelect.innerHTML = "";
			for (const d of this.deviceList){
				const opt = document.createElement("option");
				opt.value = d.deviceId;
				opt.textContent = d.label || __("Microphone");
				if (d.deviceId === currentId) opt.selected = true;
				UI.deviceSelect.appendChild(opt);
			}
			const input = this.deviceList.find((d)=>d.deviceId===currentId) || this.deviceList[0];
			if (input){ UI.deviceInfo.textContent = `${__("Using")}: ${input.label || __("Microphone")}`; }
		},

		async switchDevice(deviceId){
			this.settings.deviceId = deviceId;
			saveSettings(this.settings);
			if (this.running){ this.stop(); await this.start(); }
		},

		loop(ts){
			if (!this.running) return;

			// pull time/frequency data from AnalyserNode (for level & fallback)
			this.analyser.getFloatTimeDomainData(this.data);
			this.analyser.getFloatFrequencyData(this.freqData);

			// RMS (time-domain)
			let sum=0; const N = this.data.length;
			for (let i=0;i<N;i++) sum+=this.data[i]*this.data[i];
			const rms = Math.sqrt(sum/N);
			const gate = Number(this.settings.gate || 0.01);
			UI.levelFill.style.width = `${clamp((rms/0.3)*100,0,100)}%`;

			// Window + FFT + log spectrum (independent of AnalyserNode FFT)
			this.computeSpectrum(this.data);

			const now = performance.now() / 1000; // seconds
			let freq = 0, conf = 0, cents = NaN;

			if (rms < gate){
				this.renderNoSignal();
			}else{
				const res = this.yinPitchOptimized(this.data, this.ac.sampleRate, {threshold:0.1,minF:60,maxF:1800});
				if (res && res.freq>0){
					this.emaAlpha = Number(this.settings.smoothing || 0.4);
					if (!this.emaFreq) this.emaFreq = res.freq;
					this.emaFreq = this.emaAlpha*res.freq + (1-this.emaAlpha)*this.emaFreq;
					freq = this.emaFreq; conf = res.probability;
					cents = this.centsFromFreq(freq);
					this.renderPitch(freq, conf, ts);
				}else{
					this.renderUnstable();
				}
			}

			// keep history
			this.pushHist(now, freq, cents, rms);

			// analytics rendering (Hann+FFT driven for spectrum/gram/harm)
			this.drawWaveform(this.data);
			this.drawSpectrum();        // uses this.spec.logDb
			this.drawSpectrogram();     // uses this.spec.logDb
			this.drawHarmonics(freq);   // uses this.spec.db
			this.drawCentsTimeline();
			this.drawAutocorr();

			// compute & show metrics
			this.updateMetrics();

			this.rAF = requestAnimationFrame((t)=>this.loop(t));
		},

		// --------------------- Spectrum Pipeline ---------------------------------

		computeSpectrum(timeBuf){
			const N = timeBuf.length;
			if (!this.hann || this.hann.length !== N) this.hann = hannWindow(N);
			const re = new Float32Array(N);
			const im = new Float32Array(N);
			// Apply Hann
			for (let i=0;i<N;i++) re[i] = timeBuf[i] * this.hann[i];
			fftInPlace(re, im);

			// Single-sided amplitudes & dB
			const n2 = N/2;
			for (let i=0;i<=n2;i++){
				const amp = ampFromFFT(re, im, N, i);
				this.spec.linAmp[i] = amp;
				this.spec.db[i] = dbAmp(amp);
			}

			// Log-frequency resampling
			const binHz = this.spec.binHz;
			const f0 = 0; // bin 0 is DC
			const arr = this.spec.db;
			const M = this.spec.M;
			for (let j=0;j<M;j++){
				const f = this.spec.logFreqs[j];
				const val = (f < binHz) ? arr[1] : interp1(f, f0, binHz, arr);
				this.spec.logDb[j] = val;
			}
		},

		// --------------------- Rendering & Analytics -----------------------------

		resizeCanvas(c){
			const dpr = Math.max(1, window.devicePixelRatio || 1);
			const w = c.clientWidth * dpr;
			const h = c.clientHeight * dpr;
			if (c.width !== w || c.height !== h){ c.width = w; c.height = h; }
			return { w, h, dpr };
		},
		resizeAllCanvases(){
			[this.ctx.wave, this.ctx.spectrum, this.ctx.gram, this.ctx.harm, this.ctx.cents, this.ctx.ac].forEach((ctx)=>{
				if (!ctx) return;
				const c = ctx.canvas; const d = this.resizeCanvas(c);
				ctx.clearRect(0,0,d.w,d.h);
			});
		},

		drawWaveform(buf){
			const ctx = this.ctx.wave; if (!ctx) return;
			const { w, h } = this.resizeCanvas(ctx.canvas);
			ctx.clearRect(0,0,w,h);
			ctx.strokeStyle = "#4b88ff"; ctx.lineWidth = 2; ctx.beginPath();
			for (let i=0;i<buf.length;i++){
				const x = (i / (buf.length-1)) * w;
				const y = h*0.5 - buf[i] * (h*0.45);
				if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
			}
			ctx.stroke();
			UI.infoWave.textContent = `${__("Samples")}: ${buf.length} · ${__("Fs")}: ${this.ac?.sampleRate || 0} Hz`;
		},

		drawSpectrum(){
			const ctx = this.ctx.spectrum; if (!ctx) return;
			const { w, h } = this.resizeCanvas(ctx.canvas);
			ctx.clearRect(0,0,w,h);

			const dyn = Number(this.settings.dynRange || 80);
			const minDb = -dyn, maxDb = 0;

			// axes mapping: x = log-freq bins evenly spaced; y = dB
			ctx.strokeStyle = "#00b894"; ctx.lineWidth = 2; ctx.beginPath();
			const M = this.spec.M;
			for (let i=0;i<M;i++){
				const x = (i/(M-1)) * w;
				const v = clamp((this.spec.logDb[i] - minDb) / (maxDb - minDb), 0, 1);
				const y = h - v * h;
				if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
			}
			ctx.stroke();

			const nyq = (this.ac?.sampleRate || 48000)/2;
			UI.infoSpectrum.textContent = `${__("Log bins")}: ${M} · ${__("FFT")}: ${this.analyser?.fftSize || 0} · ${__("Nyquist")}: ${nyq.toFixed(0)} Hz`;
		},

		drawSpectrogram(){
			const ctx = this.ctx.gram; if (!ctx) return;
			const c = ctx.canvas;
			const { w, h } = this.resizeCanvas(c);

			// shift left by 1px
			const img = ctx.getImageData(1, 0, w-1, h);
			ctx.putImageData(img, 0, 0);

			const dyn = Number(this.settings.dynRange || 80);
			const minDb = -dyn, maxDb = 0;
			// paint rightmost column using log-frequency mapping
			const column = ctx.createImageData(1, h);

			for (let y=0; y<h; y++){
				// map y (top=high freq) -> log bin index
				const t = 1 - (y/(h-1));
				const j = clamp(Math.round(t*(this.spec.M-1)), 0, this.spec.M-1);
				const val = clamp((this.spec.logDb[j] - minDb) / (maxDb - minDb), 0, 1);

				// simple 'viridis-ish'
				const r = Math.floor(255 * Math.min(1, Math.max(0, -1.5*val*val + 2.5*val - 0.2)));
				const g = Math.floor(255 * Math.min(1, Math.max(0, -1.5*val*val + 2.8*val - 0.1)));
				const b = Math.floor(255 * Math.min(1, Math.max(0,  2.0*val*val      )));
				const idx = y * 4;
				column.data[idx] = r;
				column.data[idx+1] = g;
				column.data[idx+2] = b;
				column.data[idx+3] = 255;
			}
			ctx.putImageData(column, w-1, 0);
			UI.infoGram.textContent = `${__("Dyn")}: ${dyn} dB · ${__("Axis")}: ${__("Log Freq")}`;
		},

		drawHarmonics(f0){
			const ctx = this.ctx.harm; if (!ctx) return;
			const { w, h } = this.resizeCanvas(ctx.canvas);
			ctx.clearRect(0,0,w,h);
			if (!(f0 > 0)){ UI.infoHarm.textContent = "—"; return; }

			const N = (this.analyser?.fftSize || 4096);
			const binHz = this.spec.binHz || ((this.ac.sampleRate||48000)/N);
			const db = this.spec.db || [];
			const amps = [];
			const searchWin = 2; // +/- bins

			function pickPeakDbNear(freq){
				const center = freq / binHz;
				let best = -1e9;
				const lo = Math.max(0, Math.floor(center - searchWin));
				const hi = Math.min(db.length-1, Math.ceil(center + searchWin));
				for (let i=lo;i<=hi;i++) if (db[i] > best) best = db[i];
				return best;
			}

			for (let k=1; k<=10; k++){
				const f = k * f0;
				if (f > (this.ac.sampleRate/2)) { amps.push(-120); continue; }
				const val = pickPeakDbNear(f);
				amps.push(val);
			}

			// draw bars
			const pad = 8; const cols = 10; const bw = (w - pad*2) / cols;
			for (let i=0;i<cols;i++){
				const dbVal = amps[i] || -120;
				const dyn = Number(this.settings.dynRange || 80);
				const v = clamp((dbVal - (-dyn)) / (0 - (-dyn)), 0, 1);
				const bh = v * (h - pad*2);
				const x = pad + i*bw + 2; const y = h - pad - bh;
				ctx.fillStyle = i%2===0 ? "#6c5ce7" : "#0984e3";
				ctx.fillRect(x, y, Math.max(2, bw-4), Math.max(1, bh));
				ctx.fillStyle = "#666"; ctx.font = "10px sans-serif";
				ctx.textAlign = "center"; ctx.fillText(`H${i+1}`, x + (bw-4)/2, h-2);
			}

			// odd/even ratio & slope
			const lin = (dB) => Math.pow(10, dB/20);
			const odd = [0,2,4,6,8].map(i => lin((amps[i]||-120))).filter(Boolean);
			const even = [1,3,5,7,9].map(i => lin((amps[i]||-120))).filter(Boolean);
			const oddEvenDb = 10 * Math.log10(((mean(odd)||1e-12) / (mean(even)||1e-12)) + 1e-12);

			const ks = [...Array(10).keys()].map(i=>i+1);
			const slope = polyfit1(ks.map(k => Math.log2(Math.max(1,k))), amps.map(a => a||-120));

			UI.infoHarm.textContent = `${__("Odd/Even")}: ${oddEvenDb.toFixed(2)} dB · ${__("Slope")}: ${slope.toFixed(2)} dB/oct`;
			UI.m.oddEven.textContent = oddEvenDb.toFixed(2);

			// history
			this.hist.harmonics.push(amps.slice(0,10));
			this.trimHist();
		},

		drawCentsTimeline(){
			const ctx = this.ctx.cents; if (!ctx) return;
			const { w, h } = this.resizeCanvas(ctx.canvas);
			ctx.clearRect(0,0,w,h);
			const cents = this.hist.cents.slice(-400).filter(v => Number.isFinite(v));
			if (!cents.length){ UI.infoCents.textContent = "—"; return; }

			const mid = 0;
			const minV = Math.min(mid, ...cents);
			const maxV = Math.max(mid, ...cents);
			const pad = 6;

			// zero line
			const y0 = pad + (1 - (0 - minV) / ((maxV-minV)||1e-9)) * (h - pad*2);
			ctx.strokeStyle = "#ddd"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(0,y0); ctx.lineTo(w,y0); ctx.stroke();

			// path
			ctx.strokeStyle = "#4b88ff"; ctx.lineWidth = 2; ctx.beginPath();
			for (let i=0;i<cents.length;i++){
				const x = (i / (cents.length-1)) * w;
				const y = pad + (1 - (cents[i] - minV) / ((maxV-minV)||1e-9)) * (h - pad*2);
				if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
			}
			ctx.stroke();

			// mean & std
			const m = mean(cents);
			const s = std(cents);
			const drift = this.estimateDrift(this.hist.time, this.hist.cents);

			UI.m.mean.textContent = isFinite(m) ? m.toFixed(2) : "—";
			UI.m.std.textContent = isFinite(s) ? s.toFixed(2) : "—";
			UI.m.drift.textContent = isFinite(drift) ? drift.toFixed(2) : "—";
			UI.infoCents.textContent = `${__("n")}=${cents.length}`;
		},

		drawAutocorr(){
			const ctx = this.ctx.ac; if (!ctx) return;
			const { w, h } = this.resizeCanvas(ctx.canvas);
			ctx.clearRect(0,0,w,h);

			const N = Math.min(this.hist.cents.length, 800);
			if (N < 60){ UI.infoAC.textContent = "—"; return; }
			const cents = this.hist.cents.slice(-N).map(v => (Number.isFinite(v)? v : 0));

			// autocorrelation
			const ac = (function autocorr(x, maxLag){
				const n = x.length;
				const m = mean(x);
				const v = Math.sqrt(mean(x.map(y => (y - m)*(y - m))) + 1e-12);
				const out = new Float32Array(maxLag + 1);
				for (let lag=0; lag<=maxLag; lag++){
					let s=0, c=0;
					for (let i=0; i<n-lag; i++){ s += (x[i]-m)*(x[i+lag]-m); c++; }
					out[lag] = c ? (s / (c * v * v + 1e-12)) : 0;
				}
				return out;
			})(cents, Math.min(200, Math.floor(N*0.8)));

			ctx.strokeStyle = "#e17055"; ctx.lineWidth = 2; ctx.beginPath();
			for (let i=0;i<ac.length;i++){
				const x = (i / (ac.length-1)) * w;
				const y = h - (ac[i] * 0.5 + 0.5) * h;
				if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
			}
			ctx.stroke();

			// vibrato estimate: peak in 4–8 Hz band
			const times = this.hist.time.slice(-N);
			const dt = (times[times.length-1] - times[0]) / (N - 1 + 1e-9);
			const fs = 1 / Math.max(0.02, dt);

			const band = [4, 8]; // Hz
			const idxLo = Math.floor(band[0] / fs * ac.length);
			const idxHi = Math.min(ac.length-1, Math.floor(band[1] / fs * ac.length));
			let peakIdx = idxLo, peakVal = -1e9;
			for (let i=idxLo;i<=idxHi;i++){ if (ac[i] > peakVal){ peakVal = ac[i]; peakIdx = i; } }
			const vibRate = (peakIdx / ac.length) * fs;
			const depth = 2 * std(cents); // rough proxy

			UI.m.vibRate.textContent = isFinite(vibRate) ? vibRate.toFixed(2) : "—";
			UI.m.vibDepth.textContent = isFinite(depth) ? depth.toFixed(1) : "—";
			UI.infoAC.textContent = `${__("fs")}: ${fs.toFixed(1)} Hz`;
		},

		updateMetrics(){
			const N = this.hist.time.length;
			if (N < 10) return;

			// attack: 90% of max RMS
			const rms = this.hist.rms.slice(-300);
			const times = this.hist.time.slice(-300);
			if (rms.length > 20){
				const maxR = Math.max(...rms);
				const thr = 0.9 * maxR;
				let idx = rms.findIndex(v => v >= thr);
				if (idx < 0) idx = 0;
				const attackMs = (times[idx] - times[0]) * 1000;
				UI.m.attack.textContent = isFinite(attackMs) ? attackMs.toFixed(0) : "—";
			}

			// jitter (%)
			const f = this.hist.freq.slice(-200).filter(x => x > 0);
			if (f.length > 8){
				const periods = f.map(x => 1/x);
				let diffs = 0, count=0;
				for (let i=1;i<periods.length;i++){ diffs += Math.abs(periods[i] - periods[i-1]); count++; }
				const jitter = (diffs / (count * (mean(periods)+1e-9))) * 100;
				UI.m.jitter.textContent = isFinite(jitter) ? jitter.toFixed(2) : "—";
			}

			// shimmer (%)
			const env = this.hist.rms.slice(-200);
			if (env.length > 8){
				let diffs = 0, count=0;
				for (let i=1;i<env.length;i++){ diffs += Math.abs(env[i] - env[i-1]); count++; }
				const shimmer = (diffs / (count * (mean(env)+1e-9))) * 100;
				UI.m.shimmer.textContent = isFinite(shimmer) ? shimmer.toFixed(2) : "—";
			}

			// hiss index using our spectrum (HF energy ratio)
			const linAmp = this.spec.linAmp;
			if (linAmp && linAmp.length){
				const nyq = (this.ac?.sampleRate || 48000)/2;
				const startBin = Math.max(1, Math.floor(4000 / this.spec.binHz));
				let hf=0, lf=0, hc=0, lc=0;
				for (let i=1;i<linAmp.length;i++){
					if (i>=startBin){ hf += linAmp[i]; hc++; }
					else { lf += linAmp[i]; lc++; }
				}
				const hidx = clamp((hf/hc) / ((hf/hc)+(lf/lc)+1e-9), 0, 1);
				UI.m.hiss.textContent = isFinite(hidx) ? hidx.toFixed(2) : "—";
			}
		},

		// ------------------------ Core tuner visuals -----------------------------

		renderPitch(freq, confidence=0, ts=0){
			const a4 = Number(this.settings.a4 || 440);
			const midiFloat = 69 + 12*Math.log2(freq/a4);
			const midiNearest = Math.round(midiFloat);
			const targetFreqConcert = a4 * Math.pow(2,(midiNearest-69)/12);
			const cents = 1200 * Math.log2(freq/targetFreqConcert);

			const transpose = TRANSPOSE_SEMITONES[this.settings.instrument] || 0;
			const displayMode = this.settings.displayMode || "concert";
			const displayMidi = displayMode === "written" ? midiNearest + transpose : midiNearest;

			const { note, octave } = this.midiToNote(displayMidi);
			UI.noteName.textContent = `${note}${octave}`;
			UI.noteMeta.innerHTML = `${freq.toFixed(2)} Hz · ${cents>=0?"+":""}${isFinite(cents)?cents.toFixed(1):"—"} ${__("cents")} · ${__("Conf")}: ${(confidence*100).toFixed(0)}%`;
			UI.a4Label.textContent = String(a4);
			UI.modeLabel.textContent = displayMode==="concert" ? __("Concert") : __("Written");

			const rotation = clamp((cents/50)*45, -45, 45);
			UI.needle.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
			if (Math.abs(cents) < 5) UI.root.classList.add("in-tune"); else UI.root.classList.remove("in-tune");

			const view = this.settings.viewMode || "needle";
			const wantStrobe = view==="strobe" || view==="both";
			const wantNeedle = view==="needle" || view==="both";
			UI.needleWrap.style.display = wantNeedle ? "block" : "none";
			UI.strobe.style.display = wantStrobe ? "block" : "none";
			if (wantStrobe) this.drawStrobe(cents, ts);

			UI.status.textContent = `${__("Sample Rate")}: ${this.ac.sampleRate} Hz · ${__("FFT")}: ${this.analyser.fftSize}`;
		},

		renderNoSignal(){ UI.status.textContent = __("Listening… (play a sustained note)"); UI.root.classList.remove("in-tune"); this.setNeedleNeutral(); },
		renderUnstable(){ UI.status.textContent = __("Analyzing… (unstable pitch)"); UI.root.classList.remove("in-tune"); this.setNeedleNeutral(); },
		setNeedleNeutral(){ UI.needle.style.transform = "translateX(-50%) rotate(0deg)"; },
		resetDisplay(){
			UI.noteName.textContent = "--";
			UI.noteMeta.textContent = `A4 = ${this.settings.a4} Hz · ${this.settings.displayMode==="concert"?__("Concert"):__("Written")}`;
			UI.status.textContent = "—";
			UI.levelFill.style.width = "0%";
			UI.root.classList.remove("in-tune");
			this.setNeedleNeutral();
			this.clearStrobe();
			this.emaFreq = null;
			this.lastFreq = null;
			this.resetHist(true);
			this.resizeAllCanvases();
		},

		// --- Strobe --------------------------------------------------------------
		drawStrobe(cents, ts){
			const ctx = this.strobeCtx; if (!ctx) return;
			const dpr = Math.max(1, window.devicePixelRatio || 1);
			const w = UI.strobe.width = Math.max(2, Math.floor(UI.strobe.clientWidth * dpr));
			const h = UI.strobe.height = Math.max(2, Math.floor(UI.strobe.clientHeight * dpr));

			const now = ts || performance.now();
			const dt = this.lastFrameTs ? (now - this.lastFrameTs)/1000 : 0;
			this.lastFrameTs = now;

			const speed = 4 * dpr;
			this.strobePhase += (cents * speed) * dt;

			const stripeW = Math.max(12*dpr, Math.min(40*dpr, w/20));
			const offset = ((this.strobePhase % stripeW) + stripeW) % stripeW;

			ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--bg-dark") || "#111";
			ctx.fillRect(0,0,w,h);

			for (let x = -stripeW + offset; x < w + stripeW; x += stripeW){
				const grad = ctx.createLinearGradient(x,0,x+stripeW,0);
				grad.addColorStop(0, "rgba(255,255,255,0.06)");
				grad.addColorStop(0.5,"rgba(255,255,255,0.25)");
				grad.addColorStop(1, "rgba(255,255,255,0.06)");
				ctx.fillStyle = grad;
				ctx.fillRect(x,0,stripeW,h);
			}
			ctx.fillStyle = "rgba(0,0,0,0.5)";
			ctx.fillRect(w/2 - 2*dpr, 0, 4*dpr, h);
		},
		clearStrobe(){
			if (!this.strobeCtx) return;
			const dpr = Math.max(1, window.devicePixelRatio || 1);
			const w = UI.strobe.width = Math.max(2, Math.floor(UI.strobe.clientWidth * dpr));
			const h = UI.strobe.height = Math.max(2, Math.floor(UI.strobe.clientHeight * dpr));
			this.strobeCtx.clearRect(0,0,w,h);
		},

		// ---------------------------- Refactored YIN ------------------------------
		/**
		 * Optimized YIN with unrolled inner loop and clean CMND computation.
		 * threshold: typical 0.1
		 */
		yinPitchOptimized(buf, sampleRate, opts){
			const threshold = opts?.threshold ?? 0.1;
			const minF = opts?.minF ?? 60;
			const maxF = opts?.maxF ?? 1800;

			const N = buf.length|0;
			const maxTau = Math.floor(sampleRate / minF);
			const minTau = Math.max(2, Math.floor(sampleRate / maxF));
			if (N < maxTau + 2) return null;

			// Difference function d[tau]
			const d = new Float32Array(maxTau + 1);
			const limit = N; // compute up to N - tau
			for (let tau=minTau; tau<=maxTau; tau++){
				let sum=0;
				const L = limit - tau;
				let i=0;
				// loop unrolling by 4
				for (; i+3<L; i+=4){
					const d0 = buf[i]   - buf[i+tau];
					const d1 = buf[i+1] - buf[i+tau+1];
					const d2 = buf[i+2] - buf[i+tau+2];
					const d3 = buf[i+3] - buf[i+tau+3];
					sum += d0*d0 + d1*d1 + d2*d2 + d3*d3;
				}
				for (; i<L; i++){
					const di = buf[i] - buf[i+tau];
					sum += di*di;
				}
				d[tau] = sum;
			}

			// Cumulative mean normalized difference CMND
			const cmnd = new Float32Array(maxTau + 1);
			cmnd[0]=1;
			let runningSum=0;
			for (let tau=1; tau<=maxTau; tau++){
				runningSum += d[tau];
				cmnd[tau] = d[tau] * tau / (runningSum || 1);
			}

			// Absolute threshold
			let tauEstimate = -1;
			for (let tau=minTau; tau<=maxTau; tau++){
				if (cmnd[tau] < threshold){
					// find local minimum
					while (tau+1<=maxTau && cmnd[tau+1] < cmnd[tau]) tau++;
					tauEstimate = tau; break;
				}
			}
			// Fallback to global minimum in range
			if (tauEstimate < 0){
				let minVal=1e9, minIdx=-1;
				for (let tau=minTau; tau<=maxTau; tau++){
					if (cmnd[tau] < minVal){ minVal = cmnd[tau]; minIdx=tau; }
				}
				tauEstimate = minIdx;
				if (tauEstimate < 0) return null;
			}

			// Parabolic interpolation around tauEstimate
			const t = tauEstimate;
			const x0 = (t>1) ? cmnd[t-1] : cmnd[t];
			const x1 = cmnd[t];
			const x2 = (t+1<=maxTau) ? cmnd[t+1] : cmnd[t];
			const a = (x0 + x2 - 2*x1) / 2;
			const b = (x2 - x0) / 2;
			let betterTau = t;
			if (Math.abs(a) > 1e-12) betterTau = t - b / (2*a);

			const freq = sampleRate / betterTau;
			const prob = 1 - cmnd[tauEstimate];
			if (freq < minF || freq > maxF || !isFinite(freq)) return null;

			return { freq, probability: clamp(prob, 0, 1) };
		},

		midiToNote(midi){
			const n = Math.round(midi);
			const note = NOTE_STR[(n + 1200) % 12];
			const octave = Math.floor(n/12) - 1;
			return { note, octave };
		},

		centsFromFreq(freq){
			if (!(freq > 0)) return NaN;
			const a4 = Number(this.settings.a4 || 440);
			const midiFloat = 69 + 12*Math.log2(freq/a4);
			const midiNearest = Math.round(midiFloat);
			const targetFreqConcert = a4 * Math.pow(2,(midiNearest-69)/12);
			return 1200 * Math.log2(freq/targetFreqConcert);
		},

		// --------------------------- Histories -----------------------------------

		pushHist(t, f, cents, rms){
			// derive HF proxy from our spectrum (>4 kHz)
			let hf = 0;
			if (this.spec.linAmp && this.spec.linAmp.length){
				const startBin = Math.max(1, Math.floor(4000 / (this.spec.binHz || 1)));
				let s=0, c=0;
				for (let i=startBin;i<this.spec.linAmp.length;i++){ s += this.spec.linAmp[i]; c++; }
				hf = c ? (s/c) : 0;
			}

			this.hist.time.push(t);
			this.hist.freq.push(f || 0);
			this.hist.cents.push(Number.isFinite(cents)? cents : NaN);
			this.hist.rms.push(rms || 0);
			this.hist.hfRms.push(hf || 0);

			this.trimHist();
		},
		trimHist(){
			const L = this.maxHist;
			Object.keys(this.hist).forEach(k => {
				if (this.hist[k].length > L) this.hist[k] = this.hist[k].slice(-L);
			});
		},
		resetHist(clearAll){
			this.hist.time = []; this.hist.freq = []; this.hist.cents = [];
			this.hist.rms = []; this.hist.harmonics = []; this.hist.hfRms = [];
			if (clearAll){
				["m-mean","m-std","m-drift","m-vib-rate","m-vib-depth","m-odd-even","m-attack","m-jitter","m-shimmer","m-hiss"]
					.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = "—"; });
			}
		},

		estimateDrift(times, cents){
			const xs = []; const ys = [];
			for (let i=Math.max(0, times.length-200); i<times.length; i++){
				if (Number.isFinite(cents[i])){ xs.push(times[i]); ys.push(cents[i]); }
			}
			if (xs.length < 6) return NaN;
			const t0 = xs[0];
			const xz = xs.map(x => x - t0);
			return polyfit1(xz, ys);
		},

		// ---------------------------- Error & Cleanup ----------------------------

		showError(err){
			console.error("[Desk Tuner]", err);
			UI.errorBox.style.display = "block";
			UI.errorBox.textContent = (err && err.message) ? err.message : __("Microphone error. Check permissions and input device.");
		},

		async cleanup(){
			try{ this.stop(); if (this.ac && this.ac.state!=="closed") await this.ac.close(); }catch{}
		}
	};

	// --- Events ----------------------------------------------------------------
	UI.btnToggle.addEventListener("click", async () => { if (!Tuner.running) await Tuner.start(); else Tuner.stop(); });
	UI.btnReset.addEventListener("click", () => {
		Tuner.settings = { a4:440,instrument:"concert",displayMode:"concert",viewMode:"needle",gate:0.01,smoothing:0.4,deviceId:"",fftSize:4096,dynRange:80 };
		saveSettings(Tuner.settings);
		UI.a4Input.value="440"; UI.a4Range.value="440"; UI.a4Label.textContent="440";
		UI.instrumentSelect.value="concert"; UI.displayMode.value="concert"; UI.viewMode.value="needle";
		UI.gateSelect.value="0.01"; UI.smoothingSelect.value="0.4"; UI.fftSelect.value="4096"; UI.dynRange.value="80";
		UI.modeLabel.textContent = __("Concert");
		Tuner.resetDisplay();
		if (Tuner.analyser){ Tuner.analyser.fftSize = 4096; Tuner.data = new Float32Array(Tuner.analyser.fftSize); Tuner.freqData = new Float32Array(Tuner.analyser.frequencyBinCount); Tuner.onFftSizeChanged(); }
	});

	UI.a4Range.addEventListener("input",(e)=>{ const v = clamp(Number(e.target.value||440),430,446); UI.a4Input.value=String(v); UI.a4Label.textContent=String(v); Tuner.settings.a4=v; saveSettings(Tuner.settings); });
	UI.a4Input.addEventListener("change",(e)=>{ const v = clamp(Number(e.target.value||440),430,446); UI.a4Range.value=String(v); UI.a4Label.textContent=String(v); Tuner.settings.a4=v; saveSettings(Tuner.settings); });
	UI.instrumentSelect.addEventListener("change",(e)=>{ Tuner.settings.instrument=e.target.value; saveSettings(Tuner.settings); });
	UI.displayMode.addEventListener("change",(e)=>{ Tuner.settings.displayMode=e.target.value; UI.modeLabel.textContent = e.target.value==="concert"?__("Concert"):__("Written"); saveSettings(Tuner.settings); });
	UI.viewMode.addEventListener("change",(e)=>{ Tuner.settings.viewMode=e.target.value; saveSettings(Tuner.settings); if (e.target.value==="strobe"){ UI.needleWrap.style.display="none"; UI.strobe.style.display="block"; } else if (e.target.value==="needle"){ UI.needleWrap.style.display="block"; UI.strobe.style.display="none"; } else { UI.needleWrap.style.display="block"; UI.strobe.style.display="block"; } });
	UI.gateSelect.addEventListener("change",(e)=>{ Tuner.settings.gate=Number(e.target.value||0.01); saveSettings(Tuner.settings); });
	UI.smoothingSelect.addEventListener("change",(e)=>{ Tuner.settings.smoothing=Number(e.target.value||0.4); saveSettings(Tuner.settings); });
	UI.deviceSelect.addEventListener("change", async (e)=>{ await Tuner.switchDevice(e.target.value); });
	UI.fftSelect.addEventListener("change",(e)=>{
		Tuner.settings.fftSize = Number(e.target.value || 4096);
		saveSettings(Tuner.settings);
		if (Tuner.analyser){
			Tuner.analyser.fftSize = Tuner.settings.fftSize;
			Tuner.data = new Float32Array(Tuner.analyser.fftSize);
			Tuner.freqData = new Float32Array(Tuner.analyser.frequencyBinCount);
			Tuner.onFftSizeChanged();
		}
	});
	UI.dynRange.addEventListener("change",(e)=>{ Tuner.settings.dynRange = clamp(Number(e.target.value||80),40,120); saveSettings(Tuner.settings); });

	// Keep device list fresh
	if (navigator.mediaDevices?.addEventListener) {
		navigator.mediaDevices.addEventListener("devicechange", () => {
			if (Tuner.initialised) Tuner.refreshDevices().catch(()=>{});
		});
	}

	// Save battery on hide
	document.addEventListener("visibilitychange", async () => {
		try {
			if (!Tuner.ac) return;
			if (document.hidden) await Tuner.ac.suspend();
			else if (Tuner.running && Tuner.ac.state!=="running") await Tuner.ac.resume();
		} catch {}
	});

	// Unlock AudioContext on first gesture (iOS)
	const unlock = async () => {
		try { if (Tuner.ac && Tuner.ac.state!=="running") await Tuner.ac.resume(); } catch {}
		document.removeEventListener("touchend", unlock);
		document.removeEventListener("mousedown", unlock);
	};
	document.addEventListener("touchend", unlock, { once:true });
	document.addEventListener("mousedown", unlock, { once:true });

	// Cleanup when leaving
	page.wrapper.on("page-leave", function () { Tuner.cleanup(); });

	// Init (no mic yet)
	Tuner.init();
};
