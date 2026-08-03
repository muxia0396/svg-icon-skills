#!/usr/bin/env python3
"""Portable repository validation for both bundled Agent Skills."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (ROOT / "skills" / "png-to-svg", ROOT / "skills" / "create-svg-icon")
REQUIRED_REPOSITORY_FILES = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / ".gitattributes",
    ROOT / ".gitignore",
    ROOT / ".github" / "workflows" / "validate.yml",
    ROOT / "requirements.txt",
    ROOT / "requirements-dev.txt",
)
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def load_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing opening frontmatter delimiter")
    try:
        raw, _body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing frontmatter delimiter") from exc
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")
    return data


def validate_skill(skill: Path) -> list[str]:
    errors: list[str] = []
    metadata = load_frontmatter(skill / "SKILL.md")
    expected_name = skill.name
    if set(metadata) != {"name", "description"}:
        errors.append(f"{skill}: frontmatter must contain only name and description")
    if metadata.get("name") != expected_name:
        errors.append(f"{skill}: name must equal folder name {expected_name!r}")
    description = metadata.get("description")
    if not isinstance(description, str) or len(description.strip()) < 40:
        errors.append(f"{skill}: description is missing or too short")

    openai_path = skill / "agents" / "openai.yaml"
    ui = yaml.safe_load(openai_path.read_text(encoding="utf-8"))
    interface = ui.get("interface", {}) if isinstance(ui, dict) else {}
    short = interface.get("short_description", "")
    prompt = interface.get("default_prompt", "")
    if not 25 <= len(short) <= 64:
        errors.append(f"{openai_path}: short_description must contain 25-64 characters")
    if f"${expected_name}" not in prompt:
        errors.append(f"{openai_path}: default_prompt must mention ${expected_name}")
    return errors


def compile_scripts() -> list[str]:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        if ".venv" in path.parts or ".skill-test" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"{path}: {exc}")
    return errors


def audit_regression() -> list[str]:
    audit = ROOT / "skills" / "png-to-svg" / "scripts" / "svg_audit.py"
    good = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg>'
    bad = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><image href="data:image/png;base64,AA=="/></svg>'
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        good_path = temp_dir / "good.svg"
        bad_path = temp_dir / "bad.svg"
        good_path.write_text(good, encoding="utf-8")
        bad_path.write_text(bad, encoding="utf-8")
        good_run = subprocess.run([sys.executable, str(audit), str(good_path)], capture_output=True, text=True)
        bad_run = subprocess.run([sys.executable, str(audit), str(bad_path)], capture_output=True, text=True)
        if good_run.returncode != 0:
            errors.append("svg_audit rejected a valid vector-only SVG")
        if bad_run.returncode == 0:
            errors.append("svg_audit accepted an embedded raster")
    return errors


def slicer_regression() -> list[str]:
    slicer = ROOT / "skills" / "create-svg-icon" / "scripts" / "slice_sheet.py"
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        sheet_path = temp_dir / "sheet.png"
        output_dir = temp_dir / "slices"
        sheet = Image.new("RGB", (400, 400), "#808080")
        draw = ImageDraw.Draw(sheet)
        draw.rounded_rectangle((25, 25, 75, 75), radius=10, fill="#246BFD")
        draw.ellipse((125, 25, 175, 75), fill="#20C7A6")
        sheet.save(sheet_path)
        run = subprocess.run(
            [
                sys.executable,
                str(slicer),
                str(sheet_path),
                str(output_dir),
                "--grid",
                "4",
                "--count",
                "2",
                "--names",
                "rounded-square",
                "circle",
                "--size",
                "128",
            ],
            capture_output=True,
            text=True,
        )
        if run.returncode != 0:
            errors.append(f"slice_sheet regression failed: {run.stderr.strip()}")
            return errors
        for name in ("rounded-square.png", "circle.png"):
            path = output_dir / name
            if not path.exists():
                errors.append(f"slice_sheet did not create {name}")
                continue
            result = Image.open(path).convert("RGBA")
            if result.getchannel("A").getbbox() is None:
                errors.append(f"slice_sheet produced an empty {name}")
            if result.getpixel((0, 0))[3] != 0:
                errors.append(f"slice_sheet did not preserve transparent padding in {name}")
    return errors


def repository_hygiene() -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_REPOSITORY_FILES:
        if not path.is_file():
            errors.append(f"missing repository file: {path.relative_to(ROOT)}")

    publishable: list[Path] = []
    publishable.extend(path for path in (ROOT / "skills").rglob("*") if path.is_file())
    publishable.extend(path for path in (ROOT / "scripts").glob("*.py") if path.is_file())
    publishable.extend(path for path in REQUIRED_REPOSITORY_FILES if path.is_file())

    for path in publishable:
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append(f"{path.relative_to(ROOT)} is not UTF-8 text: {exc}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in {path.relative_to(ROOT)}: {pattern.pattern}")
        unfinished_markers = ("TO" + "DO", "FIX" + "ME")
        if any(marker in text for marker in unfinished_markers):
            errors.append(f"unfinished marker in {path.relative_to(ROOT)}")

    workflow = ROOT / ".github" / "workflows" / "validate.yml"
    if workflow.is_file():
        workflow_text = workflow.read_text(encoding="utf-8")
        for expected in ("actions/checkout@v7", "actions/setup-python@v6", "scripts/validate_all.py"):
            if expected not in workflow_text:
                errors.append(f"validation workflow is missing {expected}")
    return errors


def main() -> int:
    errors: list[str] = []
    for skill in SKILLS:
        try:
            errors.extend(validate_skill(skill))
        except Exception as exc:  # report all repository issues in one pass
            errors.append(str(exc))
    errors.extend(compile_scripts())
    errors.extend(audit_regression())
    errors.extend(slicer_regression())
    errors.extend(repository_hygiene())
    result = {"ok": not errors, "skills": [skill.name for skill in SKILLS], "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
