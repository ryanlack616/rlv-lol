#!/usr/bin/env python3
"""Build the RL Ventures LOC dashboard.

Reads the local-only LOC telemetry snapshot, writes a sanitized aggregate
(loc/loc_snapshot.json) and regenerates the self-contained dashboard page
(loc/index.html). Mirrors the brain/_publish_snapshot.py pattern.

SAFETY: aggregate + project-relative paths only. No absolute filesystem
paths, no keys, no machine identifiers leave this script.

Usage:
    python3 loc/_build_loc.py            # build from default telemetry path
    python3 loc/_build_loc.py --src X    # build from a specific snapshot json
    python3 loc/_build_loc.py --print    # print the aggregate, write nothing
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.expanduser("~/rje/howell-persist/telemetry/loc_latest.json")
SNAPSHOT_OUT = os.path.join(HERE, "loc_snapshot.json")
HTML_OUT = os.path.join(HERE, "index.html")


def build_snapshot(src: str) -> dict:
    with open(src, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    projects = raw.get("projects", {})
    ranked = sorted(
        ({"name": k, **v} for k, v in projects.items()),
        key=lambda p: p.get("total", 0),
        reverse=True,
    )

    largest = [
        {"lines": f["lines"], "project": f["project"], "path": f["path"]}
        for f in raw.get("largest_files", [])
    ]

    snap = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_ts": raw.get("ts"),
        "total_lines": raw.get("total", 0),
        "file_count": raw.get("file_count", 0),
        "project_count": len(projects),
        "by_category": raw.get("by_category", {}),
        "code_breakdown": raw.get("code_breakdown", {}),
        "by_ext": raw.get("by_ext", {}),
        "projects": ranked,
        "largest_files": largest,
    }
    return snap


def render_html(snap: dict) -> str:
    data_js = json.dumps(snap, separators=(",", ":"))
    # Escape closing script tags defensively.
    data_js = data_js.replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__DATA__", data_js)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RL Ventures — Lines of Code</title>
<meta name="description" content="Lines of code across the RL Ventures workspace. Where proof meets practice.">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0c;
    --surface: #101013;
    --surface-2: #161619;
    --border: #1e1e24;
    --text: #d0d0d8;
    --text-dim: #55555f;
    --text-mid: #888892;
    --accent: #c4826e;
    --accent-warm: #a3855a;
    --green: #6e9e7a;
    --amber: #c4a35a;
    --red: #c46a5a;
    --blue: #6e88a3;
    --font: 'IBM Plex Mono', 'Courier New', monospace;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg); color: var(--text);
    font-family: var(--font); font-size: 14px; line-height: 1.6;
    min-height: 100vh;
  }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .container { max-width: 880px; margin: 0 auto; padding: 0 1.5rem; }

  header { border-bottom: 1px solid var(--border); padding: 1.25rem 0; }
  header .container { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
  .wordmark { font-size: 0.85rem; letter-spacing: 0.08em; color: var(--text-mid); text-transform: uppercase; }
  .wordmark b { color: var(--accent); font-weight: 500; }
  .ts { font-size: 0.72rem; color: var(--text-dim); }

  .hero { padding: 2.5rem 0 1.5rem; border-bottom: 1px solid var(--border); }
  .hero h1 { font-size: 1.4rem; font-weight: 500; color: var(--text); letter-spacing: 0.02em; }
  .hero p { color: var(--text-mid); font-size: 0.82rem; margin-top: 0.4rem; }

  .totals { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px; background: var(--border); border: 1px solid var(--border); margin: 1.75rem 0; }
  .stat { background: var(--surface); padding: 1.1rem 1.25rem; }
  .stat .n { font-size: 1.55rem; font-weight: 400; color: var(--accent); letter-spacing: 0.01em; }
  .stat .l { font-size: 0.68rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.25rem; }

  section { margin: 2.25rem 0; }
  h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--text-mid); margin-bottom: 0.9rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border); }

  .bar { display: flex; height: 26px; width: 100%; border: 1px solid var(--border); overflow: hidden; margin-bottom: 0.75rem; }
  .bar span { display: block; height: 100%; }
  .legend { display: flex; flex-wrap: wrap; gap: 0.25rem 1.25rem; font-size: 0.74rem; color: var(--text-mid); }
  .legend i { display: inline-block; width: 9px; height: 9px; margin-right: 0.4rem; vertical-align: baseline; }

  table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  th, td { text-align: left; padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--border); }
  th { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim); font-weight: 400; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  tbody tr:hover { background: var(--surface); }
  .pname { color: var(--text); }
  .minibar { position: relative; height: 4px; background: var(--surface-2); margin-top: 4px; }
  .minibar > i { position: absolute; left: 0; top: 0; height: 100%; background: var(--accent-dim, #6b4538); }
  .muted { color: var(--text-dim); }
  .toggle { background: none; border: 1px solid var(--border); color: var(--text-mid); font-family: var(--font); font-size: 0.72rem; padding: 0.3rem 0.7rem; cursor: pointer; margin-top: 0.9rem; }
  .toggle:hover { border-color: var(--accent); color: var(--accent); }

  footer { border-top: 1px solid var(--border); padding: 1.5rem 0 2.5rem; margin-top: 2.5rem; font-size: 0.72rem; color: var(--text-dim); }
  footer a { color: var(--text-mid); }
  .note { font-size: 0.72rem; color: var(--text-dim); margin-top: 0.5rem; }
</style>
</head>
<body>
<header><div class="container">
  <div class="wordmark"><b>RL Ventures</b> · Lines of Code</div>
  <div class="ts" id="ts">—</div>
</div></header>

<main class="container">
  <div class="hero">
    <h1>The workspace, counted.</h1>
    <p>Every counted line across the active development tree. Vendored libraries, build artifacts, and generated bundles excluded.</p>
  </div>

  <div class="totals" id="totals"></div>

  <section>
    <h2>By category</h2>
    <div class="bar" id="catbar"></div>
    <div class="legend" id="catlegend"></div>
    <p class="note">Code splits into <span id="cb"></span>.</p>
  </section>

  <section>
    <h2>By language</h2>
    <table><thead><tr><th>Extension</th><th class="num">Lines</th><th class="num">Share</th></tr></thead>
    <tbody id="exttbody"></tbody></table>
  </section>

  <section>
    <h2>Projects <span class="muted" id="projcount"></span></h2>
    <table><thead><tr><th>Project</th><th class="num">Total</th><th class="num">Code</th></tr></thead>
    <tbody id="projtbody"></tbody></table>
    <button class="toggle" id="projtoggle">Show all</button>
  </section>

  <section>
    <h2>Largest single files</h2>
    <table><thead><tr><th>File</th><th class="num">Lines</th></tr></thead>
    <tbody id="bigtbody"></tbody></table>
  </section>
</main>

<footer><div class="container">
  Generated from local LOC telemetry · static snapshot · <a href="../">RL Ventures</a>
</div></footer>

<script>
const DATA = __DATA__;
const fmt = n => (n || 0).toLocaleString('en-US');
const CAT_COLORS = { code: 'var(--accent)', markup: 'var(--blue)', data: 'var(--amber)', docs: 'var(--green)' };

document.getElementById('ts').textContent =
  'snapshot ' + (DATA.source_ts || DATA.generated || '').replace('T', ' ').slice(0, 16);

const totals = [
  ['total_lines', 'Total lines'],
  ['file_count', 'Files'],
  ['project_count', 'Projects'],
];
document.getElementById('totals').innerHTML = totals.map(([k, l]) =>
  `<div class="stat"><div class="n">${fmt(DATA[k])}</div><div class="l">${l}</div></div>`
).join('') +
  `<div class="stat"><div class="n">${fmt((DATA.code_breakdown||{}).code)}</div><div class="l">Source code</div></div>`;

// Category bar
const cats = DATA.by_category || {};
const catTotal = Object.values(cats).reduce((a, b) => a + b, 0) || 1;
document.getElementById('catbar').innerHTML = Object.entries(cats)
  .sort((a, b) => b[1] - a[1])
  .map(([k, v]) => `<span style="width:${(v / catTotal * 100).toFixed(2)}%;background:${CAT_COLORS[k] || 'var(--text-dim)'}"></span>`)
  .join('');
document.getElementById('catlegend').innerHTML = Object.entries(cats)
  .sort((a, b) => b[1] - a[1])
  .map(([k, v]) => `<span><i style="background:${CAT_COLORS[k] || 'var(--text-dim)'}"></i>${k} · ${fmt(v)} (${(v / catTotal * 100).toFixed(0)}%)</span>`)
  .join('');
const cb = DATA.code_breakdown || {};
document.getElementById('cb').textContent =
  `${fmt(cb.code)} code, ${fmt(cb.comment)} comment, ${fmt(cb.blank)} blank`;

// Languages
const exts = Object.entries(DATA.by_ext || {}).sort((a, b) => b[1] - a[1]);
const extTotal = exts.reduce((a, b) => a + b[1], 0) || 1;
document.getElementById('exttbody').innerHTML = exts.map(([e, n]) =>
  `<tr><td>${e}</td><td class="num">${fmt(n)}</td><td class="num muted">${(n / extTotal * 100).toFixed(1)}%</td></tr>`
).join('');

// Projects
const projs = DATA.projects || [];
document.getElementById('projcount').textContent = `(${projs.length})`;
const maxProj = projs.length ? projs[0].total : 1;
function renderProjects(limit) {
  document.getElementById('projtbody').innerHTML = projs.slice(0, limit).map(p =>
    `<tr><td><span class="pname">${p.name}</span>
       <div class="minibar"><i style="width:${(p.total / maxProj * 100).toFixed(1)}%"></i></div></td>
     <td class="num">${fmt(p.total)}</td><td class="num muted">${fmt(p.code)}</td></tr>`
  ).join('');
}
let projExpanded = false;
renderProjects(15);
const projToggle = document.getElementById('projtoggle');
if (projs.length <= 15) { projToggle.style.display = 'none'; }
projToggle.addEventListener('click', () => {
  projExpanded = !projExpanded;
  renderProjects(projExpanded ? projs.length : 15);
  projToggle.textContent = projExpanded ? 'Show fewer' : 'Show all';
});

// Largest files
document.getElementById('bigtbody').innerHTML = (DATA.largest_files || []).slice(0, 12).map(f =>
  `<tr><td class="muted">${f.path}</td><td class="num">${fmt(f.lines)}</td></tr>`
).join('');
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the RL Ventures LOC dashboard.")
    ap.add_argument("--src", default=DEFAULT_SRC, help="LOC telemetry snapshot json")
    ap.add_argument("--print", dest="do_print", action="store_true", help="print aggregate, write nothing")
    args = ap.parse_args()

    snap = build_snapshot(args.src)

    if args.do_print:
        summary = {k: v for k, v in snap.items() if k not in ("projects", "largest_files", "by_ext")}
        summary["top_projects"] = [p["name"] for p in snap["projects"][:5]]
        print(json.dumps(summary, indent=2))
        return

    with open(SNAPSHOT_OUT, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2)
    with open(HTML_OUT, "w", encoding="utf-8") as fh:
        fh.write(render_html(snap))

    print(f"wrote {SNAPSHOT_OUT}")
    print(f"wrote {HTML_OUT}")
    print(f"  {snap['total_lines']:,} lines · {snap['file_count']:,} files · {snap['project_count']} projects")


if __name__ == "__main__":
    main()
