# Muzi crayon production

Use this optional Overlay resource only after the pinned upstream core has locked the composition and implementation, and only when Muzi actively communicates one project judgment or mechanism. It must not introduce a different composition, proof object, canvas size, or production route.

## Identity references

Load:

- `assets/identity/muzi-crayon-master.png` for face, hair, sunglasses, and upper-body identity.
- `assets/identity/muzi-crayon-fullbody-style.png` for outfit and full-body proportions when the scene shows more than a half body.
- `assets/identity/muzi-crayon-cat-master.png` only when `companionMode=include`.

These references lock identity and medium, not their backgrounds, props, poses, labels, or composition. Do not pass an action index or multiple action images to generation.

## Shot specification

Write:

```text
Core judgment:
Information structure: single-point | comparison | sequence | state | environment | focus
Composition: centered | side-by-side | character-action | object-closeup | environment-metaphor | mini-metaphor | sequence | information-focus | emotion-closeup
Density: minimal | narrative
Named objects and roles:
Story flow:
Muzi action:
Companion mode and rationale:
Cat pose and placement:
Quiet area:
Locked labels:
```

Use `minimal` for 1–3 objects and `narrative` for 3–6. Do not invent facts or objects to fill space.

## Visual DNA

- Prefer a `1672 × 941` 16:9 PNG source. When the active generator returns a fixed native canvas, record the actual dimensions and preserve aspect ratio during deterministic composition. The published README hero still uses the exact validated output size.
- Use a warm-white background with about one-third calm negative space.
- Use uneven deep-navy wax-crayon outer lines, mustard flat blocks, rust-red key accents, warm-white, skin tone, and gray-brown support colors.
- Use muted ice blue only for included cat eyes.
- Keep visible crayon grain, limited flat fills, adult big-head/small-body proportions, shoulder-length dark hair, sunglasses on the head, black varsity jacket, charcoal loose straight-leg trousers, and black-and-white sneakers.

Avoid photography, gradients, realistic skin or hair, realistic fur strands, 3D, polished cel anime, presentation grids, platform UI, logos, watermarks, extra people, unrelated brand mascots, moss green, and unconfirmed text.

## Active participation

Muzi must inspect, sort, connect, decide, build, test, repair, explain, retrieve, share, or deliver. Describe hands, gaze, body direction, and relation to the main object. Do not let him merely smile beside a finished result.

## Cat policy

Include one small long-haired colorpoint Ragdoll only for a calm minimal scene. Keep cream long fur, deep-navy/gray-brown face, ears, paws and plume tail, and muted ice-blue eyes. Place it beside Muzi, no larger than about one-third of Muzi, echoing gaze or emotion only.

Exclude it from comparison, sequence, narrative density, stop-check, and strict technical diagrams. Never give it a label, arrow, prop, workflow role, corner watermark position, collar, bow, clothing, or extra companion.

## Image generation

Use the built-in `imagegen` path. Keep exact repository names, versions, commands, and technical labels out of the generated layer. Generate the subject or scene, inspect it, then add exact copy in the deterministic composition.

Regenerate at most twice for identity, anatomy, medium, participation, composition, or cat failures. Make one targeted change per iteration. If it still fails, set `VALIDATION_FAILED` and stop.
