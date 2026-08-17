<p align="right"><a href="README.zh-CN.md">简体中文</a></p>

<p align="center">
  <img src="docs/readme/hero.svg" width="100%" alt="MZ Beautify README locks project proof and core decisions before applying a validated public visual brief">
</p>

# MZ Beautify README

Proof first. Project-native design. Explicit visual extensions only.

MZ Beautify README is a public, identity-neutral Skill for auditing, redesigning, localizing, and producing GitHub README homepages. It pins the `oil-oil/beautify-github-readme` design core, locks repository facts and proof, then applies a validated `mz.visual-brief/1` without changing the core decision.

## What it keeps separate

| README core owns | Visual Brief may change |
| --- | --- |
| Claims, information order, proof, first successful action | Public semantic color and rendering treatment |
| Theme reasoning and composition | Compatible line, texture, and material roles |
| SVG / Hybrid / Raster implementation | An explicitly supplied, hash-valid Extension |
| Localization, responsive behavior, accessibility, GitHub safety | Only the Extension capabilities permitted by the public Profile |

Repository ownership never activates an identity. Direct use resolves `readme-visual + mz-readme-project-native-v1`; private or brand-specific treatment requires an explicitly supplied Extension.

## Install and use

```text
Use $skill-installer to install:
https://github.com/MuziGeek/mz-beautify-readme/tree/main/mz-beautify-readme
```

```text
Use $mz-beautify-readme to redesign this repository README around its strongest real proof. Generate English and Simplified Chinese assets, validate them locally, and do not publish.
```

The Skill accepts direct public requests, a validated `mz.visual-brief/1`, or a brief plus an explicitly supplied Extension path.

## Contracts and review boundary

- `mz.readme-brief/3` embeds the resolved visual brief beside the immutable `coreDecision`.
- `mz.readme-asset/3` records README brief, visual brief, source, locale, viewport, output, and optional Extension hashes.
- Public and Extension variants must be identical outside `visualBrief` and review status before production.
- GIF remains explicit opt-in. Every route stops at `READY_FOR_REVIEW`; publication requires separate authorization.

## Validate

```text
python scripts/verify_upstream_snapshot.py
python scripts/test_mz_beautify_readme.py
python scripts/validate_visual_brief.py path/to/visual-brief.json
python scripts/validate_brief.py path/to/readme-brief.json
python scripts/validate_asset_manifest.py path/to/hero-manifest.json
python scripts/audit_readme.py path/to/README.md
```

Code and documentation are MIT licensed. The pinned upstream snapshot retains its MIT attribution.
