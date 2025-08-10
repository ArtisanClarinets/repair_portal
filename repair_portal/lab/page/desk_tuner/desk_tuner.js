/** biome-ignore-all lint/correctness/noUnusedVariables */
/** biome-ignore-all lint/complexity/useArrowFunction */
frappe.pages["desk-tuner"].on_page_load = function (wrapper) {
	// jQuery alias must come BEFORE any use of $ to avoid TDZ issues
	const $ = window.jQuery;

	// -----------------------------------------------------------------------------
	// Desk Tuner (Frappe v15)
	// - Robust YIN pitch with smoothing & outlier handling
	// - Transposition (Concert/B♭/A/E♭/Bass B♭) + Concert/Written display
	// - A4 calibration (430–446) with persistence
	// - Mic device selection, level meter, needle + strobe
	// - Mobile-safe: resume gates, constraints to reduce AGC/NS/EC
	// -----------------------------------------------------------------------------

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Desk Tuner"),
		single_column: true
	});
	frappe.breadcrumbs.add("Lab", "Desk Tuner");

	// --- UI ----------------------------------------------------------------------
	const ui = `
	<style>
		.tuner-wrapper{max-width:720px;margin:24px auto;padding:24px;background-color:var(--fg-color);border-radius:var(--border-radius-xl);box-shadow:var(--shadow-lg)}
		.tuner-grid{display:grid;grid-template-columns:1fr;gap:18px}
		@media (min-width:900px){.tuner-grid{grid-template-columns:1fr 1fr}}
		.section{padding:16px;border:1px solid var(--border-color);border-radius:var(--border-radius-md)}
		.section h5{margin:0 0 12px 0}
		.tuner-display{text-align:center}
		.note-name{font-size:5rem;font-weight:700;line-height:1;color:var(--text-color);transition:color .2s ease;min-height:80px}
		.note-meta{color:var(--text-muted);min-height:24px;font-size:1rem}
		.in-tune .note-name{color:var(--green-500)}
		.meter-wrap{position:relative;height:60px}
		.meter-scale{position:absolute;left:0;right:0;bottom:0;height:2px;background:var(--border-color)}
		.meter-ticks{position:absolute;left:0;right:0;bottom:0;height:100%}
		.tick{position:absolute;bottom:0;width:2px;background:var(--border-color)}
		.tick.center{left:50%;height:100%;transform:translateX(-50%)}
		.tick.side{height:50%}
		.tick.l-25{left:25%}
		.tick.r-25{right:25%}
		.needle{position:absolute;bottom:-2px;left:50%;width:4px;height:100%;background:var(--red-500);border-radius:4px 4px 0 0;transform-origin:bottom center;transform:translateX(-50%) rotate(0deg);transition:transform .12s ease-out,background-color .2s ease}
		.in-tune .needle{background:var(--green-500)}
		#strobe-canvas{width:100%;height:120px;display:none;border-radius:8px;border:1px solid var(--border-color)}
		.level-bar{height:10px;border-radius:999px;background:var(--bg-color);border:1px solid var(--border-color);overflow:hidden}
		.level-fill{height:100%;width:0%;background:var(--blue-500);transition:width .1s linear}
		.controls-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
		@media (max-width:480px){.controls-row{grid-template-columns:1fr}}
		.form-inline{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
		.form-inline label{margin:0 6px 0 0;white-space:nowrap}
		.form-inline input[type="range"]{width:160px}
		.small{font-size:.875rem;color:var(--text-muted)}
		#error-box{display:none}
	</style>

	<div class="tuner-wrapper">
		<div class="tuner-grid">
			<div class="section">
				<h5>${__("Pitch Display")}</h5>
				<div class="tuner-display" id="display-root">
					<div id="note-name" class="note-name">--</div>
					<div class="note-meta" id="note-meta">A4 = <span id="a4-label">440</span> Hz · <span id="mode-label">Concert</span></div>
					<div class="meter-wrap" id="needle-wrap">
						<div class="meter-scale"></div>
						<div class="meter-ticks">
							<div class="tick center"></div>
							<div class="tick side l-25"></div>
							<div class="tick side r-25"></div>
						</div>
						<div class="needle" id="needle"></div>
					</div>
					<canvas id="strobe-canvas"></canvas>
					<div style="margin-top:12px;">
						<div class="level-bar"><div class="level-fill" id="level-fill"></div></div>
						<div class="small" id="status-line" style="margin-top:6px;">—</div>
					</div>
				</div>
			</div>

			<div class="section">
				<h5>${__("Controls")}</h5>

				<div class="form-inline" style="margin-bottom:8px;">
					<label for="device-select">${__("Microphone")}</label>
					<select id="device-select" class="form-control"></select>
				</div>

				<div class="controls-row" style="margin-bottom:8px;">
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
					<div class="form-inline">
						<label for="display-mode">${__("Display")}</label>
						<select id="display-mode" class="form-control">
							<option value="concert">${__("Concert")}</option>
							<option value="written">${__("Written (transposed)")}</option>
						</select>
					</div>
				</div>

				<div class="controls-row" style="margin-bottom:8px;">
					<div class="form-inline">
						<label for="a4-range">A4</label>
						<input id="a4-range" type="range" min="430" max="446" step="1" value="440">
						<input id="a4-input" type="number" class="form-control" style="width:90px" min="430" max="446" step="1" value="440">
					</div>
					<div class="form-inline">
						<label for="view-mode">${__("View")}</label>
						<select id="view-mode" class="form-control">
							<option value="needle">${__("Needle")}</option>
							<option value="strobe">${__("Strobe")}</option>
							<option value="both">${__("Both")}</option>
						</select>
					</div>
				</div>

				<div class="controls-row" style="margin-bottom:8px;">
					<div class="form-inline">
						<label for="gate-select">${__("Noise Gate")}</label>
						<select id="gate-select" class="form-control">
							<option value="0.005">Low</option>
							<option value="0.01" selected>Medium</option>
							<option value="0.02">High</option>
						</select>
					</div>
					<div class="form-inline">
						<label for="smoothing-select">${__("Smoothing")}</label>
						<select id="smoothing-select" class="form-control">
							<option value="0.2">Fast</option>
							<option value="0.4" selected>Medium</option>
							<option value="0.7">Slow</option>
						</select>
					</div>
				</div>

				<div class="controls-row">
					<button id="btn-toggle" class="btn btn-primary">
						<i class="fa fa-microphone" style="margin-right: 6px;"></i>${__("Start Tuner")}
					</button>
					<button id="btn-reset" class="btn btn-default">
						<i class="fa fa-refresh" style="margin-right: 6px;"></i>${__("Reset")}
					</button>
				</div>

				<div id="error-box" class="alert alert-danger" style="margin-top:12px;"></div>
				<div class="small" style="margin-top:8px;" id="device-info">—</div>
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
		needleWrap: byId("needle-wrap"),
	};

	const NOTE_STR = ["C","C♯","D","D♯","E","F","F♯","G","G♯","A","A♯","B"];
	const TRANSPOSE_SEMITONES = { concert:0, bb:+2, a:+3, eb:-3, bb_bass:+14 };

	const SETTINGS_KEY = "desk_tuner_settings_v1";
	const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

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
				deviceId: s.deviceId || ""
			};
		} catch {
			return { a4:440,instrument:"concert",displayMode:"concert",viewMode:"needle",gate:0.01,smoothing:0.4,deviceId:"" };
		}
	};
	const saveSettings = (s) => localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));

	// --- Tuner Core --------------------------------------------------------------
	const Tuner = {
		ac:null, analyser:null, stream:null, source:null, data:null, rAF:0,
		settings: loadSettings(),
		running:false, initialised:false, lastFreq:null, emaFreq:null, emaAlpha:0.4,
		strobeCtx:null, strobePhase:0, lastFrameTs:0,
		deviceList:[],

		async init(){
			if (this.initialised) return;
			UI.a4Input.value = String(this.settings.a4);
			UI.a4Range.value = String(this.settings.a4);
			UI.instrumentSelect.value = this.settings.instrument;
			UI.displayMode.value = this.settings.displayMode;
			UI.viewMode.value = this.settings.viewMode;
			UI.gateSelect.value = String(this.settings.gate);
			UI.smoothingSelect.value = String(this.settings.smoothing);
			UI.a4Label.textContent = String(this.settings.a4);
			UI.modeLabel.textContent = this.settings.displayMode === "concert" ? __("Concert") : __("Written");

			this.ac = new (window.AudioContext || window.webkitAudioContext)();
			this.strobeCtx = UI.strobe.getContext("2d", { alpha:false });
			this.initialised = true;
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
				this.analyser.fftSize = 4096;
				this.analyser.smoothingTimeConstant = 0;
				this.data = new Float32Array(this.analyser.fftSize);
				this.source.connect(this.analyser);

				await this.refreshDevices();

				this.running = true;
				UI.btnToggle.classList.remove("btn-primary");
				UI.btnToggle.classList.add("btn-danger");
				UI.btnToggle.innerHTML = `<i class="fa fa-stop" style="margin-right:6px;"></i>${__("Stop Tuner")}`;
				UI.errorBox.style.display = "none";

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
			this.analyser.getFloatTimeDomainData(this.data);

			let sum=0; for (let i=0;i<this.data.length;i++) sum+=this.data[i]*this.data[i];
			const rms = Math.sqrt(sum/this.data.length);
			const gate = Number(this.settings.gate || 0.01);
			UI.levelFill.style.width = `${clamp((rms/0.3)*100,0,100)}%`;

			if (rms < gate){
				this.renderNoSignal();
			}else{
				const res = this.yinPitch(this.data, this.ac.sampleRate, {threshold:0.1,minF:60,maxF:2000});
				if (res && res.freq>0){
					this.emaAlpha = Number(this.settings.smoothing || 0.4);
					if (!this.emaFreq) this.emaFreq = res.freq;
					this.emaFreq = this.emaAlpha*res.freq + (1-this.emaAlpha)*this.emaFreq;
					this.renderPitch(this.emaFreq, res.probability, ts);
				}else{
					this.renderUnstable();
				}
			}
			this.rAF = requestAnimationFrame((t)=>this.loop(t));
		},

		renderPitch(freq, confidence=0, ts=0){
			const a4 = Number(this.settings.a4 || 440);
			const midiFloat = 69 + 12*Math.log2(freq/a4);
			const midiNearest = Math.round(midiFloat);
			const targetFreqConcert = a4 * Math.pow(2,(midiNearest-69)/12);
			const cents = 1200 * Math.log2(freq/targetFreqConcert);

			const transpose = {concert:0, bb:+2, a:+3, eb:-3, bb_bass:+14}[this.settings.instrument] || 0;
			const displayMode = this.settings.displayMode || "concert";
			const displayMidi = displayMode === "written" ? midiNearest + transpose : midiNearest;

			const { note, octave } = this.midiToNote(displayMidi);
			UI.noteName.textContent = `${note}${octave}`;
			UI.noteMeta.innerHTML = `${freq.toFixed(2)} Hz · ${cents>=0?"+":""}${cents.toFixed(1)} cents · ${__("Conf")}: ${(confidence*100).toFixed(0)}%`;
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

			UI.status.textContent = `${__("Sample Rate")}: ${this.ac.sampleRate} Hz`;
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

		// --- YIN Pitch -----------------------------------------------------------
		yinPitch(buf, sampleRate, opts){
			const threshold = opts?.threshold ?? 0.1;
			const minF = opts?.minF ?? 60;
			const maxF = opts?.maxF ?? 2000;

			const maxTau = Math.floor(sampleRate / minF);
			const minTau = Math.floor(sampleRate / maxF);
			const frameSize = buf.length;
			if (frameSize < maxTau + 2) return null;

			const d = new Float32Array(maxTau + 1);
			for (let tau=1; tau<=maxTau; tau++){
				let sum=0;
				for (let i=0; i<frameSize - tau; i++){
					const delta = buf[i] - buf[i+tau];
					sum += delta*delta;
				}
				d[tau] = sum;
			}

			const cmnd = new Float32Array(maxTau + 1);
			cmnd[0]=1;
			let runningSum=0;
			for (let tau=1; tau<=maxTau; tau++){
				runningSum += d[tau];
				cmnd[tau] = d[tau] * tau / (runningSum || 1);
			}

			let tauEstimate = -1;
			for (let tau=minTau; tau<=maxTau; tau++){
				if (cmnd[tau] < threshold){
					while (tau+1<=maxTau && cmnd[tau+1] < cmnd[tau]) tau++;
					tauEstimate = tau; break;
				}
			}
			if (tauEstimate < 0){
				let minVal=1e9, minIdx=-1;
				for (let tau=minTau; tau<=maxTau; tau++){
					if (cmnd[tau] < minVal){ minVal = cmnd[tau]; minIdx=tau; }
				}
				tauEstimate = minIdx;
				if (tauEstimate < 0) return null;
			}

			const tau = tauEstimate;
			const x0 = tau>1 ? cmnd[tau-1] : cmnd[tau];
			const x1 = cmnd[tau];
			const x2 = tau+1<=maxTau ? cmnd[tau+1] : cmnd[tau];
			const a = (x0 + x2 - 2*x1) / 2;
			const b = (x2 - x0) / 2;
			let betterTau = tau;
			if (Math.abs(a) > 1e-12) betterTau = tau - b / (2*a);

			const freq = sampleRate / betterTau;
			const prob = 1 - cmnd[tauEstimate];
			if (freq < minF || freq > maxF) return null;
			return { freq, probability: Math.max(0, Math.min(1, prob)) };
		},

		midiToNote(midi){
			const n = Math.round(midi);
			const note = NOTE_STR[(n + 1200) % 12]; // wrap
			const octave = Math.floor(n/12) - 1;
			return { note, octave };
		},

		showError(err){
			console.error("[Desk Tuner]", err);
			UI.errorBox.style.display = "block";
			UI.errorBox.textContent = (err && err.message) ? err.message : __("Microphone error. Check permissions and input device.");
		},

		async cleanup(){
			try{ this.stop(); if (this.ac && this.ac.state!=="closed") await this.ac.close(); }catch{}
		}
	};

	// --- Events -----------------------------------------------------------------
	UI.btnToggle.addEventListener("click", async () => { if (!Tuner.running) await Tuner.start(); else Tuner.stop(); });
	UI.btnReset.addEventListener("click", () => {
		Tuner.settings = { a4:440,instrument:"concert",displayMode:"concert",viewMode:"needle",gate:0.01,smoothing:0.4,deviceId:"" };
		saveSettings(Tuner.settings);
		UI.a4Input.value="440"; UI.a4Range.value="440"; UI.a4Label.textContent="440";
		UI.instrumentSelect.value="concert"; UI.displayMode.value="concert"; UI.viewMode.value="needle";
		UI.gateSelect.value="0.01"; UI.smoothingSelect.value="0.4"; UI.modeLabel.textContent = __("Concert");
		Tuner.resetDisplay();
	});

	UI.a4Range.addEventListener("input",(e)=>{ const v = clamp(Number(e.target.value||440),430,446); UI.a4Input.value=String(v); UI.a4Label.textContent=String(v); Tuner.settings.a4=v; saveSettings(Tuner.settings); });
	UI.a4Input.addEventListener("change",(e)=>{ const v = clamp(Number(e.target.value||440),430,446); UI.a4Range.value=String(v); UI.a4Label.textContent=String(v); Tuner.settings.a4=v; saveSettings(Tuner.settings); });
	UI.instrumentSelect.addEventListener("change",(e)=>{ Tuner.settings.instrument=e.target.value; saveSettings(Tuner.settings); });
	UI.displayMode.addEventListener("change",(e)=>{ Tuner.settings.displayMode=e.target.value; UI.modeLabel.textContent = e.target.value==="concert"?__("Concert"):__("Written"); saveSettings(Tuner.settings); });
	UI.viewMode.addEventListener("change",(e)=>{ Tuner.settings.viewMode=e.target.value; saveSettings(Tuner.settings); if (e.target.value==="strobe"){ UI.needleWrap.style.display="none"; UI.strobe.style.display="block"; } else if (e.target.value==="needle"){ UI.needleWrap.style.display="block"; UI.strobe.style.display="none"; } else { UI.needleWrap.style.display="block"; UI.strobe.style.display="block"; } });
	UI.gateSelect.addEventListener("change",(e)=>{ Tuner.settings.gate=Number(e.target.value||0.01); saveSettings(Tuner.settings); });
	UI.smoothingSelect.addEventListener("change",(e)=>{ Tuner.settings.smoothing=Number(e.target.value||0.4); saveSettings(Tuner.settings); });
	UI.deviceSelect.addEventListener("change", async (e)=>{ await Tuner.switchDevice(e.target.value); });

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