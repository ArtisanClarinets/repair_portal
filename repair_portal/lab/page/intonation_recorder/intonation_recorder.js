// Updated: 2025-07-13 – adds progress indicator, size checks, and role gate
frappe.pages["intonation_recorder"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Intonation Recorder",
    single_column: true,
  });

  const $btn = $("<button class='btn btn-primary'>Start Recording</button>").appendTo(
    page.body
  );
  const $status = $("<p class='text-muted'>Idle</p>").appendTo(page.body);
  const $spinner = $('<div class="spinner-border text-primary d-none" role="status"></div>').appendTo(page.body);

  let analyser, audioCtx, stream;

  $btn.on("click", async () => {
    if (!frappe.user_roles.includes("Technician")) {
      frappe.msgprint("Technician role required.");
      return;
    }

    $btn.prop("disabled", true);
    $status.text("Recording...");

    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    const buffer = new Float32Array(analyser.fftSize);

    const chunks = [];
    const recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/wav" });
      if (blob.size > 20 * 1024 * 1024) {
        frappe.msgprint("Recording too large (>20MB). Try again.");
        return;
      }

      $spinner.removeClass("d-none");
      $status.text("Saving...");

      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          await frappe.call({
            method: "repair_portal.lab.api.save_intonation_session",
            args: {
              instrument: null,
              recording_base64: reader.result.split(",")[1],
              filename: `intonation_${frappe.datetime.now_datetime().replace(/[: ]/g, "_")}.wav`,
            },
          });
          frappe.show_alert("Intonation saved");
        } catch (e) {
          console.error(e);
          frappe.msgprint("Upload failed");
        } finally {
          $spinner.addClass("d-none");
          $btn.prop("disabled", false);
          $status.text("Done.");
        }
      };
      reader.readAsDataURL(blob);
    };

    recorder.start();
    setTimeout(() => recorder.stop(), 5000);
  });
};