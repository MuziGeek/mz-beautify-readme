# Design for a reader's decision

Use this before locking a redesign, and revisit the relevant part when a preview exposes a failure. The goal is a convincing, usable project page, not compliance with a decorative template.

## Establish what can actually be shown

Create a compact evidence note alongside the local review artifacts. For each important promise, record the visible claim, current definition or output, and verification state: observed in this run, supplied by the user, inferred, or unsupported. Sources can be files with line/symbol references, a command log, an actual screenshot, or an explicitly attributed external source. Do not treat a search hit for a symbol as proof of its public API.

Resolve contradictions before using a claim. A feature flag, TODO, adapter, or mock is not an executed feature. If a claim is unsupported, remove it or qualify it visibly. Preserve that correction in the before/after explanation. Do not invent adoption statistics or a success screen to make a layout compelling.

For code examples, check the current package entry point, exported name, CLI parser and required flags, input shape, and expected result. Execute the shortest useful example in a disposable location when feasible. Record failures as failures; update the example only when current source proves the change. Documentation-only projects may have a navigation or lookup exercise instead of a command.

## Choose an opening from evidence

When art direction is open, compare compositions with the same title, claim, and strongest proof. A rough rendered layout is more informative than three style names. Candidates should differ in how the reader encounters the proof, not merely accent color. Make the choice before freezing the brief. A small refresh or an explicit user choice needs no candidate ritual.

| Project material | A useful opening to test | What would make it fail |
| --- | --- | --- |
| CLI or SDK with concise output | Input, transformation, actual result sharing a type/grid rhythm | Fake console text, too-small flags, irrelevant server diagrams |
| App with a strong screenshot | Short title adjacent to or followed by a large genuine product view | Screenshot becomes illegible inside a decorative device frame |
| Asset family or creative tool | A coherent field of real specimens, with title occupying intentional space | Invented specimens, arbitrary rotations, objects obscure each other |
| Research or data | One readable result plus the condition under which it was measured | Decorative curves presented as data, missing axes or qualifiers |
| Plugin or integration | Actual inputs and outputs connected through the real user action | Generic connected boxes with no visible outcome |
| Documentation or minimal utility | Quiet typography and a concrete useful example | A forced illustration buries the first useful action |

These are reasoning prompts, not mandatory presets. Choose material, composition, typography and density together. A neutral public MZ preset is not a fixed color scheme for every project. Use existing project assets when they are stronger than generated ones; do not add a character merely because generation is available.

## Edit for use, not a score

After the opening, arrange information according to the reader's next question. Keep working commands, explanations, links and essential facts in searchable Markdown. Remove repeated promises, misplaced implementation vocabulary, and boilerplate that does not help a decision. Keep important limits near the feature they qualify.

Run `audit_readme_quality.py` before and after. Its English word counts, CJK character counts, sentence flags, heading outline and code-fence list help find congestion. They do not set a universal sentence or badge quota. Chinese line breaks and terminology need direct reading at mobile width. Shorter is only better when the necessary meaning remains.

Check the page with images disabled: a reader must still know what the project does and how to proceed. Hero copy alone cannot carry the product's essential promise. Alt text explains what the proof shows; it does not repeat a filename or every visible label.

## Review visible behavior

Inspect the first screen without relying on the brief. State the product's purpose, the evidence visible, and the next useful action using only the rendered page. If those answers depend on prior knowledge, revise the opening. Treat this as reviewer observation, never as an invented timed user study.

Then inspect the full page. At 360px, read every essential label at its displayed size. Required fine print in a 1200-unit SVG often needs simplification or a separate mobile composition. Long commands and tables may have their own scroll area; the entire page must not overflow. Dark surroundings must not hide transparent strokes or subject edges.

For each defect record what is wrong, what changed, and which new capture demonstrates the fix. Prefer editing the responsible copy, scale or composition over adding decoration. If a locked design choice caused the failure, create a new brief revision and regenerate dependent assets and reviews. Never relabel old screenshots as current.

## Result a person can judge

Lead with the actual chosen visual and a link to the complete page, then a brief before/after explanation. Include phone and dark previews and editable files. Provide the evidence notes and technical report as secondary links. The user should not need to read JSON to decide whether the README is good.

Do not call a screenshot a live GitHub check. Do not call technical READY user approval. If a user asks for a revision, translate their feedback into a visible change and inspect that revision before returning it.
