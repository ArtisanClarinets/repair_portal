import csv, json, os, re, shlex
from collections import defaultdict, Counter
from datetime import datetime

import frappe
from frappe.database import Database

OUTPUT_DIR = None

def _outdir():
    global OUTPUT_DIR
    if OUTPUT_DIR:
        return OUTPUT_DIR
    site_path = frappe.get_site_path()
    OUTPUT_DIR = os.path.join(site_path, "private", "optimization")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR

def _wpath(name):
    return os.path.join(_outdir(), name)

def _write_csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def _rows(query, params=None):
    return frappe.db.sql(query, params or (), as_dict=True)

def _is_child(doctype):
    return frappe.db.get_value("DocType", doctype, "istable") == 1

def _table(doctype):
    return f"tab{doctype}"

def _is_system_table(tbl):
    return tbl.startswith("tab__") or tbl in {"_Global Search", "_User Permissions"}

def _get_all_doctypes():
    return frappe.get_all("DocType", fields=["name","issingle","istable","is_tree","is_virtual"])

def _dump_doctypes():
    rows = _get_all_doctypes()
    _write_csv(_wpath("01_doctypes.csv"), [
        [r.name, r.issingle, r.istable, r.is_tree, r.is_virtual] for r in rows
    ], ["doctype","issingle","istable","is_tree","is_virtual"])

def _dump_fields():
    rows = frappe.get_all("DocField",
            fields=["parent","fieldname","label","fieldtype","options","in_standard_filter","in_list_view","idx"],
            order_by="parent, idx")
    _write_csv(_wpath("02_fields.csv"), [
        [r.parent, r.fieldname, r.label, r.fieldtype, r.options, r.in_standard_filter, r.in_list_view, r.idx]
        for r in rows
    ], ["doctype","fieldname","label","fieldtype","options","in_standard_filter","in_list_view","idx"])

def _dump_indexes():
    sql = """
    SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS columns
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME LIKE 'tab%%'
    GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
    ORDER BY TABLE_NAME, INDEX_NAME;
    """
    rows = _rows(sql)
    _write_csv(_wpath("03_indexes.csv"), [
        [r.TABLE_NAME, r.INDEX_NAME, r.NON_UNIQUE, r.columns] for r in rows
    ], ["table","index","non_unique","columns"])

def _get_top_slow(from_minutes=120, limit=200):
    # from mysql.slow_log (requires log_output='TABLE')
    sql = f"""
    SELECT
      db, user_host, start_time, query_time, lock_time, rows_sent, rows_examined, sql_text
    FROM mysql.slow_log
    WHERE start_time >= NOW() - INTERVAL {from_minutes} MINUTE
      AND db = DATABASE()
      AND sql_text NOT LIKE 'SET %%'
      AND sql_text NOT LIKE 'SHOW %%'
    ORDER BY query_time DESC
    LIMIT {limit};
    """
    return _rows(sql)

def _dump_top_slow():
    rows = _get_top_slow()
    out = []
    for r in rows:
        out.append([
            r.db, r.start_time, float(str(r.query_time).split(':')[-1]),  # seconds
            float(str(r.lock_time).split(':')[-1]),
            r.rows_sent, r.rows_examined,
            re.sub(r"\s+", " ", (r.sql_text or "")).strip()[:5000]
        ])
    _write_csv(_wpath("04_top_slow_sql.csv"), out,
               ["db","start_time","query_sec","lock_sec","rows_sent","rows_examined","sql_text"])

def _extract_tables(sqltext):
    # very light heuristic: match `FROM `tabSomething`` and JOINs
    return re.findall(r"(?:FROM|JOIN)\s+`?(tab[0-9A-Za-z _-]+)`?", sqltext, re.I)

def _explain_query(sqltext):
    try:
        plan = frappe.db.sql("EXPLAIN FORMAT=JSON " + sqltext, as_dict=True)
        return plan[0]["EXPLAIN"]
    except Exception:
        return None

def _analyze_sql_and_explain():
    rows = _get_top_slow()
    explain_out = []
    for r in rows:
        sqltext = (r.sql_text or "").strip()
        if not sqltext or "mysql.slow_log" in sqltext:
            continue
        plan = _explain_query(sqltext)
        explain_out.append({
            "start_time": str(r.start_time),
            "query_time_s": float(str(r.query_time).split(':')[-1]),
            "tables": _extract_tables(sqltext),
            "sql": sqltext,
            "explain": json.loads(plan) if plan else None
        })
    with open(_wpath("05_explain.jsonl"), "w") as f:
        for row in explain_out:
            f.write(json.dumps(row) + "\n")

