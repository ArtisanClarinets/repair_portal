/** biome-ignore-all lint */
/* global frappe */

frappe.provide("repair_portal.lab");

frappe.pages["lab-console"].on_page_load = function (wrapper) {
	const $ = window.jQuery; // ensure alias exists before first use

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Lab Console"),
		single_column: true
	});

	// ---------- UI ----------
	const ui = `
	<style>
		.lab-wrap{max-width:1024px;margin:16px auto;padding:16px;background:var(--fg-color);border-radius:var(--border-radius-lg);box-shadow:var(--shadow-sm)}
		.grid{display:grid;grid-template-columns:1fr;gap:12px}
		@media(min-width:980px){.grid{grid-template-columns:360px 1fr}}
		.card{border:1px solid var(--border-color);border-radius:var(--border-radius-md);padding:12px}
		.card h5{margin:4px 0 10px 0}
		.form-row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:8px}
		.form-row label{white-space:nowrap}
		.btn-row{display:flex;gap:8px;flex-wrap:wrap}
		.level{height:8px;border-radius:999px;background:var(--bg-color);border:1px solid var(--border-color);overflow:hidden}
		.level-fill{height:100%;width:0%;transition:width .1s linear}
		.section-title{font-weight:600;margin:6px 0 4px}
		.inline-badge{padding:2px 8px;border-radius:999px;border:1px solid var(--border-color);font-size:12px}
		canvas{border-radius:8px;border:1px solid var(--border-color)}
		#strobe{height:100px}
		#spectrogram{height:160px}
		#needle{position:relative;height:56px}
		.needle-base{position:absolute;left:0;right:0;bottom:0;height:2px;background:var(--border-color)}
		.needle-line{position:absolute;left:50%;bottom:-2px;width:4px;height:100%;background:var(--red-500);transform-origin:bottom center;transform:translateX(-50%) rotate(0deg);border-radius:4px 4px 0 0}
		.in-tune .needle-line{background:var(--green-500)}
		.center-tick{position:absolute;left:50%;transform:translateX(-50%);bottom:0;width:2px;height:100%;background:var(--border-color)}
		.side-tick{position:absolute;bottom:0;width:2px;height:50%;background:var(--border-color)}
		.l25{left:25%} .r25{right:25%}
		.meta{color:var(--text-muted);font-size:.9rem}
		.big-note{font-size:4rem;line-height:1;font-weight:700}
		.err{display:none}
	</style>

	<div class="lab-wrap">
		<div class="grid">
			<!-- LEFT: Capture -->
			<div class="card">
				<h5>${__("Capture")}</h5>
				<div class="form-row">
					<label>${__("Session")}:</label>
					<select id="session-select" class="form-control" style="min-width:160px"></select>
					<button id="new-session" class="btn btn-default btn-sm">${__("New")}</button>
					<span id="session-badge" class="inline-badge">—</span>
				</div>
				<div class="form-row">
					<label>${__("Test Type")}:</label>
					<select id="test-type" class="form-control">
						<option value="intonation">${__("Intonation")}</option>
						<option value="resonance">${__("Resonance (ESS)")}</option>
						<option value="leak">${__("Leak")}</option>
						<option value="tone_fitness">${__("Tone Fitness")}</option>
						<option value="measurement">${__("Measurement")}</option>
						<option value="reed_match">${__("Reed Match")}</option>
					</select>
				</div>
				<div class="form-row">
					<label>${__("Instrument")}:</label>
					<select id="instrument-type" class="form-control">
						<option value="Bb">B♭</option>
						<option value="A">A</option>
						<option value="Eb">E♭</option>
						<option value="Bass">Bass</option>
					</select>
					<label>A4</label>
					<input id="a4" type="number" class="form-control" value="440" min="430" max="446" step="1" style="width:90px">
					<label>${__("Display")}</label>
					<select id="display-mode" class="form-control">
						<option value="concert">${__("Concert")}</option>
						<option value="written">${__("Written")}</option>
					</select>
				</div>
				<div class="form-row">
					<label>${__("Microphone")}:</label>
					<select id="mic" class="form-control" style="min-width:240px"></select>
					<button id="refresh-mics" class="btn btn-default btn-sm"><i class="fa fa-refresh"></i></button>
				</div>

				<div class="btn-row" style="margin-top:8px">
					<button id="btn-start" class="btn btn-primary"><i class="fa fa-circle" style="margin-right:6px"></i>${__("Start")}</button>
					<button id="btn-stop" class="btn btn-danger" disabled><i class="fa fa-stop" style="margin-right:6px"></i>${__("Stop")}</button>
					<button id="btn-save" class="btn btn-secondary" disabled><i class="fa fa-cloud-upload" style="margin-right:6px"></i>${__("Save & Analyze")}</button>
				</div>

				<div class="section-title">${__("Environment")}</div>
				<div class="form-row">
					<label>°C</label><input id="env-temp" type="number" class="form-control" style="width:90px">
					<label>%RH</label><input id="env-rh" type="number" class="form-control" style="width:90px">
					<label>hPa</label><input id="env-hpa" type="number" class="form-control" style="width:100px">
					<label>dBA</label><input id="env-dba" type="number" class="form-control" style="width:90px">
				</div>

				<div id="err" class="alert alert-danger err" style="margin-top:8px"></div>
			</div>

			<!-- RIGHT: Live -->
			<div class="card">
				<h5>${__("Live View")}</h5>
				<div class="form-row" style="align-items:flex-end;justify-content:space-between">
					<div>
						<div id="note" class="big-note">--</div>
						<div id="meta" class="meta">A4=440 · ${__("Concert")}</div>
					</div>
					<div style="min-width:220px">
						<div class="level"><div id="lvl" class="level-fill"></div></div>
					</div>
				</div>
				<div id="needle" style="margin-top:8px">
					<div class="needle-base"></div>
					<div class="center-tick"></div>
					<div class="side-tick l25"></div>
					<div class="side-tick r25"></div>
					<div id="needle-line" class="needle-line"></div>
				</div>
				<canvas id="strobe" style="width:100%;margin-top:8px"></canvas>
				<canvas id="spectrogram" style="width:100%;margin-top:8px"></canvas>
			</div>
		</div>

		<!-- Bottom: Visualize last result -->
		<div class="card" style="margin-top:12px">
			<h5>${__("Visualize (Latest Saved Test)")}</h5>
			<div id="viz" class="form-row"></div>
		</div>
	</div>
	`;
	$(wrapper).html(ui);

	// ---------- State ----------
	const UI = {
		sessionSelect: $("#session-select"),
		newSession: $("#new-session"),
		sessionBadge: $("#session-badge"),
		testType: $("#test-type"),
		instr: $("#instrument-type"),
		a4: $("#a4"),
		displayMode: $("#display-mode"),
		mic: $("#mic"),
		refreshMics: $("#refresh-mics"),
		btnStart: $("#btn-start"),
		btnStop: $("#btn-stop"),
		btnSave: $("#btn-save"),
		err: $("#err"),
		lvl: $("#lvl"),
		note: $("#note"),
		meta: $("#meta"),
		needle: $("#needle-line"),
		strobe: document.getElementById("strobe"),
		spec: document.getElementById("spectrogram"),
		viz: $("#viz"),
		env: {
			temp: $("#env-temp"),
			rh: $("#env-rh"),
			hpa: $("#env-hpa"),
			dba: $("#env-dba")
		}
	};

	const NOTE_STR = ["C","C♯","D","D♯","E","F","F♯","G","G♯","A","A♯","B"];
	const TRANSPOSE = { concert:0, Bb:+2, A:+3, Eb:-3, Bass:+14 };

	const State = {
		ac: null,
		src: null,
		an: null,
		data: null,
		rAF: 0,
		stream: null,
		startTs: null,
		frames: [],     // intonation frames [{t,f0,conf,cents,note}]
		resp: null,     // resonance {freq[],magdb[]}
		specCtx: null,
		strobeCtx: null,
		lastStrobeTs: 0,
		strobePhase: 0,
		session: null,  // current Lab Session name (string)
		lastSavedTest: null
	};

	// ---------- Helpers ----------
	const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
	const toDB = (x) => 20 * Math.log10(x + 1e-12);

	function midiToName(m) {
		const n = Math.round(m);
		return NOTE_STR[(n + 1200) % 12] + (Math.floor(n / 12) - 1);
	}

	function centsError(f, a4, midiNearest) {
		const target = a4 * Math.pow(2, (midiNearest - 69) / 12);
		return 1200 * Math.log2(f / target);
	}

	// ---------- Audio / Pitch ----------
	async function buildAudio(deviceId) {
		State.ac = new (window.AudioContext || window.webkitAudioContext)();
		if (State.ac.state !== "running") await State.ac.resume();

		const stream = await navigator.mediaDevices.getUserMedia({
			audio: {
				deviceId: deviceId ? { exact: deviceId } : undefined,
				channelCount: 1,
				echoCancellation: false, noiseSuppression: false, autoGainControl: false
			}
		});
		State.stream = stream;
		State.src = State.ac.createMediaStreamSource(stream);
		State.an = State.ac.createAnalyser();
		State.an.fftSize = 4096;
		State.an.smoothingTimeConstant = 0;
		State.data = new Float32Array(State.an.fftSize);
		State.src.connect(State.an);

		State.specCtx = UI.spec.getContext("2d", { alpha:false });
		State.strobeCtx = UI.strobe.getContext("2d", { alpha:false });
	}

	function destroyAudio() {
		cancelAnimationFrame(State.rAF);
		State.rAF = 0;
		try { State.stream && State.stream.getTracks().forEach(t => t.stop()); } catch {}
		try { State.ac && State.ac.suspend(); } catch {}
		State.frames = [];
		State.resp = null;
	}

	function yinPitch(buf, sr, threshold=0.1, minF=60, maxF=2000) {
		const maxTau = Math.floor(sr / minF);
		const minTau = Math.floor(sr / maxF);
		const N = buf.length;
		if (N < maxTau + 2) return null;

		const d = new Float32Array(maxTau + 1);
		for (let tau = 1; tau <= maxTau; tau++) {
			let sum = 0;
			for (let i = 0; i < N - tau; i++) {
				const dx = buf[i] - buf[i + tau];
				sum += dx * dx;
			}
			d[tau] = sum;
		}
		const cmnd = new Float32Array(maxTau + 1);
		cmnd[0] = 1;
		let run = 0;
		for (let tau = 1; tau <= maxTau; tau++) {
			run += d[tau];
			cmnd[tau] = d[tau] * tau / (run || 1);
		}
		let tauEst = -1;
		for (let tau = minTau; tau <= maxTau; tau++) {
			if (cmnd[tau] < threshold) {
				while (tau + 1 <= maxTau && cmnd[tau + 1] < cmnd[tau]) tau++;
				tauEst = tau; break;
			}
		}
		if (tauEst < 0) {
			let mv = 1e9, mi = -1;
			for (let tau = minTau; tau <= maxTau; tau++) {
				if (cmnd[tau] < mv) { mv = cmnd[tau]; mi = tau; }
			}
			tauEst = mi; if (tauEst < 0) return null;
		}
		const tau = tauEst;
		const x0 = tau > 1 ? cmnd[tau - 1] : cmnd[tau];
		const x1 = cmnd[tau];
		const x2 = tau + 1 <= maxTau ? cmnd[tau + 1] : cmnd[tau];
		const a = (x0 + x2 - 2 * x1) / 2;
		const b = (x2 - x0) / 2;
		let betterTau = tau;
		if (Math.abs(a) > 1e-12) betterTau = tau - b / (2 * a);
		const f0 = sr / betterTau;
		const prob = 1 - cmnd[tauEst];
		if (f0 < minF || f0 > maxF) return null;
		return { f0, prob: clamp(prob, 0, 1) };
	}

	// Simple rolling STFT spectrogram (CPU-friendly)
	const STFT = (() => {
		const win = (N) => { const w=new Float32Array(N); for (let i=0;i<N;i++) w[i]=0.5*(1-Math.cos(2*Math.PI*i/(N-1))); return w; };
		const hann2048 = win(2048);
		const re = new Float32Array(2048), im = new Float32Array(2048);
		function fftRadix2(real, imag) { // in-place Cooley–Tukey (power of 2)
			const n = real.length;
			for (let i=1,j=0;i<n;i++){
				let bit = n>>1;
				for (; j&bit; bit>>=1) j&=~bit;
				j|=bit;
				if (i<j){ const tr=real[i]; real[i]=real[j]; real[j]=tr; const ti=imag[i]; imag[i]=imag[j]; imag[j]=ti; }
			}
			for (let len=2; len<=n; len<<=1){
				const ang = -2*Math.PI/len;
				const wlen_r = Math.cos(ang), wlen_i = Math.sin(ang);
				for (let i=0;i<n;i+=len){
					let wr=1, wi=0;
					for (let j=0;j<len/2;j++){
						const u_r = real[i+j], u_i = imag[i+j];
						const v_r = real[i+j+len/2]*wr - imag[i+j+len/2]*wi;
						const v_i = real[i+j+len/2]*wi + imag[i+j+len/2]*wr;
						real[i+j] = u_r + v_r; imag[i+j] = u_i + v_i;
						real[i+j+len/2] = u_r - v_r; imag[i+j+len/2] = u_i - v_i;
						const nxt_wr = wr*wlen_r - wi*wlen_i;
						const nxt_wi = wr*wlen_i + wi*wlen_r;
						wr = nxt_wr; wi = nxt_wi;
					}
				}
			}
		}
		return {
			frame(buf, sr, ctx) {
				// take first 2048 samples for quick look
				const N = 2048;
				for (let i=0;i<N;i++){ re[i] = (buf[i]||0)*hann2048[i]; im[i] = 0; }
				fftRadix2(re, im);
				const mag = new Float32Array(N/2);
				for (let k=0;k<N/2;k++){ const mr = re[k], mi = im[k]; mag[k]=Math.sqrt(mr*mr+mi*mi); }
				// draw right-shifting waterfall
				const dpr = Math.max(1, window.devicePixelRatio||1);
				const w = ctx.canvas.width = Math.floor(ctx.canvas.clientWidth * dpr);
				const h = ctx.canvas.height = Math.floor(ctx.canvas.clientHeight * dpr);
				const img = ctx.getImageData(0,0,w,h);
				ctx.putImageData(img, -1, 0); // scroll left by 1px
				// draw new column at right
				const colx = w-1;
				for (let y=0;y<h;y++){
					const f = Math.floor((y/h)*mag.length);
					const db = toDB(mag[f]);
					const norm = clamp((db + 100)/60, 0, 1);
					const val = Math.floor(norm*255);
					ctx.fillStyle = `rgb(${val},${Math.floor(val*0.6)},${Math.floor(255-val)})`;
					ctx.fillRect(colx, h-1-y, 1, 1);
				}
			}
		};
	})();

	// ---------- Live loop ----------
	function loop(ts) {
		if (!State.an) return;
		State.an.getFloatTimeDomainData(State.data);
		// level
		let sum=0; for (let i=0;i<State.data.length;i++) sum += State.data[i]*State.data[i];
		const rms = Math.sqrt(sum / State.data.length);
		UI.lvl.css("width", `${clamp((rms / 0.3) * 100, 0, 100)}%`);

		// pitch
		const pitch = yinPitch(State.data, State.ac.sampleRate, 0.1, 60, 2000);
		const a4 = Number(UI.a4.val() || 440);
		const displayMode = UI.displayMode.val();
		const instr = UI.instr.val();
		if (pitch) {
			const midi = 69 + 12*Math.log2(pitch.f0 / a4);
			const midiNearest = Math.round(midi);
			const cents = centsError(pitch.f0, a4, midiNearest);
			const transpose = displayMode === "written" ? (TRANSPOSE[instr === "Bb" ? "Bb" : instr] || 0) : 0;
			const displayMidi = midiNearest + transpose;
			const name = midiToName(displayMidi);

			UI.note.text(name);
			UI.meta.text(`${pitch.f0.toFixed(2)} Hz · ${cents>=0?"+":""}${cents.toFixed(1)} ¢ · A4=${a4} · ${displayMode}`);

			// needle & strobe
			const rot = clamp((cents/50)*45, -45, 45);
			UI.needle.css("transform", `translateX(-50%) rotate(${rot}deg)`);
			if (Math.abs(cents) < 5) $(wrapper).find(".lab-wrap").addClass("in-tune"); else $(wrapper).find(".lab-wrap").removeClass("in-tune");
			drawStrobe(ts, cents);

			// frames for intonation
			if (State.startTs) {
				State.frames.push({
					t: (performance.now() - State.startTs)/1000,
					f0: pitch.f0,
					conf: pitch.prob,
					cents,
					midi: midiNearest,
					name
				});
			}
		} else {
			UI.meta.text(__("Analyzing…"));
			UI.needle.css("transform", "translateX(-50%) rotate(0deg)");
			drawStrobe(ts, 0);
		}

		// spectrogram
		STFT.frame(State.data, State.ac.sampleRate, State.specCtx);

		State.rAF = requestAnimationFrame(loop);
	}

	function drawStrobe(ts, cents){
		const ctx = State.strobeCtx; if (!ctx) return;
		const dpr = Math.max(1, window.devicePixelRatio||1);
		const w = ctx.canvas.width = Math.floor(ctx.canvas.clientWidth * dpr);
		const h = ctx.canvas.height = Math.floor(ctx.canvas.clientHeight * dpr);
		const now = ts || performance.now();
		const dt = State.lastStrobeTs ? (now - State.lastStrobeTs)/1000 : 0;
		State.lastStrobeTs = now;
		const speed = 4*dpr;
		State.strobePhase += (cents * speed) * dt;
		const stripeW = Math.max(12*dpr, Math.min(40*dpr, w/20));
		const offset = ((State.strobePhase % stripeW) + stripeW) % stripeW;
		ctx.fillStyle = "#111"; ctx.fillRect(0,0,w,h);
		for (let x = -stripeW + offset; x < w + stripeW; x += stripeW){
			const g = ctx.createLinearGradient(x,0,x+stripeW,0);
			g.addColorStop(0,"rgba(255,255,255,0.06)");
			g.addColorStop(0.5,"rgba(255,255,255,0.25)");
			g.addColorStop(1,"rgba(255,255,255,0.06)");
			ctx.fillStyle = g; ctx.fillRect(x,0,stripeW,h);
		}
		ctx.fillStyle = "rgba(0,0,0,0.5)";
		ctx.fillRect(w/2-2*dpr,0,4*dpr,h);
	}

	// ---------- Resonance (ESS) on client ----------
	async function runESS() {
		// lightweight log sweep, 6s 50–8000 Hz
		const sr = State.ac.sampleRate, T=6, f1=50, f2=8000;
		const L = Math.floor(sr*T);
		const sweep = new Float32Array(L);
		const K = T*Math.log(f2/f1);
		for (let n=0;n<L;n++){ const t = n/sr; sweep[n] = Math.sin(2*Math.PI * f1 * (Math.exp(t/T*Math.log(f2/f1))-1)/Math.log(f2/f1)); }
		const buf = State.ac.createBuffer(1, L, sr);
		buf.getChannelData(0).set(sweep);
		const src = State.ac.createBufferSource(); src.buffer = buf;
		src.connect(State.ac.destination);
		src.start();
		// record mic simultaneously
		const analyser = State.an; const N=2048;
		const tmp = [];
		const rec = () => {
			const t = new Float32Array(N);
			analyser.getFloatTimeDomainData(t);
			tmp.push(Array.from(t));
			if (tmp.length < Math.ceil(L/N)+10) requestAnimationFrame(rec);
		};
		rec();
		await new Promise(res=>setTimeout(res, (T+0.4)*1000));
		// flatten and naive magnitude estimate via FFT of last frame (demo-quality)
		const flat = new Float32Array(tmp.length*N);
		for (let i=0;i<tmp.length;i++) flat.set(tmp[i], i*N);
		// Simple windowed FFT average
		const M = 12; // number of frames to average
		const mags = new Float32Array(N/2).fill(0);
		for (let m=0;m<M && m<tmp.length; m++){
			const fr = new Float32Array(N), fi = new Float32Array(N);
			const hann = (i)=>0.5*(1-Math.cos(2*Math.PI*i/(N-1)));
			for (let i=0;i<N;i++){ fr[i] = (tmp[tmp.length-1-m][i]||0)*hann(i); }
			fftRadix2(fr,fi);
			for (let k=0;k<N/2;k++){ const mr=fr[k], mi=fi[k]; mags[k]+=Math.sqrt(mr*mr+mi*mi); }
		}
		for (let k=0;k<mags.length;k++) mags[k]/=M;
		const freq = new Array(N/2).fill(0).map((_,k)=>k*sr/N);
		const magdb = mags.map(toDB);
		State.resp = { freq, magdb };
		function fftRadix2(real, imag) {
			const n = real.length;
			for (let i=1,j=0;i<n;i++){
				let bit = n>>1;
				for (; j&bit; bit>>=1) j&=~bit;
				j|=bit;
				if (i<j){ const tr=real[i]; real[i]=real[j]; real[j]=tr; const ti=imag[i]; imag[i]=imag[j]; imag[j]=ti; }
			}
			for (let len=2; len<=n; len<<=1){
				const ang = -2*Math.PI/len;
				const wlen_r = Math.cos(ang), wlen_i = Math.sin(ang);
				for (let i=0;i<n;i+=len){
					let wr=1, wi=0;
					for (let j=0;j<len/2;j++){
						const u_r = real[i+j], u_i = imag[i+j];
						const v_r = real[i+j+len/2]*wr - imag[i+j+len/2]*wi;
						const v_i = real[i+j+len/2]*wi + imag[i+j+len/2]*wr;
						real[i+j] = u_r + v_r; imag[i+j] = u_i + v_i;
						real[i+j+len/2] = u_r - v_r; imag[i+j+len/2] = u_i - v_i;
						const nxt_wr = wr*wlen_r - wi*wlen_i;
						const nxt_wi = wr*wlen_i + wi*wlen_r;
						wr = nxt_wr; wi = nxt_wi;
					}
				}
			}
		}
	}

	// ---------- Sessions ----------
	async function loadSessions() {
		const r = await frappe.call("repair_portal.lab.api.list_sessions");
		const list = r.message || [];
		UI.sessionSelect.empty();
		UI.sessionSelect.append(`<option value="">${__("New Session…")}</option>`);
		list.forEach(s => UI.sessionSelect.append(`<option value="${frappe.utils.escape_html(s.name)}">${frappe.utils.escape_html(s.name)} — ${frappe.utils.escape_html(s.instrument_type||"")}</option>`));
	}

	function sessPayload() {
		return {
			reference_pitch: Number(UI.a4.val() || 440),
			instrument_type: UI.instr.val(),
			temperature: UI.env.temp.val() ? Number(UI.env.temp.val()) : null,
			humidity: UI.env.rh.val() ? Number(UI.env.rh.val()) : null,
			pressure: UI.env.hpa.val() ? Number(UI.env.hpa.val()) : null,
			room_noise_dba: UI.env.dba.val() ? Number(UI.env.dba.val()) : null
		};
	}

	// ---------- Save & Analyze ----------
	async function saveAndAnalyze() {
		try {
			UI.err.hide();
			const test_type = UI.testType.val();
			const a4 = Number(UI.a4.val()||440);
			const payload = {
				session_name: State.session || null,
				session_payload: sessPayload(),
				test_payload: {
					test_type,
					duration_s: State.startTs ? ((performance.now()-State.startTs)/1000) : null,
					config_json: {
						display_mode: UI.displayMode.val(),
						instrument_type: UI.instr.val(),
						a4
					},
					raw_json: test_type==="intonation" ? { frames: State.frames } :
						test_type==="resonance" ? { response: State.resp } : {}
				},
				images: [] // add snapshots
			};
			// snapshots: strobe & spectrogram
			function canvasToDataURL(cvs, name){ try{ return { filename:name, dataurl:cvs.toDataURL("image/png") }; }catch{return null;} }
			const snap1 = canvasToDataURL(UI.strobe, "strobe.png");
			const snap2 = canvasToDataURL(UI.spec, "spectrogram.png");
			[snap1, snap2].forEach(s => s && payload.images.push(s));

			const r = await frappe.call("repair_portal.lab.api.save_lab_test", { payload });
			const resp = r.message;
			State.session = resp.session;
			State.lastSavedTest = resp.test;
			UI.sessionBadge.text(State.session || "—");
			UI.btnSave.prop("disabled", true);

			// enqueue analysis
			await frappe.call("repair_portal.lab.api.enqueue_analysis", { session: resp.session, test: resp.test });

			frappe.show_alert({ message: __("Saved. Analysis started."), indicator: "green" });
			pollStatus(resp.test);
		} catch (e) {
			console.error(e);
			UI.err.text(e && e.message ? e.message : "Save failed").show();
		}
	}

	async function pollStatus(testName) {
		let tries = 0;
		const tick = async () => {
			const r = await frappe.call("repair_portal.lab.api.get_test_status", { test: testName });
			const m = r.message || {};
			if (m.status === "Complete" && m.plots && m.plots.length) {
				UI.viz.empty();
				m.plots.forEach(p => {
					const url = `/files/${encodeURIComponent(p)}`;
					UI.viz.append(`<div><img src="${url}" style="max-height:180px;border:1px solid var(--border-color);border-radius:8px;margin:6px"></div>`);
				});
				frappe.show_alert({ message: __("Analysis complete"), indicator: "green" });
			} else {
				if (tries++ < 120) setTimeout(tick, 1500);
			}
		};
		tick();
	}

	// ---------- Event wiring ----------
	UI.btnStart.on("click", async () => {
		try {
			UI.err.hide();
			if (!State.ac) await buildAudio(UI.mic.val());
			State.startTs = performance.now();
			State.frames = [];
			State.resp = null;
			UI.btnStart.prop("disabled", true);
			UI.btnStop.prop("disabled", false);
			UI.btnSave.prop("disabled", true);

			State.rAF = requestAnimationFrame(loop);

			if (UI.testType.val() === "resonance") {
				runESS(); // async; fills State.resp
			}
		} catch (e) {
			UI.err.text(e && e.message ? e.message : "Audio init failed").show();
		}
	});
	UI.btnStop.on("click", async () => {
		UI.btnStart.prop("disabled", false);
		UI.btnStop.prop("disabled", true);
		UI.btnSave.prop("disabled", false);
		destroyAudio();
	});
	UI.btnSave.on("click", saveAndAnalyze);

	UI.refreshMics.on("click", async () => { await fillMics(); });

	UI.sessionSelect.on("change", function () {
		const v = $(this).val();
		State.session = v || null;
		UI.sessionBadge.text(State.session || "—");
	});

	UI.newSession.on("click", async () => {
		State.session = null;
		UI.sessionSelect.val("");
		UI.sessionBadge.text("—");
	});

	// mics
	async function fillMics() {
		try {
			const s = await navigator.mediaDevices.getUserMedia({ audio:true });
			s.getTracks().forEach(t => t.stop());
		} catch {}
		const devices = await navigator.mediaDevices.enumerateDevices();
		const ins = devices.filter(d => d.kind === "audioinput");
		UI.mic.empty();
		ins.forEach(d => UI.mic.append(`<option value="${frappe.utils.escape_html(d.deviceId)}">${frappe.utils.escape_html(d.label || __("Microphone"))}</option>`));
	}

	// init
	(async function init(){
		await loadSessions();
		await fillMics();
	})();
};
