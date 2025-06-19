// Dashboard for audio capture and visualisation
frappe.pages["lab_dashboard"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Lab Dashboard",
    single_column: true,
  });

  const root = $('<div class="p-4">')
    .appendTo(page.body)
    .attr("id", "lab-root");
  root.append(
    '<button class="btn btn-primary" id="start-btn">Start Sweep</button>',
  );
  root.append('<div id="plot" class="mt-4"></div>');

  document.getElementById("start-btn").addEventListener("click", async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const context = new (window.AudioContext || window.webkitAudioContext)();
    const source = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();
    source.connect(analyser);
    const data = new Float32Array(analyser.fftSize);
    analyser.getFloatFrequencyData(data);
    frappe
      .call("repair_portal.lab.api.save_impedance_snapshot", {
        instrument: "",
        session_type: "Standalone",
        raw_data: JSON.stringify(Array.from(data)),
      })
      .then((r) => {
        frappe.msgprint("Saved: " + r.message.name);
      });
    Plotly.newPlot("plot", [{ y: Array.from(data) }], { margin: { t: 0 } });
  });
};
