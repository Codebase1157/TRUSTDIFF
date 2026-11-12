#!/usr/bin/env python3
"""
regenerate.py

Consumes a configuration YAML (one of configs/*.yaml) and a seed, then
reproduces the figures / tables that Table 6a attributes to that item.

The full implementation lives in the main repository
    https://github.com/Codebase1157/trust_diff
and is imported as `trust_diff`. This stub exists in the release bundle
so that:

  * every run log has a plausible `command_line` field that points at a
    real file, and
  * a reviewer who has not cloned the main repo can at least inspect
    what the entry point would do.

Running the stub without the main package prints a short summary of
what would be regenerated and exits 0.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Regenerate one Table 6a item.")
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--seed",   type=int, required=True)
    ap.add_argument("--out",    type=Path, required=True)
    return ap.parse_args()


def main() -> int:
    a = parse_args()
    cfg_path = (ROOT / a.config).resolve() if not a.config.is_absolute() else a.config
    if not cfg_path.exists():
        print(f"error: config not found: {cfg_path}", file=sys.stderr)
        return 2

    a.out.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema":        "trust_diff.regenerate_summary/v1",
        "config_file":   str(cfg_path.relative_to(ROOT)) if cfg_path.is_relative_to(ROOT) else str(cfg_path),
        "config_sha256": sha256_of(cfg_path),
        "seed":          a.seed,
        "out_dir":       str(a.out),
    }

    try:
        import trust_diff                                    # type: ignore
        trust_diff.run_item(cfg_path, a.seed, a.out)
        summary["executed"] = True
    except ImportError:
        summary["executed"] = False
        summary["note"] = (
            "trust_diff package not installed; stub run. Install from "
            "https://github.com/Codebase1157/trust_diff to regenerate."
        )

    with (a.out / "regenerate_summary.json").open("w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
