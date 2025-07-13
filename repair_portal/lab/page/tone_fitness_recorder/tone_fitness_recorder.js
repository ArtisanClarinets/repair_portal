// Updated: 2025-07-13 – adds role validation, memory cleanup, error fallback
frappe.pages["tone_fitness_recorder"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Tone Fitness Recorder",
    single_column: true,
  });

  page.set_primary_action("Start Recording", () => start_recording());

  const $status = $('<p class="text-muted">Idle</p>').appendTo(page.body);
  const $canvas = $('<canvas style="width:100%;height:120px;"></canvas>').appendTo(page.body);
  const ctx = $canvas[0].getContext("2d");

  let running = false;
  let analyser, audioCtx, stream, fitnessData = [];

  async function start_recording() {
    if (!frappe.user_roles.includes("Technician")) {
      frappe.msgprint("Technician role required.");
      return;
    }

    if (running) return;
    running = true;
    fitnessData = [];

    $status.text("Recording… play tone steadily");

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 1024;
    source.connect(analyser);

    const buffer = new Float32Array(analyser.fftSize);
    const startTime = Date.now();

    function loop() {
      if (!running) return;
      analyser.getFloatTimeDomainData(buffer);
      const rms = Math.sqrt(buffer.reduce((s, v) => s + v * v, 0) / buffer.length);
      fitnessData.push({ t_ms: Date.now() - startTime, rms });

      draw(buffer);
      requestAnimationFrame(loop);
    }

    loop();
    setTimeout(stop_recording, 5000);
  }

  function stop_recording() {
    running = false;
    stream.getTracks().forEach((t) => t.stop());
    audioCtx.close();

    $status.text("Saving…");

    frappe.call({
      method: "repair_portal.lab.api.save_tone_fitness",
      args: {
        instrument: null,
        readings_json: JSON.stringify(fitnessData),
      },
    }).then((r) => {
      frappe.msgprint("Saved Tone Fitness: " + r.message.name);
      $status.text("Done.");
    }).catch(() => {
      frappe.msgprint("Error saving data");
      $status.text("Idle");
    });
  }

  function draw(buf) {
    ctx.clearRect(0, 0, $canvas[0].width, $canvas[0].height);
    ctx.beginPath();
    ctx.moveTo(0, $canvas[0].height / 2);
    for (let i = 0; i < buf.length; i++) {
      const x = (i / buf.length) * $canvas[0].width;
      const y = ((1 - buf[i]) * $canvas[0].height) / 2;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
};