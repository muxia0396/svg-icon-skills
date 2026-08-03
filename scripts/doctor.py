#!/usr/bin/env python3
"""Check whether the repository can run and be validated."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also require development dependencies used before publishing",
    )
    args = parser.parse_args()

    checks = {
        "python": {
            "ok": sys.version_info >= (3, 10),
            "value": platform.python_version(),
            "required": ">=3.10",
        },
        "pillow": {
            "ok": importlib.util.find_spec("PIL") is not None,
            "required": "Pillow>=10.4,<15 (runtime)",
        },
        "pyyaml": {
            "ok": importlib.util.find_spec("yaml") is not None,
            "required": "PyYAML>=6.0.2,<7 (development)",
        },
        "image_generation": {
            "ok": None,
            "required": "a callable ImageGen/image-generation tool in the host agent",
            "note": "Host capability cannot be detected from this local Python process.",
        },
    }

    required = ["python", "pillow"] + (["pyyaml"] if args.strict else [])
    ok = all(bool(checks[name]["ok"]) for name in required)
    requirement_file = "requirements-dev.txt" if args.strict else "requirements.txt"
    report = {
        "ok": ok,
        "mode": "strict" if args.strict else "runtime",
        "executable": sys.executable,
        "checks": checks,
        "next_step": None if ok else f"Install dependencies with: python -m pip install -r {requirement_file}",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
