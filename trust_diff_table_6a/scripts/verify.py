#!/usr/bin/env python3
"""
verify.py

Checks that every file referenced by a run log matches the SHA-256
recorded in that log. Exits 0 on full verification, 1 otherwise.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    bad = []
    n = 0
    for log in sorted(LOG_DIR.glob("*.seed*.jsonl")):
        rec = json.loads(log.read_text())
        # 1) config hash
        cfg_path = ROOT / rec["config_file"]
        if sha256_of(cfg_path) != rec["config_sha256"]:
            bad.append((log.name, "config_sha256 mismatch"))
        n += 1
        # 2) base config
        base_path = ROOT / "configs" / "_base.yaml"
        if sha256_of(base_path) != rec["base_config_sha256"]:
            bad.append((log.name, "base_config_sha256 mismatch"))
        n += 1
        # 3) checkpoints
        if isinstance(rec["checkpoints"], dict):
            for name, expected in rec["checkpoints"].items():
                p = ROOT / "checkpoints" / name
                if sha256_of(p) != expected:
                    bad.append((log.name, f"{name} sha256 mismatch"))
                n += 1

    if bad:
        for name, msg in bad:
            print(f"FAIL {name}: {msg}")
        print(f"{len(bad)} mismatch(es) over {n} check(s).")
        return 1
    print(f"OK — {n} hash checks across {len(list(LOG_DIR.glob('*.seed*.jsonl')))} run logs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
