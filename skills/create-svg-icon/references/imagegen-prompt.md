# ImageGen sheet prompt

Compose the prompt in this order: style, construction, palette, numbered metaphors, composition.

## Template

```text
Create a cohesive set of {linear|filled} interface icons.

Style: {plain-language style direction}.
Construction: {grid}; {stroke or silhouette rule}; {corner rule}; {angle set}; one clear idea per icon; consistent optical size and negative space; reuse shared sub-shapes; flat front-facing perspective; no background shadows; {brand motif if any}.
Palette: use only {hex list}. Do not shift hue, saturation, or value.

The requested icons in row-major order are:
1. {name} — {one concrete metaphor}
2. ...

A neat 4x4 grid on a perfectly uniform solid medium-grey background, exact hex #808080. The background has no gradient, vignette, lighting, texture, grain, or shadow. Use generous equal gaps. Center every requested icon in its cell at consistent optical size. No grid lines, borders, frames, text, labels, numbers, watermark, mockup, or drop shadow.

Place requested icons from cell 1 onward in row-major order. Leave every unused cell completely empty plain #808080. Do not add placeholders, dots, faint marks, or decorations to empty cells. Square image.
```

For fewer than 16 icons, reinforce exact centers as needed:

- columns: x = 12.5%, 37.5%, 62.5%, 87.5%;
- rows: y = 12.5%, 37.5%, 62.5%, 87.5%.

Keep each icon well inside its 25% × 25% cell. For a single icon, place it at x=12.5%, y=12.5% and leave the other 15 cells empty.

## Linear additions

```text
Uniform {N}-unit stroke, {cap} caps and {join} joins, no filled areas, no variable stroke, no double outline, and no decorative texture.
```

## Filled additions

```text
One solid filled silhouette color, no outline, no gradient, open transparent interior holes, and no tiny detached details that will fail at the target size.
```

## Prompt QA

Before generation, confirm the prompt contains exact hex colors, explicit empty-cell instructions, no-text exclusions, one metaphor per icon, and all frozen construction values. Avoid naming existing icon libraries or living designers as a style shortcut; describe observable geometry instead.
