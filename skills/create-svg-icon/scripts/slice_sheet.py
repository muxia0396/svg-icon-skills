#!/usr/bin/env python3
"""Slice a grey-background icon sheet into transparent, centered PNG files."""

from __future__ import annotations

import argparse
from collections import deque
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - explicit runtime message
    print("Pillow is required: use an existing environment that provides PIL.", file=sys.stderr)
    raise SystemExit(2)


def parse_hex_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("background must be a six-digit hex color")
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("background must be a six-digit hex color") from exc


def remove_background(image: Image.Image, background: tuple[int, int, int], threshold: float) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = []
    feather = max(8.0, threshold * 0.45)
    source_pixels = (
        rgba.get_flattened_data()
        if hasattr(rgba, "get_flattened_data")
        else rgba.getdata()
    )
    for red, green, blue, alpha in source_pixels:
        distance = math.sqrt(
            (red - background[0]) ** 2
            + (green - background[1]) ** 2
            + (blue - background[2]) ** 2
        )
        if distance <= threshold:
            out_alpha = 0
        elif distance < threshold + feather:
            out_alpha = round(alpha * (distance - threshold) / feather)
        else:
            out_alpha = alpha
        pixels.append((red, green, blue, out_alpha))
    rgba.putdata(pixels)
    return rgba


def remove_edge_components(image: Image.Image, alpha_threshold: int = 8) -> Image.Image:
    """Remove foreground components clipped by a cell edge (normally neighbour bleed)."""
    width, height = image.size
    alpha = image.getchannel("A")
    alpha_values = (
        alpha.get_flattened_data()
        if hasattr(alpha, "get_flattened_data")
        else alpha.getdata()
    )
    values = bytes(alpha_values)
    foreground = bytearray(value > alpha_threshold for value in values)
    visited = bytearray(width * height)
    rejected = bytearray(width * height)

    for start in range(width * height):
        if not foreground[start] or visited[start]:
            continue
        queue: deque[int] = deque([start])
        visited[start] = 1
        component: list[int] = []
        touches_edge = False

        while queue:
            index = queue.popleft()
            component.append(index)
            x = index % width
            y = index // width
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                touches_edge = True
            if x > 0:
                neighbour = index - 1
                if foreground[neighbour] and not visited[neighbour]:
                    visited[neighbour] = 1
                    queue.append(neighbour)
            if x + 1 < width:
                neighbour = index + 1
                if foreground[neighbour] and not visited[neighbour]:
                    visited[neighbour] = 1
                    queue.append(neighbour)
            if y > 0:
                neighbour = index - width
                if foreground[neighbour] and not visited[neighbour]:
                    visited[neighbour] = 1
                    queue.append(neighbour)
            if y + 1 < height:
                neighbour = index + width
                if foreground[neighbour] and not visited[neighbour]:
                    visited[neighbour] = 1
                    queue.append(neighbour)

        if touches_edge:
            for index in component:
                rejected[index] = 1

    if any(rejected):
        result = image.copy()
        output_alpha = bytearray(values)
        for index, should_reject in enumerate(rejected):
            if should_reject:
                output_alpha[index] = 0
        result.putalpha(Image.frombytes("L", (width, height), bytes(output_alpha)))
        return result
    return image


def centered_square(image: Image.Image, size: int, padding: float) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    foreground = image.crop(bbox)
    usable = max(1, round(size * (1.0 - 2.0 * padding)))
    ratio = min(usable / foreground.width, usable / foreground.height)
    resized = foreground.resize(
        (max(1, round(foreground.width * ratio)), max(1, round(foreground.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
    return canvas


def safe_name(value: str, index: int) -> str:
    normalized = "-".join(value.strip().lower().replace("_", "-").split())
    return normalized or f"icon-{index + 1:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--grid", type=int, default=4)
    parser.add_argument("--count", type=int)
    parser.add_argument("--names", nargs="*")
    parser.add_argument("--background", type=parse_hex_color, default=parse_hex_color("#808080"))
    parser.add_argument("--threshold", type=float, default=32.0)
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--padding", type=float, default=0.10)
    args = parser.parse_args()

    if args.grid < 1 or args.size < 1:
        parser.error("grid and size must be positive")
    total = args.grid * args.grid
    count = total if args.count is None else args.count
    if not 1 <= count <= total:
        parser.error(f"count must be between 1 and {total}")
    if not 0 <= args.padding < 0.5:
        parser.error("padding must be in [0, 0.5)")
    if args.names and len(args.names) != count:
        parser.error("the number of --names must equal --count")

    sheet = Image.open(args.sheet).convert("RGBA")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    names = args.names or [f"icon-{index + 1:02d}" for index in range(count)]

    for index in range(count):
        row, column = divmod(index, args.grid)
        left = round(column * sheet.width / args.grid)
        top = round(row * sheet.height / args.grid)
        right = round((column + 1) * sheet.width / args.grid)
        bottom = round((row + 1) * sheet.height / args.grid)
        cell = sheet.crop((left, top, right, bottom))
        transparent = remove_background(cell, args.background, args.threshold)
        transparent = remove_edge_components(transparent)
        output = centered_square(transparent, args.size, args.padding)
        output.save(args.output_dir / f"{safe_name(names[index], index)}.png")

    print(f"Wrote {count} PNG files to {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
