// Intonation Recorder Desk Page - Frappe v15 compliant
// Last Updated: 2025-07-24
// Purpose: Record audio, analyze intonation offsets, and display a result chart.

frappe.pages['intonation_recorder'].on_page_load = function(wrapper) {
  let audioBlob = null;
  let chartObj = null;

  const $root = $('<div class="p-4" style="max-width:540px;margin:0 auto;"></div>').appendTo(wrapper);
  $root.append(`
    <h2>Intonation Recorder</h2>
    <div class="mb-3">
      <button class="btn btn-primary" id="start-record">Start Recording</button>
      <button class="btn btn-danger" id="stop-record" disabled>Stop Recording</button>
      <audio id="audio-playback" controls style="display:none;"></audio>
    </div>
    <div class="mb-3">
      <button class="btn btn-success" id="analyze-btn">Analyze Intonation</button>
    </div>
    <canvas id="intonation-chart" height="110"></canvas>
    <p id="intonation-note"></p>
  `);

  let mediaRecorder, audioChunks = [];

  $('#start-record').on('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
    mediaRecorder.onstop = () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      $('#audio-playback').attr('src', audioUrl).show();
    };

    mediaRecorder.start();
    $('#start-record').attr('disabled', true);
    $('#stop-record').removeAttr('disabled');
  });

  $('#stop-record').on('click', () => {
    mediaRecorder.stop();
    $('#start-record').removeAttr('disabled');
    $('#stop-record').attr('disabled', true);
  });

  $('#analyze-btn').on('click', async () => {
    if (!audioBlob) {
      frappe.msgprint('Please record audio first.');
      return;
    }
    const base64 = await new Promise(res => {
      const reader = new FileReader();
      reader.onloadend = () => res(reader.result);
      reader.readAsDataURL(audioBlob);
    });
    frappe.call({
      method: 'repair_portal.lab.api.save_intonation_session',
      type: 'POST',
      args: {
        recording_base64: base64.split(',')[1],
        filename: `intonation_${Date.now()}.wav`,
      },
      callback: r => {
        if (r.exc) return;
        frappe.msgprint(`Session saved: ${r.message.name}`);
        loadChart();
      }
    });
  });

  async function loadChart() {
    const sessions = await frappe.db.get_list('Intonation Session', { limit: 1, order_by: 'creation desc', fields: ['json_data'] });
    if (!sessions.length) return;
    const j = JSON.parse(sessions[0].json_data || '{}');
    const labels = j.notes || [j.note || 'Note'];
    const data = j.cents_offsets || [j.cents_offset || 0];
    if (chartObj) chartObj.destroy();
    chartObj = new Chart($('#intonation-chart')[0], {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Cents Offset', data }] },
      options: { responsive: true, scales: { y: { beginAtZero: true, min: -50, max: 50 } } }
    });
    $('#intonation-note').text(`Most Recent: ${labels[labels.length-1]} (${data[data.length-1]} cents)`);
  }

  loadChart();
};
