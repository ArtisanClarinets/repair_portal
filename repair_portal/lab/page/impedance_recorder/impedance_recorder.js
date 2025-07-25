frappe.pages['impedance_recorder'].on_page_load = async (wrapper) => {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Impedance Diagnostics",
    single_column: true,
  });

  // Main container with card layout
  const $container = $(`<div class="impedance-container"></div>`).appendTo(page.body);
  
  // ===== INSTRUMENT SELECTION CARD =====
  const $cardInstr = $(`
    <div class="card impedance-card mb-4">
      <div class="card-header">
        <h5 class="card-title">Instrument Configuration</h5>
      </div>
      <div class="card-body">
        <div class="form-group">
          <label class="form-label text-muted small mb-1" for="instr-select">
            SELECT INSTRUMENT
          </label>
          <div class="input-group">
            <select class="form-select form-control-lg" id="instr-select" aria-label="Instrument" required>
              <option value="">-- Select Instrument --</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  `).appendTo($container);

  const $instrument = $cardInstr.find('#instr-select');

  // Populate instrument dropdown
  frappe.call('repair_portal.lab.api.get_instruments', {}).then(r => {
    (r.message || []).forEach(i => {
      $instrument.append(
        `<option value="${i.name}">${i.serial_number ? i.serial_number : i.name}${i.brand || i.model ? ' - ' + [i.brand, i.model].filter(Boolean).join(' ') : ''}</option>`
      );
    });
  });

  // ===== VISUALIZATION CARD =====
  const $cardVisual = $(`
    <div class="card impedance-card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="card-title">Waveform Analysis</h5>
        <span class="badge bg-secondary" id="status-badge">IDLE</span>
      </div>
      <div class="card-body">
        <div class="impedance-visualization">
          <div class="waveform-container">
            <canvas width="600" height="160" id="waveform-canvas" aria-label="Recording waveform"></canvas>
          </div>
          <div class="mt-3 d-flex justify-content-center">
            <div class="progress" style="height: 6px; width: 80%">
              <div id="progress-bar" class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
          </div>
          <div class="text-center mt-2 text-muted small" id="timer-display">00:00</div>
        </div>
      </div>
    </div>
  `).appendTo($container);

  const $canvas = $cardVisual.find('#waveform-canvas');
  const ctx = $canvas[0].getContext("2d");
  const $statusBadge = $cardVisual.find('#status-badge');

  // ===== CONTROLS CARD =====
  const $cardControls = $(`
    <div class="card impedance-card">
      <div class="card-body">
        <div class="d-flex justify-content-center align-items-center gap-3">
          <button class="btn btn-lg btn-success rounded-pill px-4" id="btn-start">
            <span class="material-icons-outlined me-2">play_arrow</span>Start Test
          </button>
          <button class="btn btn-lg btn-danger rounded-pill px-4" id="btn-stop" disabled>
            <span class="material-icons-outlined me-2">stop</span>Stop
          </button>
        </div>
        <div class="mt-4 text-center">
          <div class="spinner-border text-primary d-none" role="status" id="processing-spinner">
            <span class="visually-hidden">Processing...</span>
          </div>
          <p class="text-muted mt-3 small" id="privacy-note">
            <span class="material-icons-outlined align-middle" style="font-size: 1rem">lock</span>
            Audio is used exclusively for diagnostics and stored securely
          </p>
        </div>
      </div>
    </div>
  `).appendTo($container);

  const $start = $cardControls.find('#btn-start');
  const $stop = $cardControls.find('#btn-stop');
  const $spinner = $cardControls.find('#processing-spinner');
  const $progressBar = $cardVisual.find('#progress-bar');
  const $timer = $cardVisual.find('#timer-display');

  // ===== STATE MANAGEMENT =====
  let mediaRecorder, audioCtx, analyser, dataArray, sourceNode, stream;
  let recorderChunks = [], running = false, animationId = null;
  let recordingTimer = null, elapsedSeconds = 0;

  // ===== ACCESSIBILITY =====
  $start.attr('aria-label', 'Start recording');
  $stop.attr('aria-label', 'Stop recording');
  $instrument.attr('tabindex', '0');

  // ===== START RECORDING =====
  $start.on('click', async () => {
    if (running) return;
    if (!$instrument.val()) {
      frappe.msgprint("Please select an instrument.");
      return;
    }
    
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (_err) {
      $statusBadge.text("ACCESS DENIED").removeClass().addClass('badge bg-danger');
      frappe.msgprint("Microphone access denied. Please allow microphone permissions.");
      return;
    }
    
    running = true;
    recorderChunks = [];
    elapsedSeconds = 0;
    $statusBadge.text("RECORDING").removeClass().addClass('badge bg-danger');
    $start.prop('disabled', true);
    $stop.prop('disabled', false);
    $progressBar.css('width', '0%');
    $timer.text('00:00');
    $spinner.addClass('d-none');

    // Audio setup
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    sourceNode = audioCtx.createMediaStreamSource(stream);
    sourceNode.connect(analyser);

    analyser.fftSize = 1024;
    dataArray = new Uint8Array(analyser.frequencyBinCount);

    drawWaveform();

    // Start media recording
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRecorder.ondataavailable = (e) => recorderChunks.push(e.data);
    mediaRecorder.start();

    // Play chirp stimulus
    playChirp(audioCtx);

    // Start recording timer
    recordingTimer = setInterval(() => {
      elapsedSeconds++;
      $timer.text(`${String(Math.floor(elapsedSeconds/60)).padStart(2, '0')}:${String(elapsedSeconds%60).padStart(2, '0')}`);
      $progressBar.css('width', `${(elapsedSeconds/3)*100}%`);
    }, 1000);

    // Auto-stop after 3s (2s chirp + 1s buffer)
    setTimeout(() => stopTest('auto'), 3000);
  });

  // ===== STOP RECORDING =====
  $stop.on('click', () => stopTest('manual'));

  async function stopTest(source) {
    if (!running) return;
    running = false;
    clearInterval(recordingTimer);
    $statusBadge.text("PROCESSING").removeClass().addClass('badge bg-warning text-dark');
    $spinner.removeClass('d-none');
    $stop.prop('disabled', true);

    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    if (audioCtx && audioCtx.state !== "closed") {
      audioCtx.close();
    }
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }

    // Process recording
    setTimeout(async () => {
      const blob = new Blob(recorderChunks, { type: "audio/webm" });
      const base64 = await blobToBase64(blob);

      frappe.call("repair_portal.lab.api.save_impedance_snapshot", {
        instrument: $instrument.val(),
        recording_base64: base64,
        filename: `impedance_${frappe.datetime.now_datetime()}.webm`,
      })
      .then(r => {
        $statusBadge.text("COMPLETE").removeClass().addClass('badge bg-success');
        $spinner.addClass('d-none');
        frappe.msgprint({
          title: __('Recording Saved'),
          indicator: 'green',
          message: __(`Impedance snapshot saved as <b>${r.message.name}</b>`)
        });
      })
      .catch(err => {
        $statusBadge.text("ERROR").removeClass().addClass('badge bg-danger');
        $spinner.addClass('d-none');
        frappe.msgprint({
          title: __('Save Failed'),
          indicator: 'red',
          message: __('Error saving recording. Please try again.')
        });
        frappe.log_error(err, "Impedance Recorder Save Failed");
      });
    }, 250);
  }

  // ===== CHIRP SIGNAL =====
  function playChirp(audioCtx) {
    const duration = 2;
    const sampleRate = audioCtx.sampleRate;
    const buffer = audioCtx.createBuffer(1, duration * sampleRate, sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i++) {
      const t = i / sampleRate;
      data[i] = Math.sin(2 * Math.PI * (100 + (5000 - 100) * (t / duration)) * t);
    }
    const src = audioCtx.createBufferSource();
    src.buffer = buffer;
    src.connect(audioCtx.destination);
    src.start();
  }

  // ===== WAVEFORM VISUALIZATION =====
  function drawWaveform() {
    if (!analyser) return;
    analyser.getByteTimeDomainData(dataArray);
    
    // Clear canvas with gradient background
    const gradient = ctx.createLinearGradient(0, 0, $canvas[0].width, 0);
    gradient.addColorStop(0, '#f8f9fa');
    gradient.addColorStop(1, '#e9ecef');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, $canvas[0].width, $canvas[0].height);
    
    // Draw center line
    ctx.beginPath();
    ctx.moveTo(0, $canvas[0].height/2);
    ctx.lineTo($canvas[0].width, $canvas[0].height/2);
    ctx.strokeStyle = '#dee2e6';
    ctx.lineWidth = 1;
    ctx.stroke();
    
    // Draw waveform
    ctx.beginPath();
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    for (let i = 0; i < dataArray.length; i++) {
      const x = (i / dataArray.length) * $canvas[0].width;
      const y = ((dataArray[i] - 128) / 128) * 60 + $canvas[0].height / 2;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = "#0d6efd";
    ctx.lineWidth = 2.5;
    ctx.stroke();
    
    animationId = requestAnimationFrame(drawWaveform);
  }

  // ===== UTILITIES =====
  function blobToBase64(blob) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(",")[1]);
      reader.readAsDataURL(blob);
    });
  }

  // Add custom styles
  $('<style>')
    .text(`
      .impedance-container {
        max-width: 800px;
        margin: 0 auto;
      }
      .impedance-card {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: none;
      }
      .card-header {
        background: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
        padding: 1rem 1.5rem;
      }
      .waveform-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
      }
      #waveform-canvas {
        display: block;
        width: 100%;
        border-radius: 6px;
        background: #fff;
      }
      .btn-lg {
        padding: 0.5rem 1.5rem;
        font-size: 1.1rem;
      }
      .badge {
        font-size: 0.85rem;
        font-weight: 500;
        padding: 0.35em 0.65em;
      }
    `)
    .appendTo('head');
};
