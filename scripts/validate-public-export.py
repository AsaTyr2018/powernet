#!/usr/bin/env python3
"""Basic repository validation for the public PowerNet export."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PRIVATE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\b[a-z0-9-]+\." + "internal" + r"\b",
        r"\b[a-z0-9-]+\.localdomain\b",
        r"\b[a-z0-9-]+\.lan\b",
        r"\b[a-z0-9-]+\.home\b",
        r"\bprivate[-_ ]ops\b",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        r"\.secret",
    ]
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    problems: list[str] = []

    for path in root.rglob("*"):
        if path.is_dir() or ".git" in path.parts:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.relative_to(root).as_posix() in {
            ".gitignore",
            "scripts/validate-public-export.py",
            "docs/modbus-discovery.md",
        }:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                problems.append(f"{path.relative_to(root)} matches {pattern.pattern}")

    template = root / "home-assistant" / "energy-solar-dashboard.template.json"
    json.loads(template.read_text(encoding="utf-8"))

    if problems:
        print("Private-reference validation failed:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("Public export validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
