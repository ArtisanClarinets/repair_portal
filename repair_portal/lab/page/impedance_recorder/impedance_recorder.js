frappe.pages["impedance_recorder"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Impedance Recorder",
    single_column: true,
  });

  page.set_primary_action("Start Test", () => start_test());

  const $status = $('<p class="text-muted">Idle</p>').appendTo(page.body);
  const $canvas = $(
    '<canvas style="width:100%;height:120px;"></canvas>',
  ).appendTo(page.body);
  const ctx = $canvas[0].getContext("2d");

  let mediaRecorder,
    recorderChunks = [];
  let running = false;

  async function start_test() {
    if (running) return;
    running = true;

    $status.text("Recording… playing chirp");
    recorderChunks = [];

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorder.ondataavailable = (e) => recorderChunks.push(e.data);
    mediaRecorder.start();

    // Play chirp stimulus
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const duration = 2;
    const sampleRate = audioCtx.sampleRate;
    const buffer = audioCtx.createBuffer(1, duration * sampleRate, sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i++) {
      const t = i / sampleRate;
      data[i] = Math.sin(
        2 * Math.PI * (100 + (5000 - 100) * (t / duration)) * t,
      );
    }
    const src = audioCtx.createBufferSource();
    src.buffer = buffer;
    src.connect(audioCtx.destination);
    src.start();

    // Wait for recording
    setTimeout(stop_test, duration * 1000 + 1000);
  }

  async function stop_test() {
    mediaRecorder.stop();
    running = false;
    $status.text("Processing…");

    const blob = new Blob(recorderChunks, { type: "audio/webm" });
    const base64 = await blob_to_base64(blob);

    frappe
      .call("repair_portal.lab.api.save_impedance_snapshot", {
        instrument: null,
        raw_data: "",
        recording_base64: base64,
        filename: "impedance_" + frappe.datetime.now_datetime() + ".webm",
      })
      .then((r) => {
        frappe.msgprint("Saved impedance snapshot: " + r.message.name);
        $status.text("Done.");
      });
  }

  function blob_to_base64(blob) {
    return new Promise((r) => {
      const reader = new FileReader();
      reader.onloadend = () => r(reader.result.split(",")[1]);
      reader.readAsDataURL(blob);
    });
  }
};
