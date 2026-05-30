#!/usr/bin/env python3
"""
_publish_snapshot.py — Howell cognition snapshot publisher for brain.rlv.lol

Reads the LOCAL-ONLY Howell daemon (/health/full at 127.0.0.1:7777), extracts a
SANITIZED, aggregate-only subset, and writes brain/snapshot.json next to this file.

Why this exists
---------------
brain.rlv.lol is a PUBLIC static site (GitHub Pages). The daemon is local-only —
a public page cannot fetch 127.0.0.1 (that means the *viewer's* machine, and https
pages block http-localhost as mixed content). So instead of exposing the daemon, we
publish a timestamped receipt of its vitals. This is the Ground= thesis applied to
the brain itself: verify everything, truth over comfort.

Safety contract (do not break)
------------------------------
ONLY aggregate, non-sensitive metrics are published. NEVER include:
  - filesystem paths, the api_key, ports/endpoints, IP addresses,
  - MCP server names, per-project local paths, raw agent IDs beyond a count.
If a future daemon field is sensitive, it must NOT be added to build_snapshot().

Usage
-----
  python3 _publish_snapshot.py                 # write brain/snapshot.json
  python3 _publish_snapshot.py --print         # print to stdout, do not write
  python3 _publish_snapshot.py --commit        # also git add+commit+push (opt-in)
  HOWELL_DAEMON_URL=http://127.0.0.1:7777 python3 _publish_snapshot.py
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DAEMON_URL = os.environ.get("HOWELL_DAEMON_URL", "http://127.0.0.1:7777").rstrip("/")
HERE = Path(__file__).resolve().parent
OUT = HERE / "snapshot.json"


def _fetch_health(timeout: float = 8.0) -> dict:
    url = f"{DAEMON_URL}/health/full"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _num(x, default=0):
    return x if isinstance(x, (int, float)) else default


def build_snapshot(health: dict) -> dict:
    """Extract a sanitized, public-safe aggregate view. No paths/keys/IPs/names."""
    daemon = health.get("daemon", {}) or {}
    threads = daemon.get("threads", {}) or {}
    threads_alive = sum(1 for t in threads.values() if isinstance(t, dict) and t.get("alive"))

    cortex = health.get("cortex", {}) or {}
    kg = health.get("knowledge_graph", {}) or {}
    agents = health.get("agents", {}) or {}
    tasks = health.get("tasks", {}) or {}
    offline = health.get("offline_readiness", {}) or {}
    speed = health.get("speed_layer", {}) or {}
    usage = (speed.get("usage", {}) or {}).get("window_5m", {}) or {}

    by_task = cortex.get("by_task", {}) or {}
    dreams = _num(by_task.get("dream")) + _num(by_task.get("dream_filter"))

    snap = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_timestamp": health.get("timestamp"),
        "daemon": {
            "status": daemon.get("status"),
            "uptime": daemon.get("uptime"),
            "threads_healthy": bool(daemon.get("threads_healthy")),
            "threads_alive": threads_alive,
            "threads_total": len(threads),
        },
        "cognition": {
            "cortex_status": cortex.get("status"),
            "archivist": bool(cortex.get("archivist")),
            "explorer": bool(cortex.get("explorer")),
            "vision": bool(cortex.get("vision")),
            "cortex_requests": _num(cortex.get("total_requests")),
            "hypotheses_verified": _num(by_task.get("verify_hypothesis")),
            "dreams": dreams,
            "consolidations": _num(by_task.get("consolidate")),
        },
        "knowledge_graph": {
            "entities": _num(kg.get("entities")),
            "relations": _num(kg.get("relations")),
            "observations": _num(kg.get("observations")),
            "structured_pct": _num(kg.get("structured_pct")),
            "last_sync": kg.get("last_sync"),
        },
        "memory": {
            "sessions": _num(agents.get("total_agents")),
            "notes": _num(agents.get("total_notes")),
            "note_coverage_pct": _num(agents.get("note_coverage_pct")),
        },
        "tasks": {
            "pending": _num(tasks.get("pending")),
            "completed": _num(tasks.get("completed")),
            "failed": _num(tasks.get("failed")),
        },
        "routing": {
            # local_pct over the most recent telemetry window — proof of local-first
            "local_pct": _num(usage.get("local_pct")),
            "offline_ready": bool(offline.get("offline_ready")),
        },
    }
    return snap


def _git_commit(path: Path) -> None:
    cwd = HERE.parent  # repo root (rlv-lol)
    rel = path.relative_to(cwd)
    subprocess.run(["git", "add", str(rel)], cwd=cwd, check=True)
    msg = f"brain: publish cognition snapshot {datetime.now(timezone.utc):%Y-%m-%dT%H:%MZ}"
    # Skip commit if nothing changed
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=cwd)
    if diff.returncode == 0:
        print("snapshot unchanged — nothing to commit")
        return
    subprocess.run(["git", "commit", "-m", msg], cwd=cwd, check=True)
    subprocess.run(["git", "push"], cwd=cwd, check=True)
    print("committed + pushed")


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish Howell cognition snapshot for brain.rlv.lol")
    ap.add_argument("--print", action="store_true", dest="to_stdout", help="print, do not write file")
    ap.add_argument("--commit", action="store_true", help="git add+commit+push after writing (opt-in)")
    args = ap.parse_args()

    try:
        health = _fetch_health()
    except Exception as exc:  # daemon down / unreachable
        print(f"ERROR: could not reach daemon at {DAEMON_URL}: {exc}", file=sys.stderr)
        return 2

    snap = build_snapshot(health)
    payload = json.dumps(snap, indent=2)

    if args.to_stdout:
        print(payload)
        return 0

    OUT.write_text(payload + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(payload)} bytes)")

    if args.commit:
        try:
            _git_commit(OUT)
        except subprocess.CalledProcessError as exc:
            print(f"git step failed: {exc}", file=sys.stderr)
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