def _recommend_indexes():
    """
    Very pragmatic consigliere:
    - For each EXPLAIN, if a table scan or 'possible_keys' exists but 'key' is null,
      try to build a composite index from WHERE equality cols -> range cols -> ORDER BY cols.
    - Deduplicate and skip if an equal-or-better existing index already covers it (leftmost rule).
    """
    def parse_conditions(plan_table):
        cond_eq, cond_range, order_cols = [], [], []
        # WHERE conditions (from attached_condition) and sorting columns
        attached = (plan_table.get("attached_condition") or "") + " " + (plan_table.get("used_columns") or "")
        # equality: col = ? or col IN (...)
        for c in re.findall(r"`([A-Za-z0-9_]+)`\s*=\s*\?", attached):
            cond_eq.append(c)
        for c in re.findall(r"`([A-Za-z0-9_]+)`\s+IN\s*\(", attached, flags=re.I):
            cond_eq.append(c)
        # range: col >, >=, <, <=, BETWEEN
        for c in re.findall(r"`([A-Za-z0-9_]+)`\s*(?:>=|<=|>|<|BETWEEN)", attached, flags=re.I):
            cond_range.append(c)
        # order
        orderby = plan_table.get("order_by_subqueries") or plan_table.get("ordering_operations") or []
        # fallback: look in 'attached_condition' for ORDER BY `col`
        return cond_eq, cond_range, order_cols

    def existing_indexes(table):
        rows = _rows("""
            SELECT INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) cols
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            GROUP BY INDEX_NAME
        """, (table,))
        return {r.INDEX_NAME: (r.cols or "").split(",") for r in rows}

    def has_covering(existing, proposal_cols):
        p = tuple(proposal_cols)
        for name, cols in existing.items():
            if tuple(cols[:len(p)]) == p:
                return True
        return False

    recs = defaultdict(lambda: Counter())
    # read EXPLAIN rows
    if not os.path.exists(_wpath("05_explain.jsonl")):
        return
    with open(_wpath("05_explain.jsonl")) as f:
        for line in f:
            j = json.loads(line)
            plan = j.get("explain") or {}
            if not plan:
                continue
            for t in (plan.get("table") and [plan] or plan.get("query_block", {}).get("nested_loop", []) or []):
                tbl = t.get("table_name") or (t.get("table", {}) or {}).get("table_name")
                if not tbl or not tbl.startswith("tab"):
                    continue
                used_key = t.get("key")
                rows_examined = t.get("rows_examined_per_scan") or t.get("rows_examined") or 0
                # skip if already using an index effectively
                if used_key:
                    continue
                eq, rng, order_cols = parse_conditions(t)
                if not eq and not rng:
                    continue
                proposal = [*eq, *rng]  # order cols are tricky; append if not present
                for oc in order_cols:
                    if oc not in proposal:
                        proposal.append(oc)
                if not proposal:
                    continue
                recs[tbl][tuple(proposal)] += 1

    rows_out = []
    for tbl, combos in recs.items():
        existing = existing_indexes(tbl)
        for cols, weight in combos.most_common():
            cols = list(cols)
            if has_covering(existing, cols):
                continue
            rows_out.append([tbl, ",".join(cols), weight])

    _write_csv(_wpath("06_index_recommendations.csv"), rows_out,
               ["table","columns","observations"])

def _emit_patches():
    # Read recs and current indexes, then write patch_add_indexes.py and patch_drop_indexes.py
    recs = []
    if os.path.exists(_wpath("06_index_recommendations.csv")):
        with open(_wpath("06_index_recommendations.csv")) as f:
            next(f)
            for line in f:
                tbl, cols, weight = [x.strip() for x in line.split(",")]
                recs.append((tbl, cols.split(","), int(weight)))

    # Build safe add-index patch
    add_lines = [
        "import frappe",
        "",
        "def add_index_if_missing(table, cols, name=None, unique=False):",
        "    cols_list = cols if isinstance(cols, (list, tuple)) else [c.strip() for c in cols.split(',')]",
        "    idx_name = name or ('idx_' + '_'.join(cols_list[:4]))",
        "    exists = frappe.db.sql('''SELECT 1 FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s''', (table, idx_name))",
        "    if not exists:",
        "        frappe.db.add_index(table.replace('tab','',1), cols_list, index_name=idx_name, unique=unique)",
        "",
        "def execute():",
    ]
    for tbl, cols, _ in recs:
        add_lines.append(f"    add_index_if_missing('{tbl}', {cols!r})")

    with open(_wpath("patch_add_indexes.py"), "w") as f:
        f.write("\n".join(add_lines) + "\n")

    # Redundant index cleanup (left-prefix rule)
    redundant = []
    stat = _rows("""
        SELECT TABLE_NAME, INDEX_NAME,
               GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) cols,
               NON_UNIQUE
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
        GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
    """)
    by_table = defaultdict(dict)
    for r in stat:
        by_table[r.TABLE_NAME][r.INDEX_NAME] = (r.cols or "").split(",")

    for tbl, idxs in by_table.items():
        for a_name, a_cols in idxs.items():
            if a_name in ("PRIMARY",):  # keep PK
                continue
            for b_name, b_cols in idxs.items():
                if a_name == b_name:
                    continue
                # if A's columns are a left prefix of B's columns, A is a candidate redundant
                if len(a_cols) <= len(b_cols) and a_cols == b_cols[:len(a_cols)]:
                    redundant.append((tbl, a_name))

    seen = set()
    drop_lines = [
        "import frappe",
        "",
        "def drop_index_if_exists(table, index_name):",
        "    exists = frappe.db.sql('''SELECT 1 FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s''', (table, index_name))",
        "    if exists:",
        "        frappe.db.sql(f\"DROP INDEX `{ '{' }index_name{ '}' }` ON `{ '{' }table{ '}' }`\")",
        "",
        "def execute():",
    ]
    for tbl, idx in redundant:
        key = (tbl, idx)
        if key in seen:
            continue
        seen.add(key)
        drop_lines.append(f"    drop_index_if_exists('{tbl}', '{idx}')")

    with open(_wpath("patch_drop_indexes.py"), "w") as f:
        f.write("\n".join(drop_lines) + "\n")

