// Updated: 2025-07-13 – adds role check, progress feedback, memory cleanup
frappe.pages['leak_test_recorder'].on_page_load = (wrapper) => {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Leak Test Recorder",
    single_column: true,
  });

  page.set_primary_action("Start Test", () => start_test());

  const $status = $('<p class="text-muted">Idle</p>').appendTo(page.body);
  const $canvas = $(
    '<canvas style="width:100%;height:120px;"></canvas>',
  ).appendTo(page.body);
  const ctx = $canvas[0].getContext("2d");

  let running = false;
  let analyser,
    audioCtx,
    stream,
    decayData = [];

  async function start_test() {
    if (!frappe.user_roles.includes("Technician")) {
      frappe.msgprint("Technician role required.");
      return;
    }

    if (running) return;
    running = true;
    decayData = [];

    $status.text("Recording… please seal and release keyhole");

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);

    const buffer = new Uint8Array(analyser.frequencyBinCount);
    const startTime = Date.now();

    function loop() {
      if (!running) return;
      analyser.getByteTimeDomainData(buffer);
      const rms = Math.sqrt(
        buffer.reduce((sum, v) => sum + (v - 128) ** 2, 0) / buffer.length,
      );
      decayData.push({ t_ms: Date.now() - startTime, rms });

      draw(rms);
      requestAnimationFrame(loop);
    }

    loop();
    setTimeout(stop_test, 5000);
  }

  function stop_test() {
    running = false;
    stream.getTracks().forEach((t) => t.stop());
    audioCtx.close();

    $status.text("Saving…");

    frappe
      .call({
        method: "repair_portal.lab.api.save_leak_test",
        args: {
          instrument: null,
          readings_json: JSON.stringify(decayData),
        },
      })
      .then((r) => {
        frappe.msgprint(`Saved Leak Test: ${r.message.name}`);
        $status.text("Done.");
      });
  }

  function draw(rms) {
    ctx.clearRect(0, 0, $canvas[0].width, $canvas[0].height);
    ctx.fillRect(0, $canvas[0].height * (1 - rms / 128), 10, 10);
  }
};
