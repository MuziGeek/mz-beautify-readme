---
name: mz-beautify-readme
description: Redesign, refresh, localize, or audit GitHub README homepages through the public MZ visual route and its pinned proof-first core. Use only when the user explicitly asks for a Muzi, MZ, or 木子 README treatment, explicitly invokes mz-beautify-readme, supplies a validated mz.visual-brief/1 handoff, or supplies an explicit visual Extension. Supports multilingual README and Hero sets, project-native continuous-scene heroes, GitHub-safe SVG, hybrid, raster, and explicitly authorized GIF delivery. Do not use for ordinary generic README beautification without an MZ signal.
---

# MZ Beautify README

Produce a README the reader can understand, try, and judge from rendered evidence. Lock repository truth and the design decision before applying the public visual brief or an explicitly supplied Extension. Never infer identity from repository ownership. A valid manifest is not proof of a good design or user satisfaction.

## 1. Verify and load the upstream core

All tool paths below are relative to this Skill folder; repository and output paths refer to the target project. Run `python scripts/verify_upstream_snapshot.py`. Stop if verification fails. Read the pinned core at [references/upstream/SKILL.md](references/upstream/SKILL.md), then only the production references needed for the selected route. Never edit the byte-locked snapshot during ordinary execution. This wrapper adds outcome verification; it does not replace the upstream design reasoning.

## 2. Lock the README core decision

1. Choose `audit`, `readme`, or `asset-only` from the authorized scope. Honor an existing choice or delegated implementation decision without asking again. Audit is read-only and ends with findings; it does not require producing assets or a READY manifest.
2. Read [references/outcome-design.md](references/outcome-design.md). Establish the reader's first useful outcome, inspect current source and real outputs, and record a compact claim/evidence ledger. Correct stale API/CLI examples from authoritative definitions before styling them. Retain before-state copies and diagnostics for comparison.
3. For a structural redesign with open art direction, compare a few materially different openings using the same truthful copy and proof. Judge them at mobile size, state the choice and why the others lose; do not require the user to choose routine details or generate alternatives for a narrow refresh. Use the pinned core to select its five-part theme, composition, and implementation. GIF remains explicit opt-in.
4. Lock audience, value, proof, first successful action, proof sources, and all visible localized copy in `mz.readme-brief/3`; record design choices under `coreDecision`. These are immutable within a revision and between public/Extension variants. If evidence shows the decision fails, make an explicit new brief revision with the reason and invalidate dependent evidence; do not force an unreadable layout merely to preserve a bad choice.

## 3. Resolve the public visual handoff

For direct use, create `mz.intent/1` with `readme-visual + mz-readme-project-native-v1` and run `python scripts/resolve_visual_brief.py intent.json --output visual-brief.json` through the bundled Engine Snapshot. It writes a new file and never auto-discovers an Extension. For an external brief, run:

```text
python scripts/validate_visual_brief.py path/to/visual-brief.json
python scripts/validate_visual_brief.py path/to/visual-brief.json --extension path/to/explicit-extension
```

An Extension is valid only when supplied explicitly and hash-valid. It may change visual tokens, texture, marks, and permitted character treatment. It may not change repository facts, proof, copy, content order, `coreDecision`, dimensions, localization, implementation, motion authorization, GitHub safety, or acceptance rules.

Embed the resolved object as `visualBrief` in `mz.readme-brief/3`. Do not auto-discover an Extension, inspect the repository owner for identity, or install a missing dependency.

## 4. Validate and produce

Run `python scripts/validate_brief.py path/to/readme-brief.json`. For multiple languages, read [references/localization.md](references/localization.md), lock one copy layer per locale, and never reuse a text-bearing asset across languages. Copy improvement and factual verification apply to the whole README in `readme` mode, including its first-use example and image-free fallback.

Use the production guide selected by `coreDecision`:

- SVG → [references/upstream/svg-production.md](references/upstream/svg-production.md)
- Hybrid → [references/upstream/hybrid-svg-production.md](references/upstream/hybrid-svg-production.md)
- Raster → project-native and GitHub canvas guidance
- GIF → [references/upstream/motion-production.md](references/upstream/motion-production.md), only after explicit authorization

When comparing public and Extension variants, run `python scripts/compare_core_decisions.py public.json extension.json`. Differences outside `visualBrief` and `status` fail.

Read [references/continuous-scene-composition.md](references/continuous-scene-composition.md) when several visual materials share a hero. Do not impose a continuous illustrated scene on a title-only, terminal, or intentionally separated proof layout. At 360px, simplify or make a mobile asset if essential text becomes unreadable; do not just shrink the desktop design.

## 5. Render, inspect, repair

Read [references/review-evidence.md](references/review-evidence.md) for commands and the evidence contract. Run the static audit and `audit_readme_quality.py`; they identify errors and diagnostics, not beauty or factual accuracy. Run the real first-use example where authorized and feasible; record the exact command, environment, exit result, and output. An unavailable environment remains UNVERIFIED, not PASS.

Use `render_readme_review.mjs` to render the complete README for every locale at 900/360 content widths in light/dark surroundings, with images enabled and disabled. For asset-only work, use a separate preview Markdown harness without changing the real README. Inspect the actual captures for first-screen meaning, proof fidelity, text clipping, mobile legibility, contrast, visual hierarchy, and a usable image-free reading path. This is a local GitHub-like preview, not proof of live GitHub rendering.

Fix concrete defects, then rerun affected diagnostics and renders. Keep the issue, correction, and evidence together. A high score, attractive hero, successful screenshot command, or whitespace measurement cannot excuse a broken example or unreadable product. If the requested result cannot be verified, deliver the useful draft and name the unresolved check without READY.

## 6. Deliver something the user can judge

Create `mz.readme-review/1` from the actual render reports; initialization deliberately leaves every review UNVERIFIED. Add specific observations only after viewing screenshots, plus file-backed truth, first-use, copy, visual, and scope evidence. Run `validate_readme_review.py`. Bind this report into `mz.readme-asset/3` as `review`, then run `validate_asset_manifest.py`. READY now requires current file hashes, every locale's preview matrix, and observations matching the screenshots. Legacy v3 drafts still load; a boolean-only legacy READY claim must be regenerated with evidence.

Show the chosen rendered result inline, link the full desktop/mobile preview and before/after comparison, explain the material improvement and any limits, and provide the diff and editable assets. Keep logs and manifests behind these reviewable outputs. `READY_FOR_REVIEW` means prepared for the user's judgment; user acceptance stays PENDING until they explicitly respond. Never claim guaranteed satisfaction or infer it from checks passing.

Do not commit, push, publish, create a remote, open a PR, or submit to a showcase without separate authorization.

## Resources

- `references/visual-engine/`: managed public Engine Snapshot.
- `references/brief.schema.json`: `mz.readme-brief/3`.
- `references/asset-manifest.schema.json`: `mz.readme-asset/3`.
- `references/outcome-design.md`: evidence, copy, design alternatives, and repair criteria.
- `references/review-evidence.md`: executable preview and acceptance workflow.
- `references/research-integration.md`: upstream analysis, selected practices, and deliberate exclusions.
- `references/upstream/`: pinned README design core.
- `scripts/`: visual-brief, README, localization, preview, and audit validation.
