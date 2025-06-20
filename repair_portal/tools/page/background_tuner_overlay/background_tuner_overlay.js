frappe.pages['background_tuner_overlay'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Background Tuner Overlay',
        single_column: true
    });

    page.set_primary_action('Start Tuner', () => {
        if (typeof initTuner === 'function') initTuner();
    });

    $(wrapper).find('.layout-main-section').html(`
        <div id="tuner-output" style="text-align:center;padding-top:2rem;">
            <h2>Frequency: <span id="freq">--</span> Hz</h2>
            <h3>Note: <span id="note">--</span></h3>
        </div>
    `);

    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/pitchy@latest/dist/pitchy.min.js';
    script.onload = () => {
        initTuner = async function () {
            const audioCtx = new AudioContext();
            const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
            const source = audioCtx.createMediaStreamSource(mic);
            const analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            source.connect(analyser);
            const buffer = new Float32Array(analyser.fftSize);

            function detectPitch() {
                analyser.getFloatTimeDomainData(buffer);
                const [freq, clarity] = pitchy.findPitch(buffer, audioCtx.sampleRate);
                if (clarity > 0.95) {
                    document.getElementById('freq').textContent = freq.toFixed(2);
                    document.getElementById('note').textContent = pitchToNote(freq);
                }
                requestAnimationFrame(detectPitch);
            }

            detectPitch();
        }
    };
    document.body.appendChild(script);
};

function pitchToNote(freq) {
    const A4 = 440;
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const noteNum = 12 * (Math.log(freq / A4) / Math.log(2));
    const idx = Math.round(noteNum) + 57;
    return noteNames[idx % 12] + Math.floor(idx / 12);
}