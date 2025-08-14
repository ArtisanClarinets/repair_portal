/* Prototype Designer (Frappe v15)
 * Visual SVG designer stored in Prototype.parameters[ "design_json" ].
 * - Tools: Select, Rectangle, Circle, Line, Text
 * - Grid + zoom (px/mm), snapping
 * - Drag to move/resize, property panel, delete, undo/redo
 * - Import/Export JSON, Download SVG
 * - Save back to Prototype via frappe.client.save
 */

frappe.pages['prototype-designer'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Prototype Designer',
    single_column: true
  });

  // ---- Routing / context ----
  const q = new URLSearchParams(window.location.search);
  const prototype = q.get('name'); // Prototype name
  page.set_primary_action('Back to Prototype', () => {
    if (prototype) frappe.set_route('Form', 'Prototype', prototype);
  });

  // ---- UI skeleton ----
  $(page.body).html(`
    <div class="p-3 d-flex gap-3 flex-wrap">
      <div class="border rounded p-2" style="width:320px;min-width:300px;">
        <div class="mb-2"><b>Prototype:</b> <span id="proto_name"></span></div>

        <div class="mb-2">
          <div class="btn-group w-100" role="group">
            <button class="btn btn-sm btn-outline-primary" id="tool_select" title="Select (V)">Select</button>
            <button class="btn btn-sm btn-outline-primary" id="tool_rect" title="Rectangle (R)">Rect</button>
            <button class="btn btn-sm btn-outline-primary" id="tool_circle" title="Circle (C)">Circle</button>
            <button class="btn btn-sm btn-outline-primary" id="tool_line" title="Line (L)">Line</button>
            <button class="btn btn-sm btn-outline-primary" id="tool_text" title="Text (T)">Text</button>
          </div>
        </div>

        <div class="row g-2 mb-2">
          <div class="col-6">
            <label class="form-label">Pixels / mm</label>
            <input id="px_per_mm" type="number" step="0.1" class="form-control form-control-sm" value="1.2"/>
          </div>
          <div class="col-6">
            <label class="form-label">Grid (mm)</label>
            <input id="grid_mm" type="number" step="0.1" class="form-control form-control-sm" value="5"/>
          </div>
        </div>
        <div class="form-check form-switch mb-2">
          <input class="form-check-input" type="checkbox" id="snap_toggle" checked>
          <label class="form-check-label" for="snap_toggle">Snap to Grid</label>
        </div>

        <div class="mb-2 d-flex gap-2">
          <button id="btn_undo" class="btn btn-sm btn-outline-secondary">Undo</button>
          <button id="btn_redo" class="btn btn-sm btn-outline-secondary">Redo</button>
          <button id="btn_delete" class="btn btn-sm btn-outline-danger">Delete</button>
        </div>

        <div class="mb-2"><b>Selection</b></div>
        <div id="prop_panel" class="small mb-3"></div>

        <div class="d-grid gap-2">
          <button id="btn_save" class="btn btn-sm btn-primary">Save to Prototype</button>
          <button id="btn_reload" class="btn btn-sm btn-outline-secondary">Reload</button>
          <button id="btn_export_json" class="btn btn-sm btn-outline-secondary">Export JSON</button>
          <input id="import_json" type="file" accept="application/json" class="form-control form-control-sm"/>
          <button id="btn_download_svg" class="btn btn-sm btn-outline-secondary">Download SVG</button>
        </div>
      </div>

      <div class="flex-grow-1">
        <div class="border rounded p-2" style="background:#fafafa;">
          <svg id="canvas" xmlns="http://www.w3.org/2000/svg"></svg>
        </div>
        <div class="mt-2 text-muted small">Tip: Use V/R/C/L/T keys to switch tools. Drag to move. For rect/circle: drag
          handles to resize. Hold Shift while dragging a line to lock horizontal/vertical.</div>
      </div>
    </div>
  `);

  $('#proto_name').text(prototype || '');

  // ---- State ----
  const S = {
    px_per_mm: 1.2,
    grid_mm: 5,
    snap: true,
    tool: 'select',
    shapes: [],         // list of {id,type,...}
    selectedId: null,
    protoDoc: null      // full Prototype doc for saving
  };

  const svg = document.getElementById('canvas');
  const NS = 'http://www.w3.org/2000/svg';

  // ---- History (undo/redo) ----
  const undo = [], redo = [];
  const pushHist = () => { undo.push(JSON.stringify(S.shapes)); if (undo.length > 50) undo.shift(); redo.length = 0; };
  const doUndo = () => { if (!undo.length) return; redo.push(JSON.stringify(S.shapes)); S.shapes = JSON.parse(undo.pop()); draw(); };
  const doRedo = () => { if (!redo.length) return; undo.push(JSON.stringify(S.shapes)); S.shapes = JSON.parse(redo.pop()); draw(); };

  // ---- Helpers ----
  const mm2px = (x) => x * S.px_per_mm;
  const px2mm = (px) => px / S.px_per_mm;
  const snapMM = (x) => S.snap ? Math.round(x / S.grid_mm) * S.grid_mm : x;
  const uid = () => 's' + Math.random().toString(36).slice(2, 9);

  function sizeCanvas() {
    // auto width from content; min viewport
    const width_px = Math.max(1200, 100 + S.px_per_mm * 600);
    const height_px = 600;
    svg.setAttribute('width', width_px);
    svg.setAttribute('height', height_px);
    svg.setAttribute('viewBox', `0 0 ${width_px} ${height_px}`);
  }

  // Grid
  function drawGrid() {
    const old = svg.querySelector('#grid'); if (old) old.remove();
    const g = document.createElementNS(NS, 'g'); g.setAttribute('id', 'grid'); svg.prepend(g);
    const W = svg.viewBox.baseVal.width || svg.getBoundingClientRect().width;
    const H = svg.viewBox.baseVal.height || svg.getBoundingClientRect().height;
    const step = Math.max(1, S.grid_mm) * S.px_per_mm;

    for (let x = 0; x <= W; x += step) {
      const line = document.createElementNS(NS, 'line');
      line.setAttribute('x1', x); line.setAttribute('y1', 0);
      line.setAttribute('x2', x); line.setAttribute('y2', H);
      line.setAttribute('stroke', '#eee');
      g.appendChild(line);
    }
    for (let y = 0; y <= H; y += step) {
      const line = document.createElementNS(NS, 'line');
      line.setAttribute('x1', 0); line.setAttribute('y1', y);
      line.setAttribute('x2', W); line.setAttribute('y2', y);
      line.setAttribute('stroke', '#eee');
      g.appendChild(line);
    }
  }

  // ---- Shape rendering ----
  function renderShapes() {
    // wipe non-grid layers
    svg.querySelectorAll('.shape,.sel,.handle').forEach(n => n.remove());
    S.shapes.forEach(s => {
      if (s.type === 'rect') {
        const r = document.createElementNS(NS, 'rect');
        r.classList.add('shape');
        r.setAttribute('x', mm2px(s.x));
        r.setAttribute('y', mm2px(s.y));
        r.setAttribute('width', mm2px(s.w));
        r.setAttribute('height', mm2px(s.h));
        r.setAttribute('fill', s.fill || 'none');
        r.setAttribute('stroke', s.stroke || 'black');
        r.setAttribute('stroke-width', s.sw || 1);
        r.dataset.id = s.id;
        svg.appendChild(r);
      } else if (s.type === 'circle') {
        const c = document.createElementNS(NS, 'circle');
        c.classList.add('shape');
        c.setAttribute('cx', mm2px(s.cx));
        c.setAttribute('cy', mm2px(s.cy));
        c.setAttribute('r', mm2px(s.r));
        c.setAttribute('fill', s.fill || 'none');
        c.setAttribute('stroke', s.stroke || 'black');
        c.setAttribute('stroke-width', s.sw || 1);
        c.dataset.id = s.id;
        svg.appendChild(c);
      } else if (s.type === 'line') {
        const l = document.createElementNS(NS, 'line');
        l.classList.add('shape');
        l.setAttribute('x1', mm2px(s.x1));
        l.setAttribute('y1', mm2px(s.y1));
        l.setAttribute('x2', mm2px(s.x2));
        l.setAttribute('y2', mm2px(s.y2));
        l.setAttribute('stroke', s.stroke || 'black');
        l.setAttribute('stroke-width', s.sw || 1);
        l.dataset.id = s.id;
        svg.appendChild(l);
      } else if (s.type === 'text') {
        const t = document.createElementNS(NS, 'text');
        t.classList.add('shape');
        t.setAttribute('x', mm2px(s.x));
        t.setAttribute('y', mm2px(s.y));
        t.setAttribute('font-size', (s.fs || 12));
        t.setAttribute('text-anchor', s.anchor || 'start');
        t.setAttribute('fill', s.fill || 'black');
        t.textContent = s.text || 'Text';
        t.dataset.id = s.id;
        svg.appendChild(t);
      }
    });
  }

  function drawSelection() {
    // selection box + handles
    const sel = S.shapes.find(x => x.id === S.selectedId);
    if (!sel) return;
    const add = (el) => { el.classList.add('sel'); svg.appendChild(el); };

    if (sel.type === 'rect') {
      const x = mm2px(sel.x), y = mm2px(sel.y), w = mm2px(sel.w), h = mm2px(sel.h);
      const box = document.createElementNS(NS, 'rect');
      box.setAttribute('x', x); box.setAttribute('y', y);
      box.setAttribute('width', w); box.setAttribute('height', h);
      box.setAttribute('fill', 'none'); box.setAttribute('stroke', '#4a90e2'); box.setAttribute('stroke-dasharray', '4 2');
      add(box);
      addHandle(x + w, y + h, 'se'); // resize handle
    } else if (sel.type === 'circle') {
      const cx = mm2px(sel.cx), cy = mm2px(sel.cy), r = mm2px(sel.r);
      const c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', cx); c.setAttribute('cy', cy); c.setAttribute('r', r);
      c.setAttribute('fill', 'none'); c.setAttribute('stroke', '#4a90e2'); c.setAttribute('stroke-dasharray', '4 2');
      add(c);
      addHandle(cx + r, cy, 'rad');
    } else if (sel.type === 'line') {
      const l = document.createElementNS(NS, 'line');
      l.setAttribute('x1', mm2px(sel.x1)); l.setAttribute('y1', mm2px(sel.y1));
      l.setAttribute('x2', mm2px(sel.x2)); l.setAttribute('y2', mm2px(sel.y2));
      l.setAttribute('stroke', '#4a90e2'); l.setAttribute('stroke-dasharray', '4 2');
      add(l);
      addHandle(mm2px(sel.x1), mm2px(sel.y1), 'p1');
      addHandle(mm2px(sel.x2), mm2px(sel.y2), 'p2');
    } else if (sel.type === 'text') {
      const x = mm2px(sel.x), y = mm2px(sel.y);
      const cross = document.createElementNS(NS, 'path');
      cross.setAttribute('d', `M ${x-8} ${y} L ${x+8} ${y} M ${x} ${y-8} L ${x} ${y+8}`);
      cross.setAttribute('stroke', '#4a90e2');
      add(cross);
    }

    function addHandle(x, y, role) {
      const h = document.createElementNS(NS, 'rect');
      h.setAttribute('x', x - 4); h.setAttribute('y', y - 4);
      h.setAttribute('width', 8); h.setAttribute('height', 8);
      h.setAttribute('fill', 'white'); h.setAttribute('stroke', '#4a90e2');
      h.classList.add('handle'); h.dataset.role = role;
      svg.appendChild(h);
    }
  }

  function draw() {
    sizeCanvas();
    drawGrid();
    renderShapes();
    drawSelection();
    buildPropPanel();
  }

  // ---- Interaction ----
  let dragging = null; // {mode:'move'|'resize'|'draw', id, start:{x,y}, ...}
  svg.addEventListener('pointerdown', (e) => {
    const pt = clientToSvg(e);
    const target = e.target;
    const clickedShape = target.classList.contains('shape') ? target : null;
    const clickedHandle = target.classList.contains('handle') ? target : null;

    if (clickedHandle) {
      const role = clickedHandle.dataset.role;
      dragging = { mode: 'resize', role, start: pt, id: S.selectedId };
      pushHist(); return;
    }

    if (clickedShape) {
      S.selectedId = clickedShape.dataset.id;
      buildPropPanel(); drawSelection();
      if (S.tool === 'select') {
        dragging = { mode: 'move', id: S.selectedId, start: pt };
        pushHist();
      }
      return;
    }

    // Canvas background
    if (S.tool === 'rect') {
      pushHist();
      const id = uid();
      const p = { id, type: 'rect', x: snapMM(px2mm(pt.x)), y: snapMM(px2mm(pt.y)), w: 10, h: 10, stroke: 'black', fill: 'none', sw: 1 };
      S.shapes.push(p); S.selectedId = id;
      dragging = { mode: 'draw', id, start: pt };
    } else if (S.tool === 'circle') {
      pushHist();
      const id = uid();
      const p = { id, type: 'circle', cx: snapMM(px2mm(pt.x)), cy: snapMM(px2mm(pt.y)), r: 5, stroke: 'black', fill: 'none', sw: 1 };
      S.shapes.push(p); S.selectedId = id;
      dragging = { mode: 'draw', id, start: pt };
    } else if (S.tool === 'line') {
      pushHist();
      const id = uid();
      const p = { id, type: 'line', x1: snapMM(px2mm(pt.x)), y1: snapMM(px2mm(pt.y)), x2: snapMM(px2mm(pt.x)), y2: snapMM(px2mm(pt.y)), stroke: 'black', sw: 1 };
      S.shapes.push(p); S.selectedId = id;
      dragging = { mode: 'draw', id, start: pt, constrain: e.shiftKey };
    } else if (S.tool === 'text') {
      pushHist();
      const id = uid();
      S.shapes.push({ id, type: 'text', x: snapMM(px2mm(pt.x)), y: snapMM(px2mm(pt.y)), text: 'Text', fs: 14, fill: 'black', anchor: 'start' });
      S.selectedId = id;
      buildPropPanel();
    } else { // select tool: clear selection
      S.selectedId = null;
    }
    draw();
  });

  svg.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    const pt = clientToSvg(e);
    const s = S.shapes.find(x => x.id === dragging.id); if (!s) return;

    const dx_mm = snapMM(px2mm(pt.x)) - snapMM(px2mm(dragging.start.x));
    const dy_mm = snapMM(px2mm(pt.y)) - snapMM(px2mm(dragging.start.y));

    if (dragging.mode === 'move') {
      if (s.type === 'rect') { s.x += dx_mm; s.y += dy_mm; }
      if (s.type === 'circle') { s.cx += dx_mm; s.cy += dy_mm; }
      if (s.type === 'line') { s.x1 += dx_mm; s.y1 += dy_mm; s.x2 += dx_mm; s.y2 += dy_mm; }
      if (s.type === 'text') { s.x += dx_mm; s.y += dy_mm; }
      dragging.start = pt;
      renderShapes(); drawSelection(); buildPropPanelInputs(); // faster than full draw
      return;
    }

    if (dragging.mode === 'resize') {
      if (s.type === 'rect' && dragging.role === 'se') {
        const newW = Math.max(0.1, snapMM(px2mm(pt.x)) - s.x);
        const newH = Math.max(0.1, snapMM(px2mm(pt.y)) - s.y);
        s.w = newW; s.h = newH;
      }
      if (s.type === 'circle' && dragging.role === 'rad') {
        const r_px = Math.hypot(pt.x - mm2px(s.cx), pt.y - mm2px(s.cy));
        s.r = Math.max(0.1, snapMM(px2mm(r_px)));
      }
      if (s.type === 'line') {
        // handled by draw mode instead
      }
      renderShapes(); drawSelection(); buildPropPanelInputs();
      return;
    }

    if (dragging.mode === 'draw') {
      if (s.type === 'rect') {
        s.w = Math.max(0.1, snapMM(px2mm(pt.x)) - s.x);
        s.h = Math.max(0.1, snapMM(px2mm(pt.y)) - s.y);
      } else if (s.type === 'circle') {
        const r_px = Math.hypot(pt.x - mm2px(s.cx), pt.y - mm2px(s.cy));
        s.r = Math.max(0.1, snapMM(px2mm(r_px)));
      } else if (s.type === 'line') {
        let x2 = snapMM(px2mm(pt.x)), y2 = snapMM(px2mm(pt.y));
        if (dragging.constrain) {
          const dx = x2 - s.x1, dy = y2 - s.y1;
          if (Math.abs(dx) > Math.abs(dy)) y2 = s.y1; else x2 = s.x1;
        }
        s.x2 = x2; s.y2 = y2;
      }
      renderShapes(); drawSelection(); buildPropPanelInputs();
      return;
    }
  });

  svg.addEventListener('pointerup', () => { dragging = null; });

  function clientToSvg(e) {
    const rect = svg.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  // ---- Property panel ----
  function buildPropPanel() {
    const s = S.shapes.find(x => x.id === S.selectedId);
    $('#prop_panel').html(s ? propFormHtml(s) : '<div class="text-muted">Nothing selected</div>');
    bindPropPanelEvents();
  }
  function buildPropPanelInputs(){ // refresh inputs without rebuilding everything
    const s = S.shapes.find(x => x.id === S.selectedId); if (!s) return;
    for (const [k,v] of Object.entries(s)) {
      const el = document.querySelector(`#prop_panel [name="${k}"]`);
      if (el) el.value = v;
    }
  }
  function propFormHtml(s) {
    const common = `
      <div class="mb-2">
        <label class="form-label">Stroke</label>
        <input name="stroke" class="form-control form-control-sm" value="${s.stroke || 'black'}"/>
      </div>
      <div class="mb-2">
        <label class="form-label">Stroke Width (px)</label>
        <input name="sw" type="number" step="0.1" class="form-control form-control-sm" value="${s.sw || 1}"/>
      </div>`;
    if (s.type === 'rect') {
      return `
        <div class="mb-2"><b>Rectangle</b></div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">x (mm)</label><input name="x" type="number" step="0.1" class="form-control form-control-sm" value="${s.x}"/></div>
          <div class="col-6"><label class="form-label">y (mm)</label><input name="y" type="number" step="0.1" class="form-control form-control-sm" value="${s.y}"/></div>
        </div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">w (mm)</label><input name="w" type="number" step="0.1" class="form-control form-control-sm" value="${s.w}"/></div>
          <div class="col-6"><label class="form-label">h (mm)</label><input name="h" type="number" step="0.1" class="form-control form-control-sm" value="${s.h}"/></div>
        </div>
        <div class="mb-2"><label class="form-label">Fill</label><input name="fill" class="form-control form-control-sm" value="${s.fill || 'none'}"/></div>
        ${common}
      `;
    }
    if (s.type === 'circle') {
      return `
        <div class="mb-2"><b>Circle</b></div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">cx (mm)</label><input name="cx" type="number" step="0.1" class="form-control form-control-sm" value="${s.cx}"/></div>
          <div class="col-6"><label class="form-label">cy (mm)</label><input name="cy" type="number" step="0.1" class="form-control form-control-sm" value="${s.cy}"/></div>
        </div>
        <div class="mb-2"><label class="form-label">r (mm)</label><input name="r" type="number" step="0.1" class="form-control form-control-sm" value="${s.r}"/></div>
        <div class="mb-2"><label class="form-label">Fill</label><input name="fill" class="form-control form-control-sm" value="${s.fill || 'none'}"/></div>
        ${common}
      `;
    }
    if (s.type === 'line') {
      return `
        <div class="mb-2"><b>Line</b></div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">x1 (mm)</label><input name="x1" type="number" step="0.1" class="form-control form-control-sm" value="${s.x1}"/></div>
          <div class="col-6"><label class="form-label">y1 (mm)</label><input name="y1" type="number" step="0.1" class="form-control form-control-sm" value="${s.y1}"/></div>
        </div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">x2 (mm)</label><input name="x2" type="number" step="0.1" class="form-control form-control-sm" value="${s.x2}"/></div>
          <div class="col-6"><label class="form-label">y2 (mm)</label><input name="y2" type="number" step="0.1" class="form-control form-control-sm" value="${s.y2}"/></div>
        </div>
        ${common}
      `;
    }
    if (s.type === 'text') {
      return `
        <div class="mb-2"><b>Text</b></div>
        <div class="mb-2"><label class="form-label">Text</label><input name="text" class="form-control form-control-sm" value="${frappe.utils.escape_html(s.text || 'Text')}"/></div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">x (mm)</label><input name="x" type="number" step="0.1" class="form-control form-control-sm" value="${s.x}"/></div>
          <div class="col-6"><label class="form-label">y (mm)</label><input name="y" type="number" step="0.1" class="form-control form-control-sm" value="${s.y}"/></div>
        </div>
        <div class="row g-2 mb-2">
          <div class="col-6"><label class="form-label">Font size (px)</label><input name="fs" type="number" step="1" class="form-control form-control-sm" value="${s.fs || 14}"/></div>
          <div class="col-6"><label class="form-label">Anchor</label>
            <select name="anchor" class="form-select form-select-sm">
              <option ${s.anchor==='start'?'selected':''}>start</option>
              <option ${s.anchor==='middle'?'selected':''}>middle</option>
              <option ${s.anchor==='end'?'selected':''}>end</option>
            </select>
          </div>
        </div>
        <div class="mb-2"><label class="form-label">Fill</label><input name="fill" class="form-control form-control-sm" value="${s.fill || 'black'}"/></div>
        ${common}
      `;
    }
    return '';
  }
  function bindPropPanelEvents() {
    $('#prop_panel').off('input change').on('input change', 'input,select', (e) => {
      const s = S.shapes.find(x => x.id === S.selectedId); if (!s) return;
      const k = e.target.name;
      const isNum = ['x','y','w','h','cx','cy','r','x1','y1','x2','y2','sw','fs'].includes(k);
      s[k] = isNum ? parseFloat(e.target.value) : e.target.value;
      renderShapes(); drawSelection();
    });
  }

  // ---- Toolbar / controls ----
  function setTool(tool) {
    S.tool = tool;
    $('#tool_select,#tool_rect,#tool_circle,#tool_line,#tool_text').removeClass('active');
    ({ select: '#tool_select', rect: '#tool_rect', circle: '#tool_circle', line: '#tool_line', text: '#tool_text' }[tool] && $(({ select: '#tool_select', rect: '#tool_rect', circle: '#tool_circle', line: '#tool_line', text: '#tool_text' }[tool])).addClass('active'));
  }
  setTool('select');

  $('#tool_select').on('click', () => setTool('select'));
  $('#tool_rect').on('click', () => setTool('rect'));
  $('#tool_circle').on('click', () => setTool('circle'));
  $('#tool_line').on('click', () => setTool('line'));
  $('#tool_text').on('click', () => setTool('text'));

  $('#px_per_mm').on('input', (e) => { S.px_per_mm = Math.max(0.05, parseFloat(e.target.value) || 1.2); draw(); });
  $('#grid_mm').on('input', (e) => { S.grid_mm = Math.max(0.1, parseFloat(e.target.value) || 5); draw(); });
  $('#snap_toggle').on('change', (e) => { S.snap = e.target.checked; });

  $('#btn_undo').on('click', doUndo);
  $('#btn_redo').on('click', doRedo);
  $('#btn_delete').on('click', () => {
    if (!S.selectedId) return;
    pushHist();
    S.shapes = S.shapes.filter(s => s.id !== S.selectedId);
    S.selectedId = null; draw();
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'v' || e.key === 'V') setTool('select');
    if (e.key === 'r' || e.key === 'R') setTool('rect');
    if (e.key === 'c' || e.key === 'C') setTool('circle');
    if (e.key === 'l' || e.key === 'L') setTool('line');
    if (e.key === 't' || e.key === 'T') setTool('text');
    if (e.key === 'Delete' || e.key === 'Backspace') { $('#btn_delete').click(); }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); doUndo(); }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') { e.preventDefault(); doRedo(); }
  });

  // ---- Load / Save with Prototype.parameters ----
  async function loadPrototype() {
    if (!prototype) return;
    const doc = await frappe.db.get_doc('Prototype', prototype);
    S.protoDoc = doc;
    // read design_json param (stringified JSON)
    let design = null;
    for (const row of (doc.parameters || [])) {
      if ((row.param_name || '').toLowerCase() === 'design_json') {
        try { design = JSON.parse(row.param_value); } catch { design = null; }
      }
    }
    if (!design) {
      // default canvas starter: one rect showing prior Width/Height params if present
      const pmap = {};
      (doc.parameters || []).forEach(p => { pmap[(p.param_name || '').toLowerCase()] = p.param_value; });
      const W = parseFloat(pmap['width'] || '180') || 180;
      const H = parseFloat(pmap['height'] || '100') || 100;
      S.shapes = [
        { id: uid(), type: 'rect', x: 10, y: 10, w: W, h: H, stroke: 'black', sw: 1, fill: 'none' },
        { id: uid(), type: 'text', x: 10, y: H + 24, text: `W=${W}mm  H=${H}mm`, fs: 12, fill: '#555', anchor: 'start' }
      ];
      pushHist();
    } else {
      S.shapes = Array.isArray(design.shapes) ? design.shapes : [];
      S.grid_mm = design.grid_mm || S.grid_mm;
      S.px_per_mm = design.px_per_mm || S.px_per_mm;
      $('#grid_mm').val(S.grid_mm);
      $('#px_per_mm').val(S.px_per_mm);
    }
    draw();
  }

  async function savePrototype() {
    if (!S.protoDoc) return;
    // upsert design_json row
    const rows = S.protoDoc.parameters || [];
    const idx = rows.findIndex(r => (r.param_name || '').toLowerCase() === 'design_json');
    const payload = JSON.stringify({ px_per_mm: S.px_per_mm, grid_mm: S.grid_mm, shapes: S.shapes });
    if (idx >= 0) {
      rows[idx].param_value = payload;
    } else {
      rows.push({ doctype: 'Prototype Parameter', parenttype: 'Prototype', param_name: 'design_json', param_value: payload });
    }
    S.protoDoc.parameters = rows;

    // save
    await frappe.call({
      method: 'frappe.client.save',
      args: { doc: S.protoDoc }
    });
    frappe.show_alert({ message: 'Design saved to Prototype', indicator: 'green' });
  }

  // ---- JSON / SVG helpers ----
  $('#btn_save').on('click', savePrototype);
  $('#btn_reload').on('click', loadPrototype);

  $('#btn_export_json').on('click', () => {
    const blob = new Blob([JSON.stringify({ px_per_mm: S.px_per_mm, grid_mm: S.grid_mm, shapes: S.shapes }, null, 2)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${prototype || 'prototype'}-design.json`; a.click(); URL.revokeObjectURL(a.href);
  });

  $('#import_json').on('change', (e) => {
    const file = e.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const obj = JSON.parse(reader.result);
        pushHist();
        S.px_per_mm = obj.px_per_mm || S.px_per_mm;
        S.grid_mm = obj.grid_mm || S.grid_mm;
        S.shapes = Array.isArray(obj.shapes) ? obj.shapes : S.shapes;
        $('#px_per_mm').val(S.px_per_mm); $('#grid_mm').val(S.grid_mm);
        draw();
      } catch { frappe.msgprint('Invalid JSON.'); }
    };
    reader.readAsText(file);
  });

  $('#btn_download_svg').on('click', () => {
    // Serialize SVG; include grid + shapes (already in DOM)
    const xml = new XMLSerializer().serializeToString(svg);
    const blob = new Blob([xml], { type: 'image/svg+xml;charset=utf-8' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${prototype || 'prototype'}-design.svg`; a.click(); URL.revokeObjectURL(a.href);
  });

  // ---- Kickoff ----
  loadPrototype();
  draw();

  // Expose for console debugging (optional)
  window.__protoDesigner = { state: S, draw, savePrototype };
};

// Keep legacy alias
frappe.provide('frappe.pages.prototype_designer');
frappe.pages.prototype_designer = frappe.pages['prototype-designer'];
