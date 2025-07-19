// Relative Path: repair_portal/public/js/recording_analyzer.js
// Last Updated: 2025-07-15
// Purpose: UI for collecting audio and running lab analysis via Lab API

frappe.ready(() => {
  let audioBlob = null;
  let intonationChart = null, toneChart = null, leakChart = null, impChart = null;

  const makeAudioTools = () => {
    const wrapper = $('<div style="margin: 20px"></div>').appendTo($('.page-content'));

    wrapper.append(`
      <p><button class="btn btn-primary" id="start-record">Start Recording</button>
         <button class="btn btn-danger" id="stop-record" disabled>Stop Recording</button></p>
      <audio id="audio-playback" controls style="display:none;"></audio>
      <div class="mt-3">
        <button class="btn btn-success" id="analyze-imp">Analyze Impedance</button>
        <button class="btn btn-info" id="analyze-intonation">Analyze Intonation</button>
        <button class="btn btn-warning" id="analyze-tone">Analyze Tone Fitness</button>
        <button class="btn btn-secondary" id="analyze-leak">Analyze Leak Test</button>
      </div>

      <div class="mt-5">
        <h5>🎶 Intonation <select id="mode-select">
          <option value="recent">Most Recent</option>
          <option value="last3">Last 3</option>
        </select></h5>
        <canvas id="intonation-chart" height="100"></canvas>
        <p id="intonation-note"></p>

        <h5 class="mt-4">💪 Tone Fitness</h5>
        <canvas id="tone-chart" height="100"></canvas>

        <h5 class="mt-4">💧 Leak Test</h5>
        <canvas id="leak-chart" height="100"></canvas>

        <h5 class="mt-4">📈 Impedance Spectrum</h5>
        <canvas id="imp-chart" height="100"></canvas>
      </div>
    `);

    setupHandlers();
  };

  const setupHandlers = () => {
    let mediaRecorder;
    let audioChunks = [];

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

    $('#mode-select').on('change', () => refreshIntonationChart($('#mode-select').val()));

    $('#analyze-intonation').on('click', async () => {
      const args = await getAudioArgs();
      frappe.call({
        method: 'repair_portal.lab.api.save_intonation_session',
        type: 'POST', args: { ...args },
        callback: async r => {
          if (!r.exc) {
            frappe.msgprint(`Intonation Session saved: ${r.message.name}`);
            await refreshIntonationChart($('#mode-select').val());
          }
        }
      });
    });

    $('#analyze-tone').on('click', async () => {
      const args = await getAudioArgs();
      frappe.call({
        method: 'repair_portal.lab.api.save_tone_fitness',
        type: 'POST', args: { ...args },
        callback: async r => {
          if (!r.exc) {
            frappe.msgprint(`Tone Fitness saved: ${r.message.name}`);
            await refreshToneChart();
          }
        }
      });
    });

    $('#analyze-leak').on('click', async () => {
      const args = await getAudioArgs();
      frappe.call({
        method: 'repair_portal.lab.api.save_leak_test',
        type: 'POST', args: { ...args },
        callback: async r => {
          if (!r.exc) {
            frappe.msgprint(`Leak Test saved: ${r.message.name}`);
            await refreshLeakChart();
          }
        }
      });
    });

    $('#analyze-imp').on('click', async () => {
      const args = await getAudioArgs();
      frappe.call({
        method: 'repair_portal.lab.api.save_impedance_snapshot',
        type: 'POST', args: { ...args, raw_data: '{}' },
        callback: async r => {
          if (!r.exc) {
            frappe.msgprint(`Impedance Snapshot saved: ${r.message.name}`);
            await refreshImpedanceChart();
          }
        }
      });
    });
  };

  const getAudioArgs = async () => {
    if (!audioBlob) throw new Error('Please record audio first');
    const base64 = await new Promise(res => {
      const reader = new FileReader();
      reader.onloadend = () => res(reader.result);
      reader.readAsDataURL(audioBlob);
    });
    return { recording_base64: base64.split(',')[1], filename: `rec_${Date.now()}.wav` };
  };

  const refreshIntonationChart = async (mode = 'recent') => {
    const sessions = await frappe.db.get_list('Intonation Session', {
      limit: mode === 'last3' ? 3 : 1,
      order_by: 'creation desc', fields: ['json_data']
    });
    const labels = [], data = [];
    sessions.reverse().forEach((s, i) => {
      const j = JSON.parse(s.json_data || '{}');
      labels.push(j.note || `#${i + 1}`);
      data.push(j.cents_offset || 0);
    });
    if (intonationChart) intonationChart.destroy();
    intonationChart = new Chart($('#intonation-chart')[0], {
      type: 'bar', data: { labels, datasets: [{ label: 'Cents Offset', data }] },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
    $('#intonation-note').text(`Note: ${labels[labels.length - 1]} (${data[data.length - 1]} cents)`);
  };

  const refreshToneChart = async () => {
    const entries = await frappe.db.get_list('Tone Fitness', {
      limit: 3, order_by: 'creation desc', fields: ['json_data']
    });
    const datasets = entries.reverse().map((e, i) => {
      const d = JSON.parse(e.json_data || '{}');
      return {
        label: `Session ${i + 1}`,
        data: [d.centroid || 0, d.spread || 0],
        backgroundColor: `rgba(100,100,${100 + i * 50},0.6)`
      };
    });
    if (toneChart) toneChart.destroy();
    toneChart = new Chart($('#tone-chart')[0], {
      type: 'bar',
      data: { labels: ['Centroid', 'Spread'], datasets },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
  };

  const refreshLeakChart = async () => {
    const leaks = await frappe.db.get_list('Leak Test', { limit: 1, order_by: 'creation desc' });
    if (!leaks.length) return;
    const doc = await frappe.db.get_doc('Leak Test', leaks[0].name);
    const labels = doc.readings.map(r => r.tone_hole);
    const data = doc.readings.map(r => r.leak_score);
    if (leakChart) leakChart.destroy();
    leakChart = new Chart($('#leak-chart')[0], {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Leak Score', data }] },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
  };

  const refreshImpedanceChart = async () => {
    const entries = await frappe.db.get_list('Impedance Snapshot', {
      limit: 3, order_by: 'creation desc', fields: ['json_data']
    });
    const datasets = entries.reverse().map((e, i) => {
      const points = JSON.parse(e.json_data || '[]');
      return {
        label: `Snapshot ${i + 1}`,
        data: points.map(p => ({ x: p.frequency, y: p.amplitude })),
        showLine: true,
        fill: false
      };
    });
    if (impChart) impChart.destroy();
    impChart = new Chart($('#imp-chart')[0], {
      type: 'scatter',
      data: { datasets },
      options: {
        responsive: true,
        scales: {
          x: { type: 'linear', title: { display: true, text: 'Frequency (Hz)' } },
          y: { title: { display: true, text: 'Amplitude' } }
        },
        plugins: {
          annotation: {
            annotations: [392, 440, 494].map(f => ({
              type: 'line', xMin: f, xMax: f, borderColor: 'red', borderDash: [6, 6], label: {
                content: `f=${f}`, enabled: true, position: 'top'
              }
            }))
          }
        }
      }
    });
  };

  makeAudioTools();
  refreshIntonationChart();
  refreshToneChart();
  refreshLeakChart();
  refreshImpedanceChart();
});
