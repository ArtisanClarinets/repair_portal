// Tone & Intonation Analyzer - Desk Page Version
// Last Updated: 2025-07-24
// Purpose: Audio capture, pitch/harmonic analysis, and visualization for lab users
// Standalone Desk page (no DocType context required)

frappe.pages['tone_intonation_analyzer'].on_page_load = (wrapper) => {
  let audioContext, analyser, animationId, source, _processor;
  let running = false;
  let referencePitch = 440;
  const _harmonics = null;
  let detectedNote = '--', detectedCents = 0, _detectedFreq = 0;
  const harmonicsChart = null;

  // --- UI Injection ---
  const html = `
    <style>
      .tia-main { max-width: 540px; margin: 36px auto; padding: 32px; background: var(--fg-color); border-radius: 1.2em; }
      .tia-note { font-size: 2.6rem; font-weight: 700; color: var(--primary); margin: 0 0 5px; height: 48px; }
      .tia-cents { font-size: 1.2rem; color: var(--text-muted); }
      .tia-controls { margin-bottom: 22px; }
      .tia-canvas { margin: 15px 0 22px 0; background: #f7f7f7; border-radius: 10px; }
      .tia-harmonics { margin: 12px 0; }
    </style>
    <div class="tia-main">
      <div class="tia-controls">
        Reference Pitch:
        <select id="tia-ref-pitch" style="width: 120px;">
          <option value="440">A4 = 440 Hz</option>
          <option value="442">A4 = 442 Hz</option>
          <option value="443">A4 = 443 Hz</option>
          <option value="415">A4 = 415 Hz</option>
        </select>
        <button class="btn btn-primary" id="tia-toggle-btn">
          <i class="fa fa-microphone"></i> <span>Start Live Analysis</span>
        </button>
      </div>
      <div class="tia-note" id="tia-note">--</div>
      <div class="tia-cents" id="tia-cents">Cents: --</div>
      <div class="tia-cents" id="tia-freq">Frequency: -- Hz</div>
      <canvas id="tia-canvas" class="tia-canvas" width="500" height="60"></canvas>
      <div class="tia-harmonics">
        <h5>Harmonics (Spectrum)</h5>
        <canvas id="tia-harmonics-chart" width="500" height="90"></canvas>
      </div>
      <div class="tia-help text-muted mt-3">Play and sustain a note. The tuner and spectrum will update in real time.</div>
    </div>
  `;
  $(wrapper).html(html);

  // --- Element handles ---
  const $note = $('#tia-note');
  const $cents = $('#tia-cents');
  const $freq = $('#tia-freq');
  const $canvas = $('#tia-canvas')[0];
  const $toggleBtn = $('#tia-toggle-btn');
  const $refPitch = $('#tia-ref-pitch');
  const $harmonicsChart = $('#tia-harmonics-chart')[0];

  // --- Reference pitch selection ---
  $refPitch.val(referencePitch);
  $refPitch.on('change', () => {
    referencePitch = Number($refPitch.val());
  });

  // --- Live Analysis Button ---
  $toggleBtn.on('click', () => {
    if (!running) {
      startAnalyzer();
    } else {
      stopAnalyzer();
    }
  });

  // --- Core Pitch Detection (Autocorrelation) ---
  function detectPitch(timeData, sr) {
    let SIZE = timeData.length;
    let rms = 0;
    for (let i = 0; i < SIZE; i++) rms += timeData[i] * timeData[i];
    rms = Math.sqrt(rms / SIZE);
    if (rms < 0.01) return -1;
    let r1 = 0, r2 = SIZE - 1, thres = 0.2;
    for (let i = 0; i < SIZE / 2; i++) if (Math.abs(timeData[i]) < thres) { r1 = i; break; }
    for (let i = 1; i < SIZE / 2; i++) if (Math.abs(timeData[SIZE - i]) < thres) { r2 = SIZE - i; break; }
    timeData = timeData.slice(r1, r2);
    SIZE = timeData.length;
    const c = new Float32Array(SIZE).fill(0);
    for (let i = 0; i < SIZE; i++) {
      for (let j = 0; j < SIZE - i; j++) {
        c[i] += timeData[j] * timeData[j + i];
      }
    }
    let d = 0; while (c[d] > c[d + 1]) d++;
    let maxval = -1, maxpos = -1;
    for (let i = d; i < SIZE; i++) if (c[i] > maxval) { maxval = c[i]; maxpos = i; }
    let T0 = maxpos;
    const x1 = c[T0 - 1], x2 = c[T0], x3 = c[T0 + 1];
    const a = (x1 + x3 - 2 * x2) / 2, b = (x3 - x1) / 2;
    if (a) T0 = T0 - b / (2 * a);
    if (T0 === 0) return -1;
    return sr / T0;
  }

  // --- Note Naming ---
  const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  function getNoteName(freq, a4 = 440) {
    const noteNum = 12 * (Math.log(freq / a4) / Math.log(2));
    const midiNum = 69 + Math.round(noteNum);
    const noteName = NOTE_NAMES[(midiNum) % 12] + Math.floor(midiNum / 12 - 1);
    return noteName;
  }

  // --- Live Audio Analysis ---
  function startAnalyzer() {
    if (running) return;
    running = true;
    $toggleBtn.removeClass('btn-primary').addClass('btn-danger');
    $toggleBtn.find('i').removeClass('fa-microphone').addClass('fa-stop');
    $toggleBtn.find('span').text('Stop Analysis');

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      animate();
    }).catch(_e => {
      frappe.msgprint('Microphone access denied');
      stopAnalyzer();
    });
  }

  function stopAnalyzer() {
    running = false;
    if (animationId) cancelAnimationFrame(animationId);
    $toggleBtn.addClass('btn-primary').removeClass('btn-danger');
    $toggleBtn.find('i').addClass('fa-microphone').removeClass('fa-stop');
    $toggleBtn.find('span').text('Start Live Analysis');
    if (audioContext) audioContext.close();
    $note.text('--');
    $cents.text('Cents: --');
    $freq.text('Frequency: -- Hz');
    const ctx = $canvas.getContext('2d'); ctx.clearRect(0,0,$canvas.width,$canvas.height);
    if (harmonicsChart) { harmonicsChart.getContext('2d').clearRect(0,0,500,90); }
  }

  function animate() {
    if (!running) return;
    const buf = new Float32Array(analyser.fftSize);
    analyser.getFloatTimeDomainData(buf);
    const freq = detectPitch(buf, audioContext.sampleRate);
    if (freq > 40) {
      _detectedFreq = freq;
      detectedNote = getNoteName(freq, referencePitch);
      const refFreq = referencePitch * 2 ** ((Math.round(12 * (Math.log(freq / referencePitch) / Math.log(2))))/12);
      detectedCents = 1200 * Math.log2(freq / refFreq);
      $note.text(detectedNote);
      $cents.text(`Cents: ${detectedCents.toFixed(1)}`);
      $freq.text(`Frequency: ${freq.toFixed(2)} Hz`);
    } else {
      $note.text('--'); $cents.text('Cents: --'); $freq.text('Frequency: -- Hz');
    }
    // Draw waveform
    const ctx = $canvas.getContext('2d');
    ctx.clearRect(0, 0, $canvas.width, $canvas.height);
    ctx.beginPath();
    ctx.moveTo(0, 30);
    for (let i = 0; i < buf.length; i++) {
      const x = (i / buf.length) * $canvas.width;
      const y = 30 + buf[i] * 25;
      ctx.lineTo(x, y);
    }
    ctx.strokeStyle = '#007bff';
    ctx.stroke();
    // Harmonics spectrum
    const freqData = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(freqData);
    const hctx = $harmonicsChart.getContext('2d');
    hctx.clearRect(0, 0, 500, 90);
    hctx.fillStyle = '#88c';
    for (let i = 0; i < freqData.length && i < 500; i++) {
      const mag = freqData[i];
      hctx.fillRect(i, 90 - mag * 0.32, 1, mag * 0.32);
    }
    animationId = requestAnimationFrame(animate);
  }

  // Clean up on page leave
  $(wrapper).on('remove', () => stopAnalyzer());
};
