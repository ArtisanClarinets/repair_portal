// Dashboard for audio capture and visualisation
frappe.pages["lab_dashboard"].on_page_load = (wrapper) => {
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

  document.getElementById('start-btn').addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const context = new (window.AudioContext || window.webkitAudioContext)();
      const source = context.createMediaStreamSource(stream);
      const analyser = context.createAnalyser();
      source.connect(analyser);
      const data = new Float32Array(analyser.fftSize);
      analyser.getFloatFrequencyData(data);

      Plotly.newPlot('plot', [{ y: Array.from(data) }], { margin: { t: 0 } });

      await frappe
        .call('repair_portal.lab.api.save_impedance_snapshot', {
          instrument: frappe.utils.get_url_arg('instrument') || '',
          session_type: 'Standalone',
          raw_data: JSON.stringify(Array.from(data)),
        })
        .then((r) => {
          frappe.show_alert(__('Saved') + ': ' + r.message.name);
        });
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error(e);
      frappe.msgprint(__('Microphone access failed.'));
    }
  });
};

