# Source analysis and integration decisions

Reviewed 2026-09-08. These sources inform original MZ guidance and helpers; no additional source code or templates are vendored. The existing oil-oil snapshot and its MIT notice remain byte-locked. Findings below distinguish tool behavior from agent instructions and advertised future work.

| Source revision | Useful contribution | Observed limit | MZ integration |
| --- | --- | --- | --- |
| [oil-oil](https://github.com/oil-oil/beautify-github-readme/tree/55bdb1c05414cd7a0cf911d02e55ece79777206e) | Derives typography and composition from real repository material | Its static audit cannot establish whether a complete page is legible or persuasive | Retain the design core; add actual page rendering and screenshot-bound review |
| [Awesome README Studio](https://github.com/BeatAPI/awesome-readme-studio/tree/04d2378c95983c43c3fec43f18e12993a51075d7) | Evidence priority, explicit claim states and selectable cover directions | Preset SVG generation does not make a motif project-specific; browser previews are advertised as future work | Require claim/source notes and compare meaningful openings instead of choosing a preset label |
| [beautify-md](https://github.com/bmeunier1974/beautify-md/tree/856102cd7627087d23a6056d1a4a1d24f882cd7f) | Before/after readability measurements separated from editorial judgment | Heuristic English sentence thresholds and successful script exit do not prove quality | Parse Markdown, report English/CJK diagnostics separately, then review meaning at displayed size |
| [good-readme](https://github.com/adewale/good-readme/tree/8631fbc0f457776cb976915930cb1fd621dca476) | Checks documented API/CLI names against actual public definitions; uses behavioral fixtures | A rubric and fixture oracle do not provide visual validation of arbitrary projects | Verify current examples and actual output; keep content and visual acceptance separate |

## What changed in the product workflow

The old MZ wrapper verified snapshot hashes, brief fields and declared asset hashes. Its `validation` object could be a single boolean. Its preview helper resized raster artwork only. Those checks were useful for integrity but insufficient to establish that a README worked for a reader.

The revised workflow binds a rendered page to the exact files reviewed, requires locale/width/theme and image-free coverage, and refuses READY when evidence is stale or an observation is absent. Markdown diagnostics locate structural and prose issues; explicit reviewer evidence covers facts and first use. None of these claim to compute taste or certify user satisfaction.

## Deliberate exclusions

- No universal visual preset, house mascot, mandatory three-option pause, or fixed cover size.
- No imported English sentence quota for Chinese copy.
- No aggregate beauty score that can compensate for a broken example or unreadable screenshot.
- No mandatory AI artwork, remote publishing, tracking, promotional footer, or upstream installation.
- No claim that an offline preview duplicates live GitHub sanitization.

## Regression expectations

A changed asset must invalidate an earlier review. A missing locale, missing screenshot, image load failure, or unresolved observation must prevent READY. A false command in a sample repository must be corrected from its parser and demonstrated by running the replacement. Visual examples should use distinct project material and remain readable on a phone; two recolored copies of one cover are not evidence of generalization.

The Python evidence tests and Node renderer tests cover mechanical behavior. Realistic forward use in an isolated repository covers the connection between instructions and generated outcomes. Keep the generated pages, observations and defects separate from test-pass counts, and ask the user to judge the displayed result.
