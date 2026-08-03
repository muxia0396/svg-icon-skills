---
name: png-to-svg
description: Convert PNG and other raster icon artwork into clean, editable, transparent SVG geometry. Use when Codex must reconstruct a supplied PNG, JPG, WebP, screenshot crop, logo, glyph, wordmark, or generated icon as a true SVG; remove a baked background; preserve a combined mark; or audit and refine an SVG against its raster source. Do not use for ordinary photo vectorization or for SVG files that merely embed a bitmap.
---

# PNG to SVG

Reconstruct the visible foreground as deliberate vector geometry. Treat the raster as evidence, not as content to wrap inside an SVG.

Resolve `<skill-dir>` to the directory containing this file. Resolve all bundled paths from it.

## Hard requirements

- Produce real SVG primitives and paths. Never use `<image>`, raster data URLs, `foreignObject`, CSS background images, or external asset references.
- Leave the SVG canvas transparent and exclude every source-background pixel.
- Preserve the requested lockup, spacing, alignment, palette, negative space, and optical weight.
- Prefer the fewest clean primitives and Bézier points that explain the raster. Do not ship a noisy automatic trace.
- Do not search for an original SVG or substitute an icon-library asset. Reconstruct only from the supplied raster and user facts.
- State genuine ambiguity instead of inventing hidden geometry.

## Workflow

### 1. Inspect the source

View the original at native size and zoomed in. Record:

- canvas dimensions, alpha channel, and likely background;
- foreground bounds and intended whitespace;
- dominant colors and antialiasing fringe;
- symmetry axes, repeated widths, radii, angles, and negative spaces;
- whether the form is best explained by strokes, fills, or both;
- whether several visible parts form one lockup or separate assets.

For an opaque source, explicitly identify and remove the background. For a textured or ambiguous background, separate the intended foreground semantically and inspect every edge.

### 2. Form a geometry model

Read `references/geometry-and-qa.md`. Start with the lowest adequate complexity:

1. circles, ellipses, lines, polylines, rectangles, rounded rectangles, and arcs;
2. small primitive composites and negative-space cutouts;
3. a few deliberate cubic curves with tangent continuity;
4. a simplified custom outline only for a genuinely irregular silhouette.

For line icons, test a centerline-stroke model before drawing both edges as an outline. Infer a shared stroke width, caps, joins, and corner language. For filled icons, reconstruct the silhouette and open interior holes rather than painting them with the source background color.

### 3. Author the SVG

Use a tight `viewBox` unless source whitespace is intentional. Use semantic ids, explicit colors, readable coordinates, and reusable definitions only when they reduce complexity. Prefer `currentColor` when the user wants a themeable monochrome UI icon; otherwise preserve explicit colors.

Keep the graphic editable:

- retain simple primitives when they express the form clearly;
- use `fill-rule="evenodd"` or masks for true cutouts;
- avoid unnecessary transforms, clipping, filters, and path knots;
- do not add metadata, editor cruft, or hidden fallback rasters.

### 4. Audit and render

Run the bundled dependency-free audit after every structural rewrite:

```bash
python <skill-dir>/scripts/svg_audit.py output.svg --report output.audit.json
```

Any raster embedding, script, `foreignObject`, external reference, invalid root, or missing `viewBox` is a hard failure.

Render the SVG at the source reference size using an available browser, SVG viewer, or existing renderer. Do not install a renderer unless the user asks. Compare the render against the source on both light and dark contrasting backgrounds.

### 5. Refine in order

Change only a few parameters per pass, in this order:

1. foreground separation, canvas, placement, scale, and optical centering;
2. topology, open/closed structure, and negative space;
3. extrema, symmetry, radii, corner positions, and shared angles;
4. stroke width, caps, joins, and local weight;
5. curve tangents, subpixel placement, and color.

Stop when the structure is clean and the reference-size render is visually faithful. A smooth primitive with correct topology is preferable to a jagged trace with marginally closer pixels.

## Acceptance gate

Deliver only when all are true:

- `svg_audit.py` exits successfully;
- the canvas is transparent and no background shape remains;
- the icon reads correctly at its intended size and at 200–400% zoom;
- curves, corners, endpoints, and holes are clean;
- repeated visual rules are consistent;
- the SVG contains only editable vector geometry;
- filenames are lowercase kebab-case and describe the icon.

Always deliver the `.svg`. Keep audit reports and comparison renders as QA evidence when they help; do not clutter the final handoff with intermediate masks or failed candidates.

## References

- `references/geometry-and-qa.md` — geometry recipes, optical corrections, and comparison criteria.
