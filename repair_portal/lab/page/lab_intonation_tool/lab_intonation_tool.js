// File Header Template
// Relative Path: repair_portal/lab/page/lab_intonation_tool/lab_intonation_tool.js
// Last Updated: 2025-07-25
// Version: v1.2
// Purpose: Frontend controller for Lab Intonation Tool — supports session type logic, mic access, pitch analysis, and impedance entry

frappe.pages['lab_intonation_tool'].on_page_load = async (wrapper) => {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Lab Intonation Tool",
    single_column: true,
  });

  let sessionType = null;
  let audioContext, analyser, canvasCtx, canvasEl;

  page.set_primary_action('Start Session', async () => {
    sessionType = $('#session-type').val();
    const instrument = $('#instrument-id').val();

    if (!sessionType || !instrument) {
      frappe.msgprint(__('Please select a session type and instrument.'));
      return;
    }

    // Save session
    frappe.call({
      method: 'frappe.client.insert',
      args: {
        doc: {
          doctype: 'Lab Intonation Session',
          instrument: instrument,
          session_type: sessionType
        }
      },
      callback: (r) => {
        if (!r.exc) {
          frappe.msgprint(__(`Session created: ${r.message.name}`));
        }
      }
    });

    if (sessionType === 'Tone' || sessionType === 'Full Sweep') {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);
        drawTone();
        frappe.msgprint(__('Microphone access granted'));
      } catch (err) {
        frappe.msgprint(__(`Microphone access denied: ${err.message}`));
      }
    }

    if (sessionType === 'Impedance' || sessionType === 'Full Sweep') {
      $('#impedance-entry').removeClass('d-none');
    }
  });

  function drawTone() {
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
      requestAnimationFrame(draw);
      analyser.getByteTimeDomainData(dataArray);

      canvasCtx.fillStyle = 'white';
      canvasCtx.fillRect(0, 0, canvasEl.width, canvasEl.height);
      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = 'blue';
      canvasCtx.beginPath();

      const sliceWidth = canvasEl.width / bufferLength;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvasEl.height) / 2;
        if (i === 0) {
          canvasCtx.moveTo(x, y);
        } else {
          canvasCtx.lineTo(x, y);
        }
        x += sliceWidth;
      }
      canvasCtx.lineTo(canvasEl.width, canvasEl.height / 2);
      canvasCtx.stroke();
    }
    draw();
  }

  $(wrapper).html(`
    <div class="p-3">
      <p>Use this tool to measure intonation across an instrument's range. You'll be guided through the process and results will be stored in a session document.</p>
      <p><b>Note:</b> Ensure microphone access is enabled in your browser.</p>
      <div class="form-group">
        <label for="instrument-id">Instrument</label>
        <input type="text" id="instrument-id" class="form-control" placeholder="Instrument Name or ID" />
      </div>
      <div class="form-group">
        <label for="session-type">Session Type</label>
        <select id="session-type" class="form-control">
          <option value="">-- Select --</option>
          <option value="Tone">Tone</option>
          <option value="Impedance">Impedance</option>
          <option value="Full Sweep">Full Sweep</option>
        </select>
      </div>
      <canvas id="tone-canvas" width="600" height="100" class="border my-3"></canvas>
      <div id="impedance-entry" class="d-none">
        <label for="impedance-value">Enter Impedance Reading:</label>
        <input type="number" id="impedance-value" class="form-control" step="0.01" placeholder="Ohms" />
      </div>
    </div>
  `);

  canvasEl = document.getElementById('tone-canvas');
  canvasCtx = canvasEl.getContext('2d');
};