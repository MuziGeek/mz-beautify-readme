# Continuous-scene composition

Use this gate for any one-board Hybrid hero that combines generated material with real project proof.

## Accepted lesson

The final asset must read as one illustration or environmental field, not as several source images placed beside one another. A single exported WebP can still look collaged when each source retains its own rectangle, border, background, or unrelated alignment.

## Required construction

- Keep one canvas background and one lighting/material language.
- Remove or match source backgrounds before composition. Prefer transparent foreground extraction, matched paper, or one shared environmental plane.
- Give proof and illustration one spatial relationship: background/foreground, object-on-table, wall/specimen field, or one shared path. Allow only intentional overlap that preserves proof legibility.
- Reuse one stroke, texture, palette, and annotation grammar across deterministic and raster layers.
- Keep the real proof exact. Extracting its background is allowed; redrawing, hallucinating, or replacing its content is not.
- Use a proof frame only when the real artifact is itself a card/window or the locked upstream composition explicitly requires a frame.

## Reject as collage

- a generated character rectangle next to a screenshot rectangle;
- proof inside a floating white card solely to hide a source background;
- multiple unrelated shadows, paper colors, corner radii, or perspective systems;
- visible rectangular seams or a cropped foreground fragment with no narrative purpose;
- decorative connectors that imply integration while objects remain spatially unrelated.

## Balance the canvas

Negative space must support the title, proof, gaze, or motion path. Do not strand it as a full-width empty band along the bottom or top merely because a previous Hero used that canvas size.

- Choose or crop the canvas after the content footprint is known. Do not treat `1200 × 420` or a square mobile canvas as universal.
- For a landscape one-board Hero, aim for meaningful vertical content occupancy of roughly `70–90%`; treat an edge band above about `18%` as suspicious when it is more than `2.5×` the opposite edge.
- Treat a full-width internal empty band above about `18%` of the canvas as suspicious too. Breathing room between copy and scene should feel like a transition, not an abandoned row.
- Keep outer top and bottom breathing room in the same visual order unless the locked composition gives one edge a communication job.
- Prefer a tighter canvas before stretching the illustration or inventing decorative filler.
- If upstream dimensions are locked, redistribute or scale existing material inside the canvas rather than changing the core decision.

Run `python scripts/audit_visual_balance.py path/to/hero.webp`. A numeric pass complements but does not replace visual inspection.

## Review gate

At desktop and mobile sizes verify:

1. The image reads as one scene when viewed for one second or blurred/squinted.
2. Removing borders would not make the composition fall apart.
3. Source-image rectangles and background seams are not visible.
4. The proof remains recognizable after intentional overlap.
5. At `360px`, the visual story still has one entry point and one dominant proof.
6. No unused full-width edge or internal band dominates the content footprint.

If any check fails, keep the core decision but rebuild the composition before `READY_FOR_REVIEW`.
