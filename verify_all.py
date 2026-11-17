#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_all.py — one command, one verdict.

Standard library only. No network required for the offline checks.
Usage:
    python3 verify_all.py            # run from the repository root
    python3 verify_all.py --root DIR # explicit root
    python3 verify_all.py --json     # machine-readable output

Exit code 0 if every check passes, 1 otherwise.
Every check prints what it compared, not just its verdict, so a reader can
re-run any single row by hand.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

RESULTS = []


def record(group, name, ok, detail=""):
    RESULTS.append((group, name, bool(ok), detail))
    return ok


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cjk_count(text):
    return sum(1 for c in text if "\u4e00" <= c <= "\u9fff")


# ---------------------------------------------------------------- A structure
def check_structure(root):
    required = ["README.md", "checks.json"]
    for f in required:
        p = os.path.join(root, f)
        record("A structure", f"present: {f}", os.path.isfile(p),
               f"{os.path.getsize(p)} B" if os.path.isfile(p) else "missing")

    cj = os.path.join(root, "checks.json")
    if not os.path.isfile(cj):
        return None
    try:
        data = json.load(open(cj, encoding="utf-8"))
    except Exception as e:
        record("A structure", "checks.json parses", False, str(e))
        return None
    record("A structure", "checks.json parses", True, "valid JSON")

    for key in ["schema", "evidence_grades", "checks", "references"]:
        record("A structure", f"key: {key}", key in data,
               repr(data.get(key))[:60] if key in data else "absent")
    return data


# ----------------------------------------------------------------- digests
def check_digests(root, data, neighbour):
    if not data:
        return
    s5 = data.get("s5_outsider_test") or {}
    files = s5.get("manifest_files") or []
    record("B digests", "manifest_files non-empty", bool(files), f"{len(files)} entries")

    if not neighbour:
        record("B digests", "neighbour repository available", False,
               "evidence-gated-medical-agent-demo not found next to this root; "
               "digests cannot be recomputed (this row is a gap, not a pass)")
        return

    ok_n = bad_n = miss_n = 0
    for entry in files:
        p = os.path.join(neighbour, entry["path"])
        if not os.path.isfile(p):
            miss_n += 1
            continue
        got = sha256_file(p)
        if got == entry["sha256"]:
            ok_n += 1
        else:
            bad_n += 1
            record("B digests", f"mismatch: {entry['path']}", False,
                   f"recorded {entry['sha256'][:16]} actual {got[:16]}")

    record("B digests", "all recorded digests match", bad_n == 0 and miss_n == 0,
           f"match {ok_n} / mismatch {bad_n} / missing {miss_n}")
    record("B digests", "declared sha_mismatch equals recomputed",
           s5.get("sha_mismatch", -1) == bad_n,
           f"declared {s5.get('sha_mismatch')} recomputed {bad_n}")


# ------------------------------------------------------------- self-containment
RUNTIME_DEP = [
    r'<script[^>]+src\s*=\s*["\'](?:https?:)?//',
    r'<link[^>]+rel\s*=\s*["\']stylesheet["\'][^>]*href\s*=\s*["\'](?:https?:)?//',
    r'<(?:img|iframe)[^>]+src\s*=\s*["\'](?:https?:)?//',
]


def check_offline(root):
    htmls = [f for f in os.listdir(root) if f.lower().endswith(".html")]
    if not htmls:
        record("C offline", "html files present", False, "none found")
        return
    for f in sorted(htmls):
        s = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        hits = sum(len(re.findall(p, s)) for p in RUNTIME_DEP)
        record("C offline", f"no runtime dependency: {f}", hits == 0,
               f"{hits} external script/style/image reference(s)" if hits else "self-contained")


