frappe.pages["intonation_recorder"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Intonation Recorder",
    single_column: true,
  });

  page.set_primary_action("Start Recording", async () => start_recording());

  const $status = $('<p class="text-muted">Idle</p>').appendTo(page.body);
  const $canvas = $(
    '<canvas style="width:100%;height:120px;"></canvas>',
  ).appendTo(page.body);
  const ctx = $canvas[0].getContext("2d");

  let mediaStream,
    audioCtx,
    analyser,
    recorderChunks = [];
  let running = false,
    lastPitch = null,
    peaks = [];

  async function start_recording() {
    if (running) {
      stop_recording();
      return;
    }
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(mediaStream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    source.connect(analyser);

    const mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: "audio/webm",
    });
    mediaRecorder.ondataavailable = (e) => recorderChunks.push(e.data);
    mediaRecorder.start();

    running = true;
    $status.text("Recording… click again to stop");

    const buffer = new Float32Array(analyser.fftSize);
    const loop = () => {
      if (!running) return;
      analyser.getFloatTimeDomainData(buffer);
      const pitchHz = detect_pitch(buffer, audioCtx.sampleRate);
      if (pitchHz) {
        const now = frappe.datetime.now_datetime();
        peaks.push({ note_hz: pitchHz, reading_time: now });
        lastPitch = pitchHz;
      }
      draw_waveform(buffer);
      requestAnimationFrame(loop);
    };
    loop();

    page.set_primary_action("Stop & Save", stop_recording);

    async function stop_recording() {
      running = false;
      mediaRecorder.stop();
      mediaStream.getTracks().forEach((t) => t.stop());
      $status.text("Processing…");

      const blob = new Blob(recorderChunks, { type: "audio/webm" });
      const base64 = await blob_to_base64(blob);

      const safe_filename =
        "intonation_" +
        frappe.datetime.now_datetime().replace(/[: ]/g, "_") +
        ".webm";

      frappe
        .call("repair_portal.lab.api.save_intonation_session", {
          instrument: null,
          player: null,
          session_type: "Standalone",
          raw_data: JSON.stringify(peaks),
          recording_base64: base64,
          filename: safe_filename,
        })
        .then((r) => {
          frappe.msgprint("Saved as " + r.message.name);
          $status.text("Saved ✓");
          peaks = [];
          recorderChunks = [];
          page.set_primary_action("Start Recording", start_recording);
        })
        .catch((e) => {
          frappe.msgprint("Error: " + e.message);
          $status.text("Error");
          page.set_primary_action("Start Recording", start_recording);
        });
    }
  }

  function detect_pitch(buf, sampleRate) {
    let maxSamples = buf.length,
      bestOffset = -1,
      bestCorr = 0;
    for (let offset = 32; offset < 1000; offset++) {
      let corr = 0;
      for (let i = 0; i < maxSamples - offset; i++)
        corr += buf[i] * buf[i + offset];
      corr = corr / maxSamples;
      if (corr > 0.9 && corr > bestCorr) {
        bestCorr = corr;
        bestOffset = offset;
      }
    }
    if (bestOffset > -1) return sampleRate / bestOffset;
    return null;
  }

  function draw_waveform(buf) {
    const { width, height } = $canvas[0];
    ctx.clearRect(0, 0, width, height);
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    for (let i = 0; i < buf.length; i++) {
      const x = (i / buf.length) * width;
      const y = ((1 - buf[i]) * height) / 2;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
    if (lastPitch) {
      ctx.fillText(lastPitch.toFixed(1) + " Hz", 10, 10);
    }
  }

  function blob_to_base64(blob) {
    return new Promise((r) => {
      const reader = new FileReader();
      reader.onloadend = () => r(reader.result.split(",")[1]);
      reader.readAsDataURL(blob);
    });
  }
};