def _emit_capabilities_and_js():
    # server: capabilities
    server_py = '''
import frappe

@frappe.whitelist()
def get_ui_capabilities(doctypes: list[str]|None=None):
    """Return per-doctype caps + user permissions (scopes)."""
    user = frappe.session.user
    if doctypes is None:
        doctypes = [d.name for d in frappe.get_all("DocType", pluck="name")]
    caps = {}
    for dt in doctypes:
        try:
            caps[dt] = {
                "read": frappe.has_permission(dt, "read"),
                "write": frappe.has_permission(dt, "write"),
                "create": frappe.has_permission(dt, "create"),
                "submit": frappe.has_permission(dt, "submit"),
                "cancel": frappe.has_permission(dt, "cancel"),
                "amend": frappe.has_permission(dt, "amend"),
            }
        except Exception:
            caps[dt] = {"read": False, "write": False, "create": False, "submit": False, "cancel": False, "amend": False}

    # user permission scopes (Link scoping)
    scopes = {}
    ups = frappe.get_all("User Permission", filters={"user": user},
                         fields=["allow","for_value"])
    for up in ups:
        scopes.setdefault(up.allow, set()).add(up.for_value)
    scopes = {k:list(v) for k,v in scopes.items()}

    return {"user": user, "caps": caps, "scopes": scopes}
'''
    with open(_wpath("capabilities.py"), "w") as f:
        f.write(server_py)

    # client: ui guards
    client_js = r'''
// Lightweight UI guards; include this from hooks.py app_include_js
frappe.provide("my_app");

my_app.apply_ui_guards = async function() {
  try {
    const doctypes = Object.keys(frappe.boot.doctype_count || {});
    const { message } = await frappe.call({
      method: "my_app.optimize.capabilities.get_ui_capabilities",
      args: { doctypes }
    });
    const caps = message.caps || {};
    // Listview buttons
    frappe.listview_settings = frappe.listview_settings || {};
    for (const dt of Object.keys(caps)) {
      const c = caps[dt];
      frappe.listview_settings[dt] = frappe.listview_settings[dt] || {};
      frappe.listview_settings[dt].onload = function(listview) {
        if (!c.create) {
          listview.page.btn_primary?.hide(); // "Add <Doctype>"
        }
      };
    }
    // Form guards
    frappe.ui.form.on("*", {
      refresh(frm) {
        const c = caps[frm.doctype] || {};
        // Create/Save/Submit buttons visibility
        if (!c.write) { frm.disable_save(); }
        if (!c.submit && frm.events?.before_submit) {
          frm.page.set_secondary_action_group && frm.page.set_secondary_action_group("hidden");
        }
        // Example: disable fields by permission level
        // (Server still enforces; this is UX only)
        if (!c.write) {
          (frm.fields || []).forEach(df => {
            frm.toggle_enable(df.fieldname, false);
          });
        }
      }
    });

    // Link field scoping via get_query using User Permissions scopes
    frappe.ui.form.on("*", {
      onload(frm) {
        const scopes = message.scopes || {};
        for (const [allow, values] of Object.entries(scopes)) {
          // For every Link to `allow`, constrain the query
          (frm.fields || []).filter(df => df.fieldtype === "Link" && df.options === allow)
            .forEach(df => {
              frm.set_query(df.fieldname, () => ({
                filters: { name: ["in", values] }
              }));
            });
        }
      }
    });

  } catch (e) {
    // Fail-safe: never block UI if capability call fails
    console.warn("UI guards init failed", e);
  }
};

// boot-time init
frappe.after_ajax(() => { my_app.apply_ui_guards(); });
'''
    js_dir = os.path.join(frappe.get_app_path("my_app"), "public", "js")
    os.makedirs(js_dir, exist_ok=True)
    with open(os.path.join(js_dir, "ui_guards.js"), "w") as f:
        f.write(client_js)

    hooks_snip = '''
# hooks.py additions
app_include_js = app_include_js + ["assets/my_app/js/ui_guards.js"] if 'app_include_js' in globals() else ["assets/my_app/js/ui_guards.js"]
'''
    with open(_wpath("hooks_snippet.txt"), "w") as f:
        f.write(hooks_snip)

@frappe.whitelist()
def scan():
    """Entry point: bench --site yoursite execute my_app.optimize.scan"""
    _dump_doctypes()
    _dump_fields()
    _dump_indexes()
    _dump_top_slow()
    _analyze_sql_and_explain()
    _recommend_indexes()
    _emit_patches()
    _emit_capabilities_and_js()
    return {"output_dir": _outdir()}
