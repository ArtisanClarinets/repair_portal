// File: repair_portal/public/js/note_autocorrect.js
// Purpose: Live-typing autocorrect for ALL musical accidentals (double-flat → double-sharp)
// App: repair_portal on Frappe/ERPNext v15
// Version: 1.0.0
// Creation Date: 2025-07-28
// Last Updated: 2025-07-28

(function() {
  // ASCII → Unicode map for accidentals on A–G
  const ACCIDENTAL_MAP = {
    // Double-flats (𝄫 U+1D12B) :contentReference[oaicite:2]{index=2}
    'Abb': 'A𝄫',
    'Bbb': 'B𝄫',
    'Cbb': 'C𝄫',
    'Dbb': 'D𝄫',
    'Ebb': 'E𝄫',
    'Fbb': 'F𝄫',
    'Gbb': 'G𝄫',
    // Flats (♭ U+266D)
    'Ab': 'A♭',
    'Bb': 'B♭',
    'Cb': 'C♭',
    'Db': 'D♭',
    'Eb': 'E♭',
    'Fb': 'F♭',
    'Gb': 'G♭',
    // Naturals (♮ U+266E)
    'An': 'A♮',
    'Bn': 'B♮',
    'Cn': 'C♮',
    'Dn': 'D♮',
    'En': 'E♮',
    'Fn': 'F♮',
    'Gn': 'G♮',
    // Sharps (♯ U+266F)
    'A#': 'A♯',
    'B#': 'B♯',
    'C#': 'C♯',
    'D#': 'D♯',
    'E#': 'E♯',
    'F#': 'F♯',
    'G#': 'G♯',
    // Double-sharps (𝄪 U+1D12A) :contentReference[oaicite:3]{index=3}
    'A##': 'A𝄪',
    'B##': 'B𝄪',
    'C##': 'C𝄪',
    'D##': 'D𝄪',
    'E##': 'E𝄪',
    'F##': 'F𝄪',
    'G##': 'G𝄪'
  };

  // Build regex: \b(Abb|A##|...|Gbb)\b
  const pattern = new RegExp('\\b('
    + Object.keys(ACCIDENTAL_MAP)
        // sort longer keys first so 'A##' matches before 'A#'
        .sort((a, b) => b.length - a.length)
        .join('|')
    + ')\\b', 'g');

  function replaceAccidentals(text) {
    return text.replace(pattern, m => ACCIDENTAL_MAP[m] || m);
  }

  function attachField(field) {
    if (field._note_autocorrect_attached) return;
    field._note_autocorrect_attached = true;
    field.addEventListener('input', e => {
      const el = e.target;
      const [start, end] = [el.selectionStart, el.selectionEnd];
      const newVal = replaceAccidentals(el.value);
      if (newVal !== el.value) {
        el.value = newVal;
        el.setSelectionRange(start, end);
      }
    });
  }

  // Hook into form fields
  frappe.ui.form.on('*', {
    refresh(frm) {
      setTimeout(() => {
        frm.wrapper
          .find('input[type="text"], textarea')
          .each((_, el) => attachField(el));
      }, 50);
    }
  });

  // Hook into ListView inline editing
  frappe.listview_settings['*'] = {
    onload(listview) {
      listview.page.body.on(
        'input',
        'input[data-fieldname], textarea[data-fieldname]',
        e => {
          e.target.value = replaceAccidentals(e.target.value);
        }
      );
    }
  };
})();
