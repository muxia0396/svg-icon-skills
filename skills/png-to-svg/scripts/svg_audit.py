#!/usr/bin/env python3
"""Dependency-free structural audit for editable SVG assets."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


FORBIDDEN_TAGS = {"image", "foreignObject", "script", "iframe", "object", "embed"}
LINK_ATTRIBUTES = {"href", "src"}
EVENT_ATTRIBUTE = re.compile(r"^on[a-z]+$", re.IGNORECASE)
URL_VALUE = re.compile(r"url\(([^)]+)\)", re.IGNORECASE)


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def is_external_reference(value: str) -> bool:
    cleaned = value.strip().strip("\"'")
    if not cleaned or cleaned.startswith("#"):
        return False
    lowered = cleaned.lower()
    return lowered.startswith(("http:", "https:", "file:", "data:", "//")) or "://" in lowered


def parse_viewbox(value: str | None) -> tuple[bool, str]:
    if not value:
        return False, "missing viewBox"
    parts = re.split(r"[\s,]+", value.strip())
    if len(parts) != 4:
        return False, "viewBox must contain four numbers"
    try:
        nums = [float(part) for part in parts]
    except ValueError:
        return False, "viewBox contains a non-numeric value"
    if not all(math.isfinite(number) for number in nums):
        return False, "viewBox contains a non-finite value"
    if nums[2] <= 0 or nums[3] <= 0:
        return False, "viewBox width and height must be positive"
    return True, ""


def audit(path: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}

    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return {"ok": False, "errors": [f"cannot parse SVG: {exc}"], "warnings": [], "elements": {}}

    if local_name(root.tag) != "svg":
        errors.append("root element is not <svg>")

    valid_viewbox, viewbox_error = parse_viewbox(root.attrib.get("viewBox"))
    if not valid_viewbox:
        errors.append(viewbox_error)

    root_style = " ".join(
        [root.attrib.get("style", ""), root.attrib.get("fill", "")]
    ).lower()
    if "background" in root_style:
        warnings.append("root styling mentions a background; confirm that the canvas remains transparent")

    for element in root.iter():
        tag = local_name(element.tag)
        counts[tag] = counts.get(tag, 0) + 1
        if tag in FORBIDDEN_TAGS:
            errors.append(f"forbidden element <{tag}>")

        for raw_name, raw_value in element.attrib.items():
            name = local_name(raw_name)
            value = str(raw_value)
            if EVENT_ATTRIBUTE.match(name):
                errors.append(f"event handler attribute {name} on <{tag}>")
            if name in LINK_ATTRIBUTES and is_external_reference(value):
                errors.append(f"external reference in {name} on <{tag}>")
            for match in URL_VALUE.finditer(value):
                if is_external_reference(match.group(1)):
                    errors.append(f"external url() reference on <{tag}>")

    if sum(counts.get(name, 0) for name in ("path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "use")) == 0:
        warnings.append("SVG contains no common visible vector geometry")

    return {
        "ok": not errors,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "elements": dict(sorted(counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    result = audit(args.svg)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
