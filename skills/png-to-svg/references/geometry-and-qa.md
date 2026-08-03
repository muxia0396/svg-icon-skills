# Geometry and QA reference

## Geometry recipes

### Stroke-authored icons

- Infer a centerline from paired raster edges and use one shared stroke width.
- Prefer `round` caps and joins only when the source supports them; do not round every style by habit.
- Place horizontal and vertical strokes on pixel-aware coordinates at the intended render size.
- Use arcs or smooth cubic curves for rounded turns. Avoid many short line segments.
- Compare endpoint position and tangent before changing stroke width.

### Fill-authored icons

- Build silhouettes from primitives and a small number of paths.
- Keep holes transparent with compound paths, masks, or boolean-equivalent geometry.
- Use the same corner-radius language across related forms.
- Remove overlaps and invisible duplicate shapes that complicate later editing.

### Curves

- Put anchors at meaningful extrema and topology changes.
- Keep handles tangent across smooth joins.
- Mirror control points only where real symmetry is visible.
- Use fewer points; add one only when it fixes a specific measured mismatch.

### Symmetry and repetition

- Establish a symmetry axis before tuning local detail.
- Share centers, radii, widths, gaps, and angles wherever the evidence supports it.
- Reuse canonical sub-shapes in a family rather than redrawing nearly identical parts.

### Optical correction

- Circles and diagonals often need to extend slightly beyond square keylines to appear equal in size.
- Filled forms usually need more negative space than line forms at the same nominal bounds.
- Asymmetric icons should be centered by perceived mass, not bounding-box center alone.
- Judge at intended size first; zoom is for detecting defects, not deciding perceived weight.

## Comparison order

Evaluate in this order so cosmetic tuning does not hide structural errors:

1. transparent background and foreground bounds;
2. canvas, scale, placement, and optical center;
3. topology and negative space;
4. extrema, radii, symmetry, and repeated gaps;
5. stroke width, caps, joins, and filled weight;
6. curve smoothness and color.

Inspect on at least two contrasting backgrounds. At 200–400% zoom, reject flat spots, cusps, stray nodes, clipped strokes, accidental seams, and antialias-colored background remnants.

## SVG hygiene

- Require a finite numeric `viewBox` with positive width and height.
- Reject `<image>`, `<foreignObject>`, `<script>`, external `href`, event-handler attributes, and remote CSS.
- Allow internal fragment references such as `url(#gradient)` and `href="#shape"`.
- Prefer explicit `fill="none"` on stroke-only elements.
- Avoid editor namespaces and unused definitions.
