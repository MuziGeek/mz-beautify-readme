# Reproducible README review

Run scripts from the installed Skill directory; supply the target paths explicitly. Keep review JSON at the target repository root so all records use the same relative-path base. Keep screenshots, logs, scratch designs and evidence notes in a review subdirectory. Follow the project's ignore/release rules for those local artifacts.

## Tools and honest fallback

- Python tools: dependencies in `scripts/requirements.txt` (Pillow and markdown-it-py).
- Complete-page preview: Node.js, `marked`, `playwright`, and an available Chromium browser. If those packages are in a bundled runtime, set `MZ_NODE_MODULES` to its `node_modules` directory; otherwise use normally resolvable packages. No private machine path is embedded in the Skill.
- The renderer never installs packages or a browser. Missing dependencies produce a specific error. Continue useful copy/design work but leave render verification incomplete until a suitable environment is available.
- `build_asset_previews.py` and `audit_visual_balance.py` are supplemental single-image tools; neither substitutes for page preview or aesthetic inspection.

```text
python scripts/audit_readme.py TARGET/README.md
python scripts/audit_readme_quality.py TARGET/README.md --root TARGET --output TARGET/.readme-review/quality.en.json
node scripts/render_readme_review.mjs --root TARGET --readme README.md --locale en --out TARGET/.readme-review/en
node scripts/render_readme_review.mjs --root TARGET --readme README.zh-CN.md --locale zh-CN --out TARGET/.readme-review/zh-CN
```

The Node renderer outputs offline HTML, eight PNG captures (900/360 content widths, light/dark, images on/off), and `render-report.json`. It records current source hashes and reports missing assets, unsafe markup, broken images, page errors and page-wide overflow. Remote resources remain unverified and are not downloaded. Its local HTML/CSS is a GitHub-like approximation, not GitHub's sanitizer or authenticated page.

For asset-only mode, make a temporary Markdown page that embeds the proposed assets plus only enough copy to inspect them. Preserve the real README bytes and prove that in the scope evidence. Store a localized preview subject for every output locale. A preview harness is not authorization to change the real README.

## Initialize without manufacturing results

```text
python scripts/validate_readme_review.py TARGET/readme-review.json --init --render TARGET/.readme-review/en/render-report.json --render TARGET/.readme-review/zh-CN/render-report.json --input TARGET/readme-brief.json --input TARGET/visual-brief.json
```

Add any other deliverables or production source files as `--input`. Initialization collects render inputs and creates only a DRAFT. It refuses to overwrite a prior report. No checks or observations are passed automatically.

## Evidence contract: mz.readme-review/1

`inputs` binds the current README, assets, briefs and production sources with `{path, sha256}` records. `readmes` maps each locale to its exact README or asset-only preview subject. `renders` contains hash records pointing to renderer JSON reports. Each report binds its inputs to repository-relative paths and its capture files to paths relative to that report.

Complete the five checks with concrete notes and one or more evidence file records:

| Check | Evidence needed |
| --- | --- |
| truth | Claim ledger, current definitions, actual output or supplied evidence; resolve contradictions |
| first-use | Exact command/environment/exit result and actual output, or a performed documentation lookup/navigation exercise |
| copy | Before/after diagnostics plus reviewer findings about meaning, repetition and image-free usability |
| visual | Chosen direction, inspected rendered result, and any concrete defect/correction notes |
| scope | Before/after file inventory or diff, preserving unrelated work and asset-only README bytes |

Allowed completed status is `PASS`. Only `first-use` may be `NOT_APPLICABLE`, with evidence explaining why no runnable or navigable product action exists. Missing environment/access is `UNVERIFIED`, not N/A. No generic script can prove semantic truth from a note; the reviewer is responsible for actually reading and executing the evidence.

Inspect every screenshot and fill its observation: `locale`, `width`, `theme`, `images`, `captureSha256`, `verdict`, and concrete `findings`. Do not batch-fill PASS based on successful generation. State what was visible and why it meets the intended reader's need. `userAcceptance` stays `PENDING`; this report records technical/reviewer readiness only.

When all checks and observations are satisfied, set `status` to `READY_FOR_REVIEW` and run:

```text
python scripts/validate_readme_review.py TARGET/readme-review.json
python scripts/validate_asset_manifest.py TARGET/readme-assets.json
```

The asset manifest's `review` is a hash record for `readme-review.json`. A READY asset manifest must bind its briefs, primary asset, variants and sources into the review inputs. Its locale mapping must match the brief and review. The validator reads both the brief and visual brief; a file whose name happens to end in JSON is insufficient.

Changed README, asset, proof evidence, renderer report or screenshot hashes invalidate the old review. Re-render and inspect affected outputs, create a new review revision, and update the manifest hashes. Existing v3 draft manifests remain valid; legacy boolean-only READY manifests intentionally fail until backed by this evidence. `validation` remains descriptive metadata and cannot bypass the review.

## Delivery and limits

Deliver a visible preview and complete-page links first, with before/after findings, editable files and outstanding limitations. READY does not grant permission to publish and does not establish user satisfaction. A fully offline run does not validate remote links, hosted badges, live GitHub sanitization or external services. If those are central to the requested result, resolve them in an authorized environment or leave the relevant check UNVERIFIED.
