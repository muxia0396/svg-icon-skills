---
name: create-svg-icon
description: Design new linear or filled SVG icons and cohesive icon sets through a mandatory raster-first workflow. Use when Codex must invent an icon concept, create branded UI icons, make matching navigation or feature icons, or extend an existing icon family. Always generate PNG concepts with ImageGen first, then invoke the sibling png-to-svg skill to reconstruct and audit the final SVG; never hand-author the final SVG before the PNG concept exists.
---

# Create SVG Icon

Create original icons through one fixed pipeline:

**design system → ImageGen PNG → visual approval → PNG-to-SVG reconstruction → SVG QA**

Resolve `<skill-dir>` to this skill directory and `<collection-dir>` to its parent. The required conversion skill is `<collection-dir>/png-to-svg/SKILL.md`.

## Non-negotiable workflow gate

- Read `references/icon-design-guide.md` completely before making design decisions.
- Use the host's callable ImageGen/image-generation tool to create the raster concept.
- Generate only **linear** or **filled** icon artwork unless the user explicitly expands the style scope.
- Do not draw, code, trace, or deliver the final SVG until a generated PNG concept has been inspected and accepted for conversion.
- After the PNG is accepted, load and follow the sibling `$png-to-svg` skill for every final icon.
- Never embed the generated PNG in the SVG. The PNG is design evidence; the SVG is a clean vector reconstruction.

If ImageGen is unavailable, stop and tell the user that the required first stage cannot run. Do not silently bypass it by drawing an SVG directly.

## 1. Define the icon system

Ask only for information that cannot be inferred from supplied product context. Otherwise make reasonable decisions and record a compact style spec:

- icon names and intended meanings;
- target size and usage context;
- linear or filled construction;
- live area, padding, optical sizing, angle set, and detail budget;
- stroke width/caps/joins for linear icons;
- corner language and fill rule;
- locked color hex values;
- one recurring brand motif, when appropriate;
- light/dark background requirements and active/inactive states.

For a set, write each concept as `name — one concrete metaphor`. Use one idea per icon and keep abstraction and detail density consistent.

Use `references/style-specs.md` as the baseline, then adapt it to the product rather than producing generic recolored symbols.

## 2. Compose the ImageGen prompt

Use `references/imagegen-prompt.md`. Include, in order:

1. the selected linear or filled style;
2. the construction system and optical rules;
3. the locked palette;
4. the numbered icon metaphors in row-major order;
5. the fixed sheet composition and exclusions.

For a set, generate one 4×4 sheet on uniform `#808080` grey. Put requested icons first in row-major order and require unused cells to remain completely empty. One sheet keeps the family visually coherent.

For one icon, still generate a 4×4 sheet with the icon in cell 1 and the other 15 cells empty. This preserves the same pipeline and gives generous crop space.

Call ImageGen directly with the composed prompt. Save the selected result as `raw/<set-name>-sheet.png`.

## 3. Inspect and iterate the PNG

Reject and regenerate when any of these appear:

- ambiguous metaphor or poor recognition at target size;
- mixed stroke weights, radii, perspectives, or detail levels;
- filled areas in a linear set or outlines in a pure filled set;
- text, labels, grid lines, frames, drop shadows, texture, or non-grey background;
- neighbor bleed, clipped shapes, inconsistent scale, or uneven optical centering;
- generic symbols that ignore the supplied brand motif or product meaning.

Do not proceed because a sheet is merely attractive. It must be reconstructable as clean vector geometry.

## 4. Slice the selected PNG

Use the bundled slicer. If Pillow is missing, install the repository runtime dependencies from its root before continuing:

```bash
python -m pip install -r <skill-dir>/requirements.txt
python <skill-dir>/scripts/slice_sheet.py raw/set-sheet.png work/png \
  --grid 4 --count 5 --names home search library profile settings
```

The script removes the fixed grey background and centers each foreground on a transparent square. Inspect every slice on magenta and dark backgrounds. Do not silently replace this deterministic step with an unverified crop.

## 5. Reconstruct every SVG

Load `<collection-dir>/png-to-svg/SKILL.md` and execute it separately for each accepted PNG. Preserve the frozen system spec across the set:

- reuse one stroke width, cap, join, corner radius, and angle vocabulary;
- reuse canonical sub-shapes for recurring parts;
- normalize live area and optical weight, not just raw bounds;
- keep interior holes transparent;
- use `currentColor` only when themeability is part of the requirement.

The generated raster is the visual source of truth, but clean systematic vector geometry takes precedence over antialiasing noise.

## 6. Validate the family

Render all SVGs together at the target size and at 4×. Check:

- immediate recognition without labels;
- consistent silhouette weight and negative space;
- matched stroke, corners, endpoints, angles, and density;
- optical alignment of circles, squares, diagonals, and asymmetric forms;
- legibility on required light and dark backgrounds;
- no raster embeds or external references in any SVG.

Regenerate the PNG concept when the underlying metaphor or style is wrong. Refine only the SVG when the concept is right but geometry is imperfect.

## Deliverables

Always deliver:

- lowercase kebab-case SVG files;
- the frozen style spec used for the family;
- a contact-sheet preview when more than one icon is created.

Keep the accepted PNG concepts as provenance inside the work output unless the user requests SVG-only delivery. Do not ship rejected generations or temporary masks.

## References

- `references/icon-design-guide.md` — mandatory aesthetic, semantic, grid, optical, and delivery guidance.
- `references/style-specs.md` — linear and filled baseline systems.
- `references/imagegen-prompt.md` — deterministic sheet prompt structure.
