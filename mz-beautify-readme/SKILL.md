---
name: mz-beautify-readme
description: Redesign, refresh, localize, or audit GitHub README homepages with a pinned proof-first design core and an identity-neutral public MZ visual route. Use for README audits, multilingual README and Hero sets, project-native continuous-scene heroes, GitHub-safe SVG, hybrid, raster, or explicitly authorized GIF delivery, including validated mz.visual-brief/1 handoffs and explicitly supplied visual Extensions.
---

# MZ Beautify README

Lock repository truth and the README design core before applying a public visual brief or an explicitly supplied Extension. Never infer identity from repository ownership.

## 1. Verify and load the upstream core

Run `python scripts/verify_upstream_snapshot.py`. Stop if verification fails. Read the pinned core at [references/upstream/SKILL.md](references/upstream/SKILL.md) and its directly linked production references. Never edit the byte-locked snapshot during ordinary execution.

## 2. Lock the README core decision

1. Choose `audit`, `readme`, or `asset-only`.
2. Inspect repository truth and lock audience, one-sentence value, primary proof, first successful action, proof sources, claims, and visible copy.
3. Let the pinned core choose its five-part theme, one composition, and one implementation route. GIF remains explicit opt-in.
4. Record these immutable choices under `coreDecision` in `mz.readme-brief/3`.

## 3. Resolve the public visual handoff

For direct use, create `mz.intent/1` with `readme-visual + mz-readme-project-native-v1` and resolve it through the bundled Engine Snapshot. For an external brief, run:

```text
python scripts/validate_visual_brief.py path/to/visual-brief.json
python scripts/validate_visual_brief.py path/to/visual-brief.json --extension path/to/explicit-extension
```

An Extension is valid only when supplied explicitly and hash-valid. It may change visual tokens, texture, marks, and permitted character treatment. It may not change repository facts, proof, copy, content order, `coreDecision`, dimensions, localization, implementation, motion authorization, GitHub safety, or acceptance rules.

Embed the resolved object as `visualBrief` in `mz.readme-brief/3`. Do not auto-discover an Extension, inspect the repository owner for identity, or install a missing dependency.

## 4. Validate and produce

Run `python scripts/validate_brief.py path/to/readme-brief.json`. For multiple languages, read [references/localization.md](references/localization.md), lock one copy layer per locale, and never reuse a text-bearing asset across languages.

Use the production guide selected by `coreDecision`:

- SVG → [references/upstream/svg-production.md](references/upstream/svg-production.md)
- Hybrid → [references/upstream/hybrid-svg-production.md](references/upstream/hybrid-svg-production.md)
- Raster → project-native and GitHub canvas guidance
- GIF → [references/upstream/motion-production.md](references/upstream/motion-production.md), only after explicit authorization

When comparing public and Extension variants, run `python scripts/compare_core_decisions.py public.json extension.json`. Differences outside `visualBrief` and `status` fail.

## 5. Preview and stop

Create `mz.readme-asset/3`, then run the README audit, asset-manifest validator, desktop/mobile previews, and visual-balance audit. Inspect every locale at 900px and 360px on light and dark GitHub surroundings.

Stop at `READY_FOR_REVIEW`. Do not commit, push, publish, create a remote, open a PR, or submit to a showcase without separate authorization.

## Resources

- `references/visual-engine/`: managed public Engine Snapshot.
- `references/brief.schema.json`: `mz.readme-brief/3`.
- `references/asset-manifest.schema.json`: `mz.readme-asset/3`.
- `references/upstream/`: pinned README design core.
- `scripts/`: visual-brief, README, localization, preview, and audit validation.
