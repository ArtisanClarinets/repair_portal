/* Clarinet Visual Editor (Frappe v15)
 * Features:
 * - Drag tone holes along X with grid snapping
 * - Bore outline from samples
 * - Rulers & section markers (barrel/upper/lower/bell)
 * - Undo/redo, autosave toggle
 * - JSON/SVG/PNG export, persistent DocType storage
 */

frappe.pages['clarinet-editor'].on_page_load = async function(wrapper) {
  const page = frappe.ui.make_app_page({ parent: wrapper, title: 'Clarinet Editor', single_column: true });
  const q = new URLSearchParams(window.location.search);
  const prototype = q.get('prototype');

  if (!prototype) {
    $(page.body).html(`<div class="text-danger p-3">Missing prototype. Open this page via the Prototype form button.</div>`);
    return;
  }

  // Skeleton UI
  $(page.body).empty().append(`
    <div class="clarinet-editor p-3">
      <div class="d-flex gap-3 flex-wrap">
        <div class="editor-side">
          <div class="mb-2"><b>Prototype:</b> <span id="proto_name"></span></div>

          <div class="mb-2">
            <label class="form-label">Title</label>
            <input type="text" id="title" class="form-control form-control-sm"/>
          </div>
          <div class="mb-2">
            <label class="form-label">Clarinet Type</label>
            <select id="clarinet_type" class="form-select form-select-sm">
              <option>B♭</option><option>A</option><option>E♭</option><option>C</option>
              <option>Bass (Low E♭)</option><option>Bass (Low C)</option>
            </select>
          </div>

          <div class="row g-2 mb-2">
            <div class="col-6">
              <label class="form-label">Pixels / mm (zoom)</label>
              <input type="number" id="px_per_mm" step="0.1" value="1.2" class="form-control form-control-sm"/>
            </div>
            <div class="col-6">
              <label class="form-label">Grid (mm)</label>
              <input type="number" id="grid_mm" step="0.1" class="form-control form-control-sm"/>
            </div>
          </div>

          <div class="row g-2 mb-2">
            <div class="col-6">
              <label class="form-label">Wall Thickness (mm)</label>
              <input type="number" id="wall_thickness_mm" step="0.1" class="form-control form-control-sm"/>
            </div>
            <div class="col-6">
              <label class="form-label">Autosave</label>
              <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" id="autosave_toggle">
                <label class="form-check-label small" for="autosave_toggle">Every 60s</label>
              </div>
            </div>
          </div>

          <div class="mb-2"><b>Section Lengths (mm)</b></div>
          <div class="row g-2 mb-2">
            <div class="col-6"><label class="form-label">Barrel</label><input type="number" id="barrel_length_mm" step="0.1" class="form-control form-control-sm"/></div>
            <div class="col-6"><label class="form-label">Upper Joint</label><input type="number" id="upper_joint_length_mm" step="0.1" class="form-control form-control-sm"/></div>
          </div>
          <div class="row g-2 mb-2">
            <div class="col-6"><label class="form-label">Tenon Gap</label><input type="number" id="tenon_gap_mm" step="0.1" class="form-control form-control-sm"/></div>
            <div class="col-6"><label class="form-label">Lower Joint</label><input type="number" id="lower_joint_length_mm" step="0.1" class="form-control form-control-sm"/></div>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-6"><label class="form-label">Bell</label><input type="number" id="bell_length_mm" step="0.1" class="form-control form-control-sm"/></div>
            <div class="col-6"><label class="form-label">Overall</label><input type="number" id="overall_length_mm" step="0.1" class="form-control form-control-sm"/></div>
          </div>

          <div class="d-flex gap-2 mb-3">
            <button id="undo" class="btn btn-outline-secondary btn-sm">Undo</button>
            <button id="redo" class="btn btn-outline-secondary btn-sm">Redo</button>
            <button id="save" class="btn btn-primary btn-sm">Save</button>
          </div>

          <hr/>
          <div class="d-flex justify-content-between align-items-center">
            <b>Bore Samples</b>
            <div>
              <button id="add_bore" class="btn btn-sm btn-outline-secondary">Add</button>
              <button id="clear_bore" class="btn btn-sm btn-outline-danger">Clear</button>
            </div>
          </div>
          <div id="bore_list" class="mt-2 small"></div>

          <hr/>
          <div class="d-flex justify-content-between align-items-center">
            <b>Tone Holes</b>
            <div>
              <button id="add_hole" class="btn btn-sm btn-outline-secondary">Add</button>
              <button id="clear_holes" class="btn btn-sm btn-outline-danger">Clear</button>
            </div>
          </div>
          <div id="holes_list" class="mt-2 small"></div>

          <hr/>
          <div class="d-grid gap-2">
            <button id="export_json" class="btn btn-outline-primary btn-sm">Export JSON</button>
            <input type="file" id="import_json" accept="application/json" class="form-control form-control-sm"/>
            <button id="export_svg" class="btn btn-outline-secondary btn-sm">Export SVG (attach)</button>
            <button id="export_png" class="btn btn-outline-secondary btn-sm">Export PNG (attach)</button>
            <button id="back" class="btn btn-outline-dark btn-sm">Back to Prototype</button>
          </div>
        </div>

        <div class="editor-canvas">
          <svg id="clarinet_svg" class="clarinet-svg" xmlns="http://www.w3.org/2000/svg"></svg>
        </div>
      </div>
    </div>
  `);

  $('#proto_name').text(prototype);

  // ---- State, Undo/Redo ----
  const S = {
    title: "", clarinet_type: "B♭",
    overall_length_mm: 600, barrel_length_mm: 66,
    upper_joint_length_mm: 230, tenon_gap_mm: 2.0,
    lower_joint_length_mm: 250, bell_length_mm: 110,
    wall_thickness_mm: 2.5, grid_mm: 5.0,
    px_per_mm: 1.2, autosave: false,
    bore_segments: [], tone_holes: []
  };
  const undoStack = []; const redoStack = [];
  const maxHist = 50;
  const pushHist = () => { undoStack.push(JSON.stringify(S)); if (undoStack.length>maxHist) undoStack.shift(); redoStack.length=0; };

  // ---- Load from server ----
  const load = await frappe.call({ method: 'repair_portal.prototyping.clarinet_api.load_design', args: { prototype }});
  Object.assign(S, load.message);
  // Defaults that aren't persisted
  S.px_per_mm = 1.2;
  S.autosave = false;

  // Patch form fields
  $('#title').val(S.title);
  $('#clarinet_type').val(S.clarinet_type);
  $('#grid_mm').val(S.grid_mm);
  $('#wall_thickness_mm').val(S.wall_thickness_mm);
  $('#barrel_length_mm').val(S.barrel_length_mm);
  $('#upper_joint_length_mm').val(S.upper_joint_length_mm);
  $('#tenon_gap_mm').val(S.tenon_gap_mm);
  $('#lower_joint_length_mm').val(S.lower_joint_length_mm);
  $('#bell_length_mm').val(S.bell_length_mm);
  $('#overall_length_mm').val(S.overall_length_mm);
  $('#px_per_mm').val(S.px_per_mm);

  // ---- Helpers ----
  const svg = document.getElementById('clarinet_svg');

  function mm2px(x) { return x * S.px_per_mm + 40; } // margin
  function px2mm(px) { return (px - 40) / S.px_per_mm; }
  function centerY() { return 150; }
  function sizeCanvas() {
    const W = Math.max(1000, S.overall_length_mm * S.px_per_mm + 80);
    const H = 320;
    svg.setAttribute('width', W);
    svg.setAttribute('height', H);
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  }

  function snapMM(xmm) {
    const g = Math.max(0.1, S.grid_mm);
    return Math.round(xmm / g) * g;
  }

  // Section markers (computed from lengths)
  function sectionPositions() {
    const x0 = 0;
    const xBarrelEnd = S.barrel_length_mm;
    const xUpperEnd  = xBarrelEnd + S.upper_joint_length_mm;
    const xLowerStart= xUpperEnd + S.tenon_gap_mm;
    const xLowerEnd  = xLowerStart + S.lower_joint_length_mm;
    const xBellEnd   = xLowerEnd + S.bell_length_mm;
    return { x0, xBarrelEnd, xUpperEnd, xLowerStart, xLowerEnd, xBellEnd };
  }

  function drawRuler() {
    let g = svg.querySelector('#ruler'); if (g) g.remove();
    g = document.createElementNS('http://www.w3.org/2000/svg','g'); g.setAttribute('id','ruler'); svg.appendChild(g);
    const y = centerY() - 120;
    const tickMajor = 6, tickMinor = 3;
    const step = Math.max(1, S.grid_mm);
    for (let xmm=0; xmm<=S.overall_length_mm; xmm+=step) {
      const x = mm2px(xmm);
      const line = document.createElementNS('http://www.w3.org/2000/svg','line');
      line.setAttribute('x1', x); line.setAttribute('x2', x);
      const isMajor = (Math.round(xmm) % (step*2) === 0);
      line.setAttribute('y1', y); line.setAttribute('y2', y + (isMajor? tickMajor: tickMinor));
      line.setAttribute('stroke','gray');
      g.appendChild(line);
      if (isMajor) {
        const t = document.createElementNS('http://www.w3.org/2000/svg','text');
        t.setAttribute('x', x); t.setAttribute('y', y-2);
        t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','9');
        t.textContent = `${Math.round(xmm)}`;
        g.appendChild(t);
      }
    }
  }

  function drawAxisAndSections() {
    let g = svg.querySelector('#axis'); if (g) g.remove();
    g = document.createElementNS('http://www.w3.org/2000/svg','g'); g.setAttribute('id','axis'); svg.appendChild(g);

    const y = centerY();
    const axis = document.createElementNS('http://www.w3.org/2000/svg','line');
    axis.setAttribute('x1', mm2px(0)); axis.setAttribute('y1', y);
    axis.setAttribute('x2', mm2px(S.overall_length_mm)); axis.setAttribute('y2', y);
    axis.setAttribute('stroke','gray'); axis.setAttribute('stroke-dasharray','4 4');
    g.appendChild(axis);

    const {xBarrelEnd,xUpperEnd,xLowerStart,xLowerEnd,xBellEnd} = sectionPositions();
    const markers = [
      {x: xBarrelEnd, color:'blue', label:'Barrel End'},
      {x: xUpperEnd, color:'green', label:'Upper End'},
      {x: xLowerStart, color:'purple', label:'Tenon Gap'},
      {x: xLowerEnd, color:'orange', label:'Lower End'},
      {x: xBellEnd, color:'black', label:'Bell End'}
    ];
    markers.forEach(m=>{
      const L = document.createElementNS('http://www.w3.org/2000/svg','line');
      L.setAttribute('x1', mm2px(m.x)); L.setAttribute('y1', y-90);
      L.setAttribute('x2', mm2px(m.x)); L.setAttribute('y2', y+90);
      L.setAttribute('stroke', m.color);
      g.appendChild(L);
      const T = document.createElementNS('http://www.w3.org/2000/svg','text');
      T.setAttribute('x', mm2px(m.x)); T.setAttribute('y', y-96);
      T.setAttribute('text-anchor','middle'); T.setAttribute('font-size','10'); T.textContent = m.label;
      g.appendChild(T);
    });
  }

  function boreY(bore_mm) {
    const y = centerY();
    const r = (bore_mm/2)*S.px_per_mm;
    return [y-r, y+r];
  }

  function drawBore() {
    if (!S.bore_segments.length) { const old = svg.querySelector('#bore'); if (old) old.remove(); return; }
    const sorted = [...S.bore_segments].sort((a,b)=>a.x_mm-b.x_mm);
    const topPts=[]; const botPts=[];
    sorted.forEach(s=>{
      const x=mm2px(s.x_mm); const [yt,yb]=boreY(s.bore_mm);
      topPts.push(`${x},${yt}`); botPts.push(`${x},${yb}`);
    });
    const pts = topPts.concat(botPts.reverse()).join(' ');
    let poly = svg.querySelector('#bore'); if (!poly) {
      poly = document.createElementNS('http://www.w3.org/2000/svg','polygon');
      poly.setAttribute('id','bore'); svg.appendChild(poly);
    }
    poly.setAttribute('points', pts);
    poly.setAttribute('fill','none');
    poly.setAttribute('stroke','black');
  }

  function drawHoles() {
    svg.querySelectorAll('.hole').forEach(n=>n.remove());
    S.tone_holes.forEach((h, i)=>{
      const cx = mm2px(h.x_mm);
      const r = Math.max(2, (h.diameter_mm/2)*S.px_per_mm);
      const cy = centerY() + (h.y_offset_mm||0)*S.px_per_mm;
      const g = document.createElementNS('http://www.w3.org/2000/svg','g'); g.classList.add('hole'); g.setAttribute('data-index', i);

      const c = document.createElementNS('http://www.w3.org/2000/svg','circle');
      c.setAttribute('cx', cx); c.setAttribute('cy', cy); c.setAttribute('r', r);
      c.setAttribute('fill', 'none'); c.setAttribute('stroke', h.ringed ? 'teal' : 'crimson'); c.setAttribute('stroke-width','1.5');

      const label = document.createElementNS('http://www.w3.org/2000/svg','text');
      label.setAttribute('x', cx); label.setAttribute('y', cy - (r+8));
      label.setAttribute('text-anchor','middle'); label.setAttribute('font-size','10');
      label.textContent = h.name_label || `Hole ${i+1}`;

      g.appendChild(c); g.appendChild(label); svg.appendChild(g);

      // Drag along X with snapping
      let dragging=false, startX=0;
      g.addEventListener('pointerdown', (e)=>{ dragging=true; startX=e.clientX; g.setPointerCapture(e.pointerId); pushHist(); });
      g.addEventListener('pointermove', (e)=>{
        if(!dragging) return;
        const dx = e.clientX - startX; startX = e.clientX;
        const new_cx = parseFloat(c.getAttribute('cx')) + dx;
        c.setAttribute('cx', new_cx); label.setAttribute('x', new_cx);
        let xmm = px2mm(new_cx);
        xmm = snapMM(xmm);
        S.tone_holes[i].x_mm = Math.max(0, Math.min(xmm, S.overall_length_mm));
        // Reflect in list
        $(`#holes_list .row[data-index="${i}"] input[name="x_mm"]`).val(S.tone_holes[i].x_mm.toFixed(2));
      });
      g.addEventListener('pointerup', ()=> dragging=false);
      g.addEventListener('pointercancel', ()=> dragging=false);
    });
  }

  function refreshBoreList() {
    const $b = $('#bore_list').empty();
    const header = $(`<div class="row fw-bold small">
        <div class="col-4">X (mm)</div><div class="col-4">Bore Ø (mm)</div><div class="col-4">Del</div>
      </div>`);
    $b.append(header);
    S.bore_segments.sort((a,b)=>a.x_mm-b.x_mm).forEach((s, idx)=>{
      const row = $(`
        <div class="row align-items-center mb-1" data-index="${idx}">
          <div class="col-4"><input name="x_mm" type="number" step="0.1" class="form-control form-control-sm" value="${s.x_mm}"/></div>
          <div class="col-4"><input name="bore_mm" type="number" step="0.01" class="form-control form-control-sm" value="${s.bore_mm}"/></div>
          <div class="col-4 text-end"><button class="btn btn-sm btn-outline-danger del_bore">×</button></div>
        </div>
      `);
      row.on('input','input',(e)=>{ const n=e.currentTarget.name; const v=parseFloat(e.currentTarget.value); S.bore_segments[idx][n]=isFinite(v)?v:S.bore_segments[idx][n]; draw(); });
      row.on('click','.del_bore',()=>{ pushHist(); S.bore_segments.splice(idx,1); refreshBoreList(); draw(); });
      $b.append(row);
    });
  }

  function refreshHoleList() {
    const $h = $('#holes_list').empty();
    const head = $(`<div class="row fw-bold small">
      <div class="col-2">Name</div><div class="col-2">Note</div><div class="col-2">X (mm)</div>
      <div class="col-2">Ø (mm)</div><div class="col-2">Y (mm)</div><div class="col-2">Del</div>
    </div>`);
    $h.append(head);
    S.tone_holes.forEach((h, idx)=>{
      const row = $(`
        <div class="row align-items-center mb-1" data-index="${idx}">
          <div class="col-2"><input name="name_label" class="form-control form-control-sm" value="${frappe.utils.escape_html(h.name_label||'')}"/></div>
          <div class="col-2"><input name="note_label" class="form-control form-control-sm" value="${frappe.utils.escape_html(h.note_label||'')}"/></div>
          <div class="col-2"><input name="x_mm" type="number" step="0.1" class="form-control form-control-sm" value="${h.x_mm}"/></div>
          <div class="col-2"><input name="diameter_mm" type="number" step="0.01" class="form-control form-control-sm" value="${h.diameter_mm}"/></div>
          <div class="col-2"><input name="y_offset_mm" type="number" step="0.1" class="form-control form-control-sm" value="${h.y_offset_mm||0}"/></div>
          <div class="col-2 text-end"><button class="btn btn-sm btn-outline-danger del_hole">×</button></div>
          <div class="col-12 small mt-1">
            <div class="d-flex flex-wrap gap-2">
              <label class="form-check">
                <input class="form-check-input" type="checkbox" name="ringed" ${h.ringed? 'checked':''}/> <span class="form-check-label">Ringed</span>
              </label>
              <label class="form-check">
                <input class="form-check-input" type="checkbox" name="is_open_key" ${h.is_open_key? 'checked':''}/> <span class="form-check-label">Open-Key</span>
              </label>
              <span>Azimuth°</span>
              <input name="azimuth_deg" type="number" step="0.1" class="form-control form-control-sm" style="width:80px" value="${h.azimuth_deg||0}"/>
              <select name="joint" class="form-select form-select-sm" style="width:120px">
                <option ${h.joint==='Barrel'?'selected':''}>Barrel</option>
                <option ${h.joint==='Upper'?'selected':''}>Upper</option>
                <option ${h.joint==='Lower'?'selected':''}>Lower</option>
                <option ${h.joint==='Bell'?'selected':''}>Bell</option>
              </select>
            </div>
          </div>
        </div>
      `);
      row.on('input','input,select',(e)=>{
        const n=e.currentTarget.name;
        const v=(n==='name_label'||n==='note_label'||n==='joint')? $(e.currentTarget).val() : parseFloat($(e.currentTarget).val());
        S.tone_holes[idx][n] = (n==='name_label'||n==='note_label'||n==='joint') ? v : (isFinite(v)?v:S.tone_holes[idx][n]);
        draw();
      });
      row.on('change','input[type="checkbox"]',(e)=>{
        const n=e.currentTarget.name; S.tone_holes[idx][n] = e.currentTarget.checked ? 1 : 0; draw();
      });
      row.on('click','.del_hole',()=>{ pushHist(); S.tone_holes.splice(idx,1); refreshHoleList(); draw(); });
      $h.append(row);
    });
  }

  function draw() {
    sizeCanvas();
    [...svg.querySelectorAll('*')].forEach(n=>n.remove());
    drawRuler();
    drawAxisAndSections();
    drawBore();
    drawHoles();
  }

  function recomputeOverallFromSections() {
    const { xBellEnd } = sectionPositions();
    S.overall_length_mm = xBellEnd;
    $('#overall_length_mm').val(S.overall_length_mm);
  }

  function collectHeaderFromForm() {
    S.title = $('#title').val();
    S.clarinet_type = $('#clarinet_type').val();
    S.grid_mm = parseFloat($('#grid_mm').val()) || S.grid_mm;
    S.wall_thickness_mm = parseFloat($('#wall_thickness_mm').val()) || S.wall_thickness_mm;
    S.barrel_length_mm = parseFloat($('#barrel_length_mm').val()) || S.barrel_length_mm;
    S.upper_joint_length_mm = parseFloat($('#upper_joint_length_mm').val()) || S.upper_joint_length_mm;
    S.tenon_gap_mm = parseFloat($('#tenon_gap_mm').val()) || S.tenon_gap_mm;
    S.lower_joint_length_mm = parseFloat($('#lower_joint_length_mm').val()) || S.lower_joint_length_mm;
    S.bell_length_mm = parseFloat($('#bell_length_mm').val()) || S.bell_length_mm;
    S.overall_length_mm = parseFloat($('#overall_length_mm').val()) || S.overall_length_mm;
    S.px_per_mm = parseFloat($('#px_per_mm').val()) || S.px_per_mm;
  }

  async function saveDesign() {
    const payload = JSON.stringify({
      title: S.title,
      clarinet_type: S.clarinet_type,
      overall_length_mm: S.overall_length_mm,
      barrel_length_mm: S.barrel_length_mm,
      upper_joint_length_mm: S.upper_joint_length_mm,
      tenon_gap_mm: S.tenon_gap_mm,
      lower_joint_length_mm: S.lower_joint_length_mm,
      bell_length_mm: S.bell_length_mm,
      wall_thickness_mm: S.wall_thickness_mm,
      grid_mm: S.grid_mm,
      bore_segments: S.bore_segments,
      tone_holes: S.tone_holes
    });
    await frappe.call({ method: 'repair_portal.prototyping.clarinet_api.save_design', args: { prototype, payload }});
    frappe.show_alert({ message: 'Design saved', indicator: 'green' });
  }

  // ---- Bindings ----
  $('#px_per_mm,#grid_mm,#wall_thickness_mm,#barrel_length_mm,#upper_joint_length_mm,#tenon_gap_mm,#lower_joint_length_mm,#bell_length_mm,#overall_length_mm,#title,#clarinet_type')
    .on('input change', ()=>{ collectHeaderFromForm(); recomputeOverallFromSections(); draw(); });

  $('#undo').on('click', ()=>{
    if (!undoStack.length) return;
    const cur = JSON.stringify(S); redoStack.push(cur);
    const prev = JSON.parse(undoStack.pop()); Object.assign(S, prev);
    // sync UI
    $('#title').val(S.title); $('#clarinet_type').val(S.clarinet_type);
    $('#grid_mm').val(S.grid_mm); $('#wall_thickness_mm').val(S.wall_thickness_mm);
    $('#barrel_length_mm').val(S.barrel_length_mm); $('#upper_joint_length_mm').val(S.upper_joint_length_mm);
    $('#tenon_gap_mm').val(S.tenon_gap_mm); $('#lower_joint_length_mm').val(S.lower_joint_length_mm);
    $('#bell_length_mm').val(S.bell_length_mm); $('#overall_length_mm').val(S.overall_length_mm);
    refreshBoreList(); refreshHoleList(); draw();
  });
  $('#redo').on('click', ()=>{
    if (!redoStack.length) return;
    const cur = JSON.stringify(S); undoStack.push(cur);
    const next = JSON.parse(redoStack.pop()); Object.assign(S, next);
    $('#title').val(S.title); $('#clarinet_type').val(S.clarinet_type);
    $('#grid_mm').val(S.grid_mm); $('#wall_thickness_mm').val(S.wall_thickness_mm);
    $('#barrel_length_mm').val(S.barrel_length_mm); $('#upper_joint_length_mm').val(S.upper_joint_length_mm);
    $('#tenon_gap_mm').val(S.tenon_gap_mm); $('#lower_joint_length_mm').val(S.lower_joint_length_mm);
    $('#bell_length_mm').val(S.bell_length_mm); $('#overall_length_mm').val(S.overall_length_mm);
    refreshBoreList(); refreshHoleList(); draw();
  });

  $('#save').on('click', async ()=>{ collectHeaderFromForm(); await saveDesign(); });

  let autosaveTimer = null;
  $('#autosave_toggle').on('change', (e)=>{
    S.autosave = e.currentTarget.checked;
    if (S.autosave) {
      autosaveTimer = setInterval(()=>saveDesign().catch(()=>{}), 60000);
    } else if (autosaveTimer) {
      clearInterval(autosaveTimer); autosaveTimer = null;
    }
  });

  $('#add_bore').on('click', ()=>{ pushHist(); S.bore_segments.push({x_mm:0, bore_mm:14.6}); refreshBoreList(); draw(); });
  $('#clear_bore').on('click', ()=>{ pushHist(); S.bore_segments=[]; refreshBoreList(); draw(); });

  $('#add_hole').on('click', ()=>{ pushHist(); S.tone_holes.push({
      name_label:`Hole ${S.tone_holes.length+1}`, note_label:"",
      joint:"Upper", x_mm:100, diameter_mm:6.0, chimney_mm:4.0,
      undercut_pct:0, azimuth_deg:0, y_offset_mm:0, ringed:0, is_open_key:0
    }); refreshHoleList(); draw(); });
  $('#clear_holes').on('click', ()=>{ pushHist(); S.tone_holes=[]; refreshHoleList(); draw(); });

  $('#export_json').on('click', ()=>{
    const blob = new Blob([JSON.stringify({
      title:S.title, clarinet_type:S.clarinet_type, overall_length_mm:S.overall_length_mm,
      barrel_length_mm:S.barrel_length_mm, upper_joint_length_mm:S.upper_joint_length_mm,
      tenon_gap_mm:S.tenon_gap_mm, lower_joint_length_mm:S.lower_joint_length_mm,
      bell_length_mm:S.bell_length_mm, wall_thickness_mm:S.wall_thickness_mm, grid_mm:S.grid_mm,
      bore_segments:S.bore_segments, tone_holes:S.tone_holes
    }, null, 2)], {type: 'application/json'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
    a.download = `${prototype}-clarinet-design.json`; a.click(); URL.revokeObjectURL(a.href);
  });

  $('#import_json').on('change', (e)=>{
    const file = e.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = ()=>{
      try {
        pushHist();
        const obj = JSON.parse(reader.result);
        Object.assign(S, {
          title: obj.title ?? S.title,
          clarinet_type: obj.clarinet_type ?? S.clarinet_type,
          overall_length_mm: obj.overall_length_mm ?? S.overall_length_mm,
          barrel_length_mm: obj.barrel_length_mm ?? S.barrel_length_mm,
          upper_joint_length_mm: obj.upper_joint_length_mm ?? S.upper_joint_length_mm,
          tenon_gap_mm: obj.tenon_gap_mm ?? S.tenon_gap_mm,
          lower_joint_length_mm: obj.lower_joint_length_mm ?? S.lower_joint_length_mm,
          bell_length_mm: obj.bell_length_mm ?? S.bell_length_mm,
          wall_thickness_mm: obj.wall_thickness_mm ?? S.wall_thickness_mm,
          grid_mm: obj.grid_mm ?? S.grid_mm,
          bore_segments: obj.bore_segments ?? S.bore_segments,
          tone_holes: obj.tone_holes ?? S.tone_holes
        });
        $('#title').val(S.title); $('#clarinet_type').val(S.clarinet_type);
        $('#grid_mm').val(S.grid_mm); $('#wall_thickness_mm').val(S.wall_thickness_mm);
        $('#barrel_length_mm').val(S.barrel_length_mm); $('#upper_joint_length_mm').val(S.upper_joint_length_mm);
        $('#tenon_gap_mm').val(S.tenon_gap_mm); $('#lower_joint_length_mm').val(S.lower_joint_length_mm);
        $('#bell_length_mm').val(S.bell_length_mm); $('#overall_length_mm').val(S.overall_length_mm);
        refreshBoreList(); refreshHoleList(); draw();
      } catch {
        frappe.msgprint('Invalid JSON file.');
      }
    };
    reader.readAsText(file);
  });

  $('#export_svg').on('click', async ()=>{
    const xml = new XMLSerializer().serializeToString(svg);
    const b64 = btoa(unescape(encodeURIComponent(xml)));
    const r = await frappe.call({ method: 'repair_portal.prototyping.clarinet_api.export_svg', args: { prototype, svg_text_b64: b64 }});
    frappe.msgprint(`SVG attached: <a href="${r.message}" target="_blank">${r.message}</a>`);
  });

  $('#export_png').on('click', async ()=>{
    // Convert SVG to PNG on the client, then attach
    const xml = new XMLSerializer().serializeToString(svg);
    const img = new Image();
    const blob = new Blob([xml], {type:'image/svg+xml;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    img.onload = async () => {
      const canvas = document.createElement('canvas');
      canvas.width = svg.viewBox.baseVal.width || svg.getBoundingClientRect().width;
      canvas.height = svg.viewBox.baseVal.height || svg.getBoundingClientRect().height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      const data = canvas.toDataURL('image/png').split(',')[1]; // base64
      const r = await frappe.call({ method: 'repair_portal.prototyping.clarinet_api.export_png', args: { prototype, png_b64: data }});
      frappe.msgprint(`PNG attached: <a href="${r.message}" target="_blank">${r.message}</a>`);
    };
    img.src = url;
  });

  $('#back').on('click', ()=> frappe.set_route('Form', 'Prototype', prototype));

  // ---- Initial lists + draw ----
  refreshBoreList(); refreshHoleList(); draw();
};

/* Clarinet Visual Editor + OpenWind bridge (concise) */
frappe.pages['clarinet-editor'].on_page_load = async function(wrapper) {
  const page = frappe.ui.make_app_page({ parent: wrapper, title: 'Clarinet Editor', single_column: true });
  const q = new URLSearchParams(window.location.search); const prototype = q.get('prototype');
  if (!prototype) { $(page.body).html(`<div class="text-danger p-3">Missing prototype.</div>`); return; }

  $(page.body).html(`
    <div class="p-3 d-flex gap-3 flex-wrap">
      <div class="editor-side">
        <div class="mb-2"><b>Prototype:</b> <span id="proto_name"></span></div>
        <div class="mb-2"><label class="form-label">Title</label><input id="title" class="form-control form-control-sm"/></div>
        <div class="mb-2"><label class="form-label">Type</label>
          <select id="clarinet_type" class="form-select form-select-sm"><option>B♭</option><option>A</option><option>E♭</option><option>C</option><option>Bass (Low E♭)</option><option>Bass (Low C)</option></select>
        </div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">px/mm</label><input id="px_per_mm" type="number" step="0.1" value="1.2" class="form-control form-control-sm"/></div>
          <div class="col-6"><label class="form-label">Grid (mm)</label><input id="grid_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
        </div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">Wall (mm)</label><input id="wall_thickness_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
          <div class="col-6"><label class="form-label">Overall (mm)</label><input id="overall_length_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
        </div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">Barrel</label><input id="barrel_length_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
          <div class="col-6"><label class="form-label">Upper</label><input id="upper_joint_length_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
        </div>
        <div class="row g-2 mb-3">
          <div class="col-6"><label class="form-label">Tenon Gap</label><input id="tenon_gap_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
          <div class="col-6"><label class="form-label">Lower</label><input id="lower_joint_length_mm" type="number" step="0.1" class="form-control form-control-sm"/></div>
        </div>
        <div class="d-flex gap-2 mb-3">
          <button id="save" class="btn btn-primary btn-sm">Save</button>
          <button id="run_sim" class="btn btn-outline-primary btn-sm">Run Simulation</button>
        </div>
        <div class="mb-2"><b>Bore Samples</b> <button id="add_bore" class="btn btn-sm btn-outline-secondary">Add</button> <button id="clear_bore" class="btn btn-sm btn-outline-danger">Clear</button></div>
        <div id="bore_list" class="small mb-3"></div>
        <div class="mb-2"><b>Tone Holes</b> <button id="add_hole" class="btn btn-sm btn-outline-secondary">Add</button> <button id="clear_holes" class="btn btn-sm btn-outline-danger">Clear</button></div>
        <div id="holes_list" class="small"></div>
        <hr/>
        <div id="warns" class="alert alert-warning d-none"></div>
        <div class="d-grid gap-2 mt-2">
          <button id="export_svg" class="btn btn-outline-secondary btn-sm">Export SVG</button>
          <button id="export_png" class="btn btn-outline-secondary btn-sm">Export PNG</button>
          <button id="back" class="btn btn-outline-dark btn-sm">Back</button>
        </div>
      </div>
      <div class="flex-grow-1">
        <svg id="clarinet_svg" class="clarinet-svg" xmlns="http://www.w3.org/2000/svg"></svg>
        <div class="mt-3">
          <div class="d-flex justify-content-between align-items-center">
            <b>Impedance</b>
            <div class="small text-muted">Shows |Z| vs frequency (Hz)</div>
          </div>
          <canvas id="imp_canvas" width="980" height="260" style="border:1px solid #ddd;background:#fff"></canvas>
        </div>
      </div>
    </div>
  `);

  $('#proto_name').text(prototype);

  // --- state ---
  const S = {
    title:"", clarinet_type:"B♭", px_per_mm:1.2, grid_mm:5, wall_thickness_mm:2.5,
    overall_length_mm:600, barrel_length_mm:66, upper_joint_length_mm:230,
    tenon_gap_mm:2, lower_joint_length_mm:250, bell_length_mm:110,
    bore_segments:[], tone_holes:[], warnIdx:new Set()
  };

  // --- helpers ---
  const svg = document.getElementById('clarinet_svg');
  const canvas = document.getElementById('imp_canvas'); const ctx = canvas.getContext('2d');

  function mm2px(x){ return x*S.px_per_mm + 40; }
  function px2mm(px){ return (px-40)/S.px_per_mm; }
  function centerY(){ return 150; }
  function sizeCanvas(){ const W=Math.max(1000, S.overall_length_mm*S.px_per_mm+80); svg.setAttribute('width',W); svg.setAttribute('height',320); svg.setAttribute('viewBox',`0 0 ${W} 320`); }
  function snapMM(x){ const g=Math.max(0.1,S.grid_mm||5); return Math.round(x/g)*g; }
  function interpBore(x){
    const B=[...S.bore_segments].sort((a,b)=>a.x_mm-b.x_mm);
    if(!B.length) return 14.6;
    if(x<=B[0].x_mm) return B[0].bore_mm;
    if(x>=B[B.length-1].x_mm) return B[B.length-1].bore_mm;
    for(let i=0;i<B.length-1;i++){
      const a=B[i], b=B[i+1]; if(x>=a.x_mm && x<=b.x_mm){ const t=(x-a.x_mm)/(b.x_mm-a.x_mm); return a.bore_mm+t*(b.bore_mm-a.bore_mm); }
    }
    return B[B.length-1].bore_mm;
  }

  function drawAxis(){
    [...svg.querySelectorAll('#axis,#ruler')].forEach(n=>n.remove());
    const g=document.createElementNS('http://www.w3.org/2000/svg','g'); g.setAttribute('id','axis'); svg.appendChild(g);
    const y=centerY(); const ax=document.createElementNS('http://www.w3.org/2000/svg','line');
    ax.setAttribute('x1',mm2px(0)); ax.setAttribute('y1',y); ax.setAttribute('x2',mm2px(S.overall_length_mm)); ax.setAttribute('y2',y); ax.setAttribute('stroke','gray'); ax.setAttribute('stroke-dasharray','4 4'); g.appendChild(ax);
    const marks=[S.barrel_length_mm, S.barrel_length_mm+S.upper_joint_length_mm, S.barrel_length_mm+S.upper_joint_length_mm+S.tenon_gap_mm, S.overall_length_mm-S.bell_length_mm, S.overall_length_mm];
    const labels=['Barrel End','Upper End','Tenon Gap','Lower End','Bell End'];
    marks.forEach((mx,i)=>{ const L=document.createElementNS('http://www.w3.org/2000/svg','line'); L.setAttribute('x1',mm2px(mx)); L.setAttribute('y1',y-90); L.setAttribute('x2',mm2px(mx)); L.setAttribute('y2',y+90); L.setAttribute('stroke','steelblue'); g.appendChild(L);
      const T=document.createElementNS('http://www.w3.org/2000/svg','text'); T.setAttribute('x',mm2px(mx)); T.setAttribute('y',y-96); T.setAttribute('text-anchor','middle'); T.setAttribute('font-size','10'); T.textContent=labels[i]; g.appendChild(T); });
  }

  function boreY(d){ const y=centerY(), r=(d/2)*S.px_per_mm; return [y-r,y+r]; }
  function drawBore(){
    const old=svg.querySelector('#bore'); if(old) old.remove();
    if(!S.bore_segments.length) return;
    const B=[...S.bore_segments].sort((a,b)=>a.x_mm-b.x_mm);
    const top=[],bot=[];
    B.forEach(s=>{ const x=mm2px(s.x_mm); const [yt,yb]=boreY(s.bore_mm); top.push(`${x},${yt}`); bot.push(`${x},${yb}`); });
    const poly=document.createElementNS('http://www.w3.org/2000/svg','polygon'); poly.setAttribute('id','bore'); poly.setAttribute('points', top.concat(bot.reverse()).join(' ')); poly.setAttribute('fill','none'); poly.setAttribute('stroke','black'); svg.appendChild(poly);
  }

  function drawHoles(){
    svg.querySelectorAll('.hole').forEach(n=>n.remove());
    S.tone_holes.forEach((h,i)=>{
      const cx=mm2px(h.x_mm); const r=Math.max(2,(h.diameter_mm/2)*S.px_per_mm); const cy=centerY()+(h.y_offset_mm||0)*S.px_per_mm;
      const g=document.createElementNS('http://www.w3.org/2000/svg','g'); g.classList.add('hole'); g.setAttribute('data-index',i);
      const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
      c.setAttribute('cx',cx); c.setAttribute('cy',cy); c.setAttribute('r',r);
      c.setAttribute('fill','none'); c.setAttribute('stroke', S.warnIdx.has(i)? 'red' : (h.ringed?'teal':'crimson')); c.setAttribute('stroke-width','1.5');
      const t=document.createElementNS('http://www.w3.org/2000/svg','text'); t.setAttribute('x',cx); t.setAttribute('y',cy-(r+8)); t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','10'); t.textContent=h.name_label||`Hole ${i+1}`;
      g.appendChild(c); g.appendChild(t); svg.appendChild(g);
      let drag=false, sx=0;
      g.addEventListener('pointerdown',e=>{ drag=true; sx=e.clientX; g.setPointerCapture(e.pointerId); });
      g.addEventListener('pointermove',e=>{ if(!drag) return; const dx=e.clientX-sx; sx=e.clientX; const ncx=parseFloat(c.getAttribute('cx'))+dx; c.setAttribute('cx',ncx); t.setAttribute('x',ncx);
        S.tone_holes[i].x_mm=Math.max(0,Math.min(snapMM(px2mm(ncx)),S.overall_length_mm)); $(`#holes_list .row[data-index="${i}"] input[name="x_mm"]`).val(S.tone_holes[i].x_mm.toFixed(2)); });
      g.addEventListener('pointerup',()=>drag=false); g.addEventListener('pointercancel',()=>drag=false);
    });
  }

  function refreshBoreList(){
    const $b=$('#bore_list').empty(); $b.append(`<div class="row fw-bold small"><div class="col-4">X</div><div class="col-4">Ø</div><div class="col-4">Del</div></div>`);
    S.bore_segments.sort((a,b)=>a.x_mm-b.x_mm).forEach((s,i)=>{
      const row=$(`
        <div class="row align-items-center mb-1" data-index="${i}">
          <div class="col-4"><input name="x_mm" type="number" step="0.1" class="form-control form-control-sm" value="${s.x_mm}"/></div>
          <div class="col-4"><input name="bore_mm" type="number" step="0.01" class="form-control form-control-sm" value="${s.bore_mm}"/></div>
          <div class="col-4 text-end"><button class="btn btn-sm btn-outline-danger del_bore">×</button></div>
        </div>`);
      row.on('input','input',(e)=>{ const n=e.currentTarget.name; const v=parseFloat(e.currentTarget.value); S.bore_segments[i][n]=isFinite(v)?v:S.bore_segments[i][n]; draw(); });
      row.on('click','.del_bore',()=>{ S.bore_segments.splice(i,1); refreshBoreList(); draw(); });
      $b.append(row);
    });
  }

  function refreshHoleList(){
    const $h=$('#holes_list').empty();
    $h.append(`<div class="row fw-bold small"><div class="col-3">Name</div><div class="col-2">Note</div><div class="col-2">X</div><div class="col-2">Ø</div><div class="col-2">Y</div><div class="col-1">Del</div></div>`);
    S.tone_holes.forEach((h,i)=>{
      const row=$(`
        <div class="row align-items-center mb-1" data-index="${i}">
          <div class="col-3"><input name="name_label" class="form-control form-control-sm" value="${frappe.utils.escape_html(h.name_label||'')}"/></div>
          <div class="col-2"><input name="note_label" class="form-control form-control-sm" value="${frappe.utils.escape_html(h.note_label||'')}"/></div>
          <div class="col-2"><input name="x_mm" type="number" step="0.1" class="form-control form-control-sm" value="${h.x_mm}"/></div>
          <div class="col-2"><input name="diameter_mm" type="number" step="0.01" class="form-control form-control-sm" value="${h.diameter_mm}"/></div>
          <div class="col-2"><input name="y_offset_mm" type="number" step="0.1" class="form-control form-control-sm" value="${h.y_offset_mm||0}"/></div>
          <div class="col-1 text-end"><button class="btn btn-sm btn-outline-danger del_hole">×</button></div>
          <div class="col-12 small mt-1">
            <div class="d-flex flex-wrap gap-2">
              <label class="form-check"><input class="form-check-input" type="checkbox" name="ringed" ${h.ringed?'checked':''}/> <span class="form-check-label">Ringed</span></label>
              <label class="form-check"><input class="form-check-input" type="checkbox" name="is_open_key" ${h.is_open_key?'checked':''}/> <span class="form-check-label">Open-Key</span></label>
              <span>Azimuth°</span><input name="azimuth_deg" type="number" step="0.1" class="form-control form-control-sm" style="width:80px" value="${h.azimuth_deg||0}"/>
              <select name="joint" class="form-select form-select-sm" style="width:120px"><option ${h.joint==='Barrel'?'selected':''}>Barrel</option><option ${h.joint==='Upper'?'selected':''}>Upper</option><option ${h.joint==='Lower'?'selected':''}>Lower</option><option ${h.joint==='Bell'?'selected':''}>Bell</option></select>
            </div>
          </div>
        </div>`);
      row.on('input','input,select',(e)=>{ const n=e.currentTarget.name; const v=(n==='name_label'||n==='note_label'||n==='joint')?$(e.currentTarget).val():parseFloat($(e.currentTarget).val()); S.tone_holes[i][n]=(n==='name_label'||n==='note_label'||n==='joint')?v:(isFinite(v)?v:S.tone_holes[i][n]); draw(); });
      row.on('change','input[type="checkbox"]',(e)=>{ const n=e.currentTarget.name; S.tone_holes[i][n]=e.currentTarget.checked?1:0; draw(); });
      row.on('click','.del_hole',()=>{ S.tone_holes.splice(i,1); refreshHoleList(); draw(); });
      $h.append(row);
    });
  }

  function collectHeader(){
    S.title=$('#title').val(); S.clarinet_type=$('#clarinet_type').val();
    S.px_per_mm=parseFloat($('#px_per_mm').val())||S.px_per_mm; S.grid_mm=parseFloat($('#grid_mm').val())||S.grid_mm;
    S.wall_thickness_mm=parseFloat($('#wall_thickness_mm').val())||S.wall_thickness_mm;
    S.barrel_length_mm=parseFloat($('#barrel_length_mm').val())||S.barrel_length_mm;
    S.upper_joint_length_mm=parseFloat($('#upper_joint_length_mm').val())||S.upper_joint_length_mm;
    S.tenon_gap_mm=parseFloat($('#tenon_gap_mm').val())||S.tenon_gap_mm;
    S.lower_joint_length_mm=parseFloat($('#lower_joint_length_mm').val())||S.lower_joint_length_mm;
    S.overall_length_mm=parseFloat($('#overall_length_mm').val())||S.overall_length_mm;
    S.bell_length_mm = S.overall_length_mm - (S.barrel_length_mm + S.upper_joint_length_mm + S.tenon_gap_mm + S.lower_joint_length_mm);
  }

  function toleranceChecks(){
    const msgs=[]; S.warnIdx.clear();
    S.tone_holes.forEach((h,i)=>{
      const bore_d=interpBore(h.x_mm);
      const outer_d=bore_d + 2*(S.wall_thickness_mm||0);
      const eff_hole_d=(h.diameter_mm||0)*(1 + (h.undercut_pct||0)/100);
      const margin = outer_d - eff_hole_d;
      if (margin < 0.6) { // min clearance
        S.warnIdx.add(i);
        msgs.push(`${h.name_label||'Hole '+(i+1)} @ ${h.x_mm.toFixed(1)}mm: margin ${margin.toFixed(2)}mm (< 0.6mm).`);
      }
    });
    const box=$('#warns');
    if (msgs.length){ box.removeClass('d-none').html(`<b>Tolerance warnings:</b><br>${msgs.map(m=>`• ${m}`).join('<br>')}`); }
    else { box.addClass('d-none').empty(); }
  }

  function draw(){ sizeCanvas(); [...svg.querySelectorAll('*')].forEach(n=>n.remove()); drawAxis(); drawBore(); toleranceChecks(); drawHoles(); }

  async function saveDesign(){
    const payload=JSON.stringify({
      title:S.title, clarinet_type:S.clarinet_type, overall_length_mm:S.overall_length_mm,
      barrel_length_mm:S.barrel_length_mm, upper_joint_length_mm:S.upper_joint_length_mm,
      tenon_gap_mm:S.tenon_gap_mm, lower_joint_length_mm:S.lower_joint_length_mm,
      bell_length_mm:S.bell_length_mm, wall_thickness_mm:S.wall_thickness_mm, grid_mm:S.grid_mm,
      bore_segments:S.bore_segments, tone_holes:S.tone_holes
    });
    await frappe.call({ method:'repair_portal.prototyping.clarinet_api.save_design', args:{ prototype, payload }});
    frappe.show_alert({message:'Saved', indicator:'green'});
  }

  function plotImpedance(freqs, z){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    if(!freqs || !freqs.length) return;
    const W=canvas.width, H=canvas.height, pad=30;
    const fmin=Math.min(...freqs), fmax=Math.max(...freqs);
    const zmax=Math.max(...z);
    const x=(f)=> pad + (W-2*pad)*( (f-fmin)/(fmax-fmin) );
    const y=(v)=> H-pad - (H-2*pad)*( v/(zmax||1) );
    // axes
    ctx.beginPath(); ctx.moveTo(pad,H-pad); ctx.lineTo(W-pad,H-pad); ctx.moveTo(pad,H-pad); ctx.lineTo(pad,pad); ctx.stroke();
    // line
    ctx.beginPath();
    ctx.moveTo(x(freqs[0]), y(z[0]));
    for(let i=1;i<freqs.length;i++){ ctx.lineTo(x(freqs[i]), y(z[i])); }
    ctx.stroke();
  }

  // --- load initial ---
  const r = await frappe.call({ method:'repair_portal.prototyping.clarinet_api.load_design', args:{ prototype }});
  Object.assign(S, r.message); S.px_per_mm=1.2; $('#title').val(S.title); $('#clarinet_type').val(S.clarinet_type);
  $('#grid_mm').val(S.grid_mm); $('#wall_thickness_mm').val(S.wall_thickness_mm);
  $('#overall_length_mm').val(S.overall_length_mm); $('#barrel_length_mm').val(S.barrel_length_mm);
  $('#upper_joint_length_mm').val(S.upper_joint_length_mm); $('#tenon_gap_mm').val(S.tenon_gap_mm);
  $('#lower_joint_length_mm').val(S.lower_joint_length_mm);

  // --- bind UI ---
  $('#px_per_mm,#grid_mm,#wall_thickness_mm,#overall_length_mm,#barrel_length_mm,#upper_joint_length_mm,#tenon_gap_mm,#lower_joint_length_mm,#title,#clarinet_type')
    .on('input change', ()=>{ collectHeader(); draw(); });

  $('#save').on('click', async ()=>{ collectHeader(); await saveDesign(); });

  $('#export_svg').on('click', async ()=>{ const xml=new XMLSerializer().serializeToString(svg); const b64=btoa(unescape(encodeURIComponent(xml)));
    const r=await frappe.call({ method:'repair_portal.prototyping.clarinet_api.export_svg', args:{ prototype, svg_text_b64:b64 }}); frappe.msgprint(`SVG attached: <a target="_blank" href="${r.message}">${r.message}</a>`); });

  $('#export_png').on('click', async ()=>{ const xml=new XMLSerializer().serializeToString(svg); const img=new Image(); const url=URL.createObjectURL(new Blob([xml],{type:'image/svg+xml'}));
    img.onload=async()=>{ const c=document.createElement('canvas'); c.width=svg.viewBox.baseVal.width||svg.getBoundingClientRect().width; c.height=svg.viewBox.baseVal.height||svg.getBoundingClientRect().height;
      const cx=c.getContext('2d'); cx.drawImage(img,0,0); URL.revokeObjectURL(url);
      const b64=c.toDataURL('image/png').split(',')[1]; const r=await frappe.call({ method:'repair_portal.prototyping.clarinet_api.export_png', args:{ prototype, png_b64:b64 }});
      frappe.msgprint(`PNG attached: <a target="_blank" href="${r.message}">${r.message}</a>`); }; img.src=url; });

  $('#add_bore').on('click', ()=>{ S.bore_segments.push({x_mm:0,bore_mm:14.6}); refreshBoreList(); draw(); });
  $('#clear_bore').on('click', ()=>{ S.bore_segments=[]; refreshBoreList(); draw(); });
  $('#add_hole').on('click', ()=>{ S.tone_holes.push({name_label:`Hole ${S.tone_holes.length+1}`,note_label:"",joint:"Upper",x_mm:100,diameter_mm:6,chimney_mm:4,undercut_pct:0,azimuth_deg:0,y_offset_mm:0,ringed:0,is_open_key:0}); refreshHoleList(); draw(); });
  $('#clear_holes').on('click', ()=>{ S.tone_holes=[]; refreshHoleList(); draw(); });

  $('#back').on('click', ()=> frappe.set_route('Form','Prototype',prototype));

  $('#run_sim').on('click', async ()=>{
    await saveDesign(); // ensure latest geometry
    const sim = await frappe.call({
      method: 'repair_portal.prototyping.clarinet_api.run_openwind',
      args: { prototype, solver_params_json: JSON.stringify({ f_min_hz: 50, f_max_hz: 4000, df_hz: 5 }) }
    });
    const m = sim.message || {};
    if (m.plot_png_b64){
      // draw returned PNG
      const img=new Image(); img.onload=()=>{ ctx.clearRect(0,0,canvas.width,canvas.height); ctx.drawImage(img,0,0,canvas.width,canvas.height); }; img.src=`data:image/png;base64,${m.plot_png_b64}`;
      // also attach
      await frappe.call({ method:'repair_portal.prototyping.clarinet_api.export_png', args:{ prototype, png_b64: m.plot_png_b64 }});
      frappe.show_alert('Simulation plot attached');
    } else if (m.frequencies && m.impedance){
      plotImpedance(m.frequencies, m.impedance);
      // attach canvas snapshot
      const b64 = canvas.toDataURL('image/png').split(',')[1];
      await frappe.call({ method:'repair_portal.prototyping.clarinet_api.export_png', args:{ prototype, png_b64: b64 }});
      frappe.show_alert('Simulation plot attached');
    } else {
      frappe.msgprint('Simulation ran, but no recognizable output was returned.');
    }
  });

  function refreshAll(){ refreshBoreList(); refreshHoleList(); draw(); }
  refreshAll();
};