# --------------------------------------------------------------- executability
def check_demo(neighbour):
    if not neighbour:
        record("D demo", "demo repository available", False, "neighbour not found")
        return
    py = os.path.join(neighbour, "lgd_medai_demo.py")
    if not os.path.isfile(py):
        record("D demo", "lgd_medai_demo.py present", False, "missing")
        return
    try:
        r = subprocess.run([sys.executable, "lgd_medai_demo.py"], cwd=neighbour,
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        record("D demo", "demo runs", False, str(e))
        return

    out = r.stdout
    record("D demo", "exit code is 0", r.returncode == 0, f"exit {r.returncode}")
    for token in ["DENIED", "PAUSE", "ROLLBACK", "RESUMED"]:
        record("D demo", f"receipt: {token}", token in out,
               "found" if token in out else "absent from output")

    # Behavioural fingerprints. Presence of the four words alone is not enough:
    # a run can still print DENIED/PAUSE/ROLLBACK/RESUMED while the state machine
    # has stopped doing what the package claims. These four numbers are what the
    # trajectory should produce, and they move if anything upstream changes.
    for key, want in [("final_state", "RESUMED"), ("evidence_count", "9"),
                      ("log_entries", "20"), ("model_version", "v1.0")]:
        m = re.search(rf'"{key}"\s*:\s*("[^"]+"|[0-9]+)', out)
        got = m.group(1).strip('"') if m else None
        record("D demo", f"{key} == {want}", got == want, f"got {got}")

    m = re.search(r'"chain_digest"\s*:\s*"([0-9a-f]{64})"', out)
    record("D demo", "chain_digest is a 256-bit hex digest", bool(m),
           m.group(1)[:24] + "…" if m else "no 64-hex digest in output")
    if m:
        manifest_p = os.path.join(neighbour, "manifest.json")
        if os.path.isfile(manifest_p):
            mf = json.load(open(manifest_p, encoding="utf-8"))
            declared = (mf.get("anchors") or {}).get("chain_digest")
            if declared:
                record("D demo", "chain_digest matches manifest anchor", declared == m.group(1),
                       f"manifest {declared[:16]} / run {m.group(1)[:16]}")


# ------------------------------------------------------------------- language
def check_language(root):
    for f in os.listdir(root):
        if not f.lower().endswith((".md", ".json", ".html", ".cff")):
            continue
        s = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
        n = cjk_count(s)
        record("E language", f"no CJK in: {f}", n == 0, f"{n} CJK character(s)" if n else "0")


# --------------------------------------------------------------------- wording
BANNED = [
    "we are stronger", "better than", "nobody has published", "no one has published",
    "first and only", "fully compliant", "fully conformant",
    "end-to-end closed loop", "ecosystem closed loop",
]


def check_wording(root):
    hits = []
    for f in os.listdir(root):
        if not f.lower().endswith((".md", ".json", ".html", ".cff")):
            continue
        s = open(os.path.join(root, f), encoding="utf-8", errors="replace").read().lower()
        for b in BANNED:
            if b in s:
                hits.append(f"{f}:{b}")
    record("F wording", "no absolute superiority claim", not hits,
           "; ".join(hits) if hits else "none found")


# ------------------------------------------------------------------------- main
def find_neighbour(root):
    parent = os.path.dirname(os.path.abspath(root))
    cand = os.path.join(parent, "evidence-gated-medical-agent-demo")
    return cand if os.path.isdir(cand) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    data = check_structure(root)
    neighbour = find_neighbour(root)
    check_digests(root, data, neighbour)
    check_offline(root)
    check_demo(neighbour)
    check_language(root)
    check_wording(root)

    passed = sum(1 for r in RESULTS if r[2])
    total = len(RESULTS)

    if a.json:
        print(json.dumps({
            "root": root,
            "neighbour": neighbour,
            "passed": passed, "total": total,
            "rows": [{"group": g, "name": n, "ok": o, "detail": d} for g, n, o, d in RESULTS],
        }, indent=2))
    else:
        print("=" * 78)
        print("verify_all — one command, one verdict")
        print(f"root      {root}")
        print(f"neighbour {neighbour or '(not found)'}")
        print("=" * 78)
        cur = None
        for g, n, o, d in RESULTS:
            if g != cur:
                print(f"\n[{g}]")
                cur = g
            print(f"  {'PASS' if o else 'FAIL'}  {n:52s} {d}")
        print("\n" + "-" * 78)
        print(f"  {passed}/{total} passed")
        gaps = [r for r in RESULTS if not r[2]]
        if gaps:
            print(f"  {len(gaps)} not passing:")
            for g, n, o, d in gaps:
                print(f"    - {n}: {d}")
        print("-" * 78)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
