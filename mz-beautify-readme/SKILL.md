---
name: mz-beautify-readme
description: Redesign, refresh, localize, or audit GitHub README homepages using the pinned oil-oil/beautify-github-readme design core, with an optional Muzi Visual Overlay for Muzi-owned repositories. Use for README audits, multilingual README and Hero sets, project-native continuous-scene heroes, proof-first redesigns, MZ-branded assets, and GitHub-safe SVG, hybrid, raster, or explicitly authorized GIF delivery.
---

# MZ Beautify README

Use the exact upstream design system first. Muzi is a visual overlay, never a replacement design system.

## 1. Verify and load the upstream core

Run `python scripts/verify_upstream_snapshot.py`. Stop if verification fails.

Read the full pinned core at [references/upstream/SKILL.md](references/upstream/SKILL.md). Its relative references map to this package as follows:

- `references/content-architecture.md` → [references/upstream/content-architecture.md](references/upstream/content-architecture.md)
- `references/visual-direction.md` → [references/upstream/visual-direction.md](references/upstream/visual-direction.md)
- `references/project-native-hero.md` → [references/upstream/project-native-hero.md](references/upstream/project-native-hero.md)
- `references/github-readme-canvas.md` → [references/upstream/github-readme-canvas.md](references/upstream/github-readme-canvas.md)
- `references/svg-production.md` → [references/upstream/svg-production.md](references/upstream/svg-production.md)
- `references/hybrid-svg-production.md` → [references/upstream/hybrid-svg-production.md](references/upstream/hybrid-svg-production.md)
- `references/motion-production.md` → [references/upstream/motion-production.md](references/upstream/motion-production.md)
- `references/showcase-contribution.md` → [references/upstream/showcase-contribution.md](references/upstream/showcase-contribution.md)
- upstream scripts → `scripts/upstream/`

The snapshot and its files are locked by `upstream-lock.json`. Never edit them to add Muzi rules. Normal Skill execution is offline. Maintainers may run `python scripts/sync_upstream.py --check`; only an explicit maintenance task may use `--apply`.

## 2. Make and lock the core decision

Follow the upstream sequence without Muzi styling:

1. Choose exactly one scope: `audit`, `readme`, or `asset-only`.
2. Inspect repository truth and extract audience, one-sentence value, primary proof, first successful action, and claims requiring evidence.
3. Write the upstream five-part theme specification: palette, typography, shape, motif, and composition.
4. Choose one composition: `split`, `integrated`, `artifact-wall`, `background-proof`, or `title-only`.
5. Choose one implementation: `svg`, `hybrid`, `raster`, or `none`. GIF remains explicit opt-in.

Record these immutable choices under `coreDecision` in `mz.readme-brief/2`. Muzi must not alter them later.

## 3. Resolve the optional Overlay

Run:

```text
python scripts/resolve_overlay.py --repository owner/name --explicit auto
```

Routing priority is fixed:

1. Explicit user enable or disable wins.
2. Owner `MuziGeek` defaults to `muzi`.
3. Third-party and uncertain ownership default to `none`.
4. `MZ` appearing in a repository name is never ownership evidence.

For `overlay.id=none`, continue with the upstream project-native theme unchanged. For `overlay.id=muzi`, read [references/muzi-overlay.md](references/muzi-overlay.md). Read [references/muzi-crayon-production.md](references/muzi-crayon-production.md) only when a Muzi character has a concrete communication job.

## 4. Validate the brief before production

Use [brief.schema.json](references/brief.schema.json), then run:

```text
python scripts/validate_brief.py path/to/readme-brief.json
```

Hero copy requires only a project `title` and concrete `value`. `context`, `processCue`, and `proofLabels` are optional and project-driven. Keep exact claims, commands, and labels deterministic. Preserve proof sources and lock every visible string before `READY_FOR_REVIEW`.

When the repository has multiple README languages, read [references/localization.md](references/localization.md). Record `localization`, generate one deterministic copy layer per locale, and never reuse a text-bearing asset across languages.

When comparing overlay-on and overlay-off variants, run `python scripts/compare_core_decisions.py none.json muzi.json`. Content, proof, copy, composition, implementation, and motion decisions must remain identical.

## 5. Produce through the upstream route

Use the production guide selected by the core:

- SVG → [references/upstream/svg-production.md](references/upstream/svg-production.md)
- Hybrid → [references/upstream/hybrid-svg-production.md](references/upstream/hybrid-svg-production.md)
- Raster → upstream project-native and canvas guidance
- GIF → [references/upstream/motion-production.md](references/upstream/motion-production.md), only after explicit authorization

Muzi changes tokens and rendering treatment only. A divider is allowed only when the upstream core chose `split`; its position is solved per project, never fixed globally. Characters, cats, flourishes, or floating cards may not force a new composition or displace real proof. For a Muzi one-board Hybrid hero, read [references/continuous-scene-composition.md](references/continuous-scene-composition.md) and pass its anti-collage gate before review.

## 6. Validate, preview, and stop

Create `mz.readme-asset/2` from [asset-manifest.schema.json](references/asset-manifest.schema.json) and run:

```text
python scripts/audit_readme.py path/to/README.md
python scripts/validate_asset_manifest.py path/to/hero-manifest.json
python scripts/build_asset_previews.py path/to/hero.webp path/to/previews
python scripts/audit_visual_balance.py path/to/hero.webp
```

Apply the upstream accessibility, GitHub safety, responsive, file-size, theme, and real-proof gates. Inspect at `900px` and `360px` on light and dark GitHub surroundings. For multilingual sets, run the same checks for every locale and verify README-to-asset and localized-alt routing. Verify deterministic rebuild hashes where the route promises them.

Stop at `READY_FOR_REVIEW`. Do not commit, push, publish, create a remote, open a PR, or submit to an upstream showcase without separate explicit authorization.
