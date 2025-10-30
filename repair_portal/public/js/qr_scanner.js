(function () {
  const detectorSupported = typeof window.BarcodeDetector !== 'undefined';

  async function scanWithDetector(detector, video, onSuccess, status) {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    video.srcObject = stream;
    await video.play();
    status.textContent = __('Scanning...');

    const interval = setInterval(async () => {
      try {
        const codes = await detector.detect(video);
        if (codes && codes.length) {
          clearInterval(interval);
          stream.getTracks().forEach((track) => track.stop());
          onSuccess(codes[0].rawValue);
        }
      } catch (error) {
        console.warn('Detector error', error);
      }
    }, 350);
  }

  async function resolveCode(resolverUrl, code, status) {
    status.textContent = __('Resolving {0}...', [code]);
    try {
      const response = await fetch(resolverUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': frappe.csrf_token
        },
        body: JSON.stringify({ code })
      });
      const data = await response.json();
      if (data.exc) {
        frappe.msgprint({ message: data.exc, indicator: 'red' });
        status.textContent = __('Unable to resolve the code.');
        return;
      }
      status.textContent = __('Opening {0}...', [data.message.route]);
      window.location.href = data.message.route;
    } catch (error) {
      console.error(error);
      status.textContent = __('Resolution failed. Check the console for details.');
    }
  }

  function attachManualHandler(input, button, resolver, status) {
    button.addEventListener('click', () => {
      const value = input.value.trim();
      if (!value) {
        frappe.msgprint(__('Enter a barcode value first.'));
        return;
      }
      resolveCode(resolver, value, status);
    });
  }

  window.repairPortalScan = {
    init({ video, overlay, status, manualInput, manualButton, startButton, resolver }) {
      if (!video || !status) {
        console.warn('Scanner missing DOM elements');
        return;
      }

      attachManualHandler(manualInput, manualButton, resolver, status);

      startButton.addEventListener('click', async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          frappe.msgprint(__('Camera access is not available in this browser.'));
          return;
        }
        overlay.style.opacity = '0';
        status.textContent = __('Requesting camera access...');
        try {
          if (detectorSupported) {
            const detector = new BarcodeDetector({ formats: ['qr_code', 'code_128', 'code_39'] });
            await scanWithDetector(detector, video, (value) => resolveCode(resolver, value, status), status);
          } else {
            status.textContent = __('Camera scanning is not supported. Use manual entry.');
          }
        } catch (error) {
          console.error(error);
          status.textContent = __('Camera initialisation failed.');
        }
      });
    }
  };
})();
