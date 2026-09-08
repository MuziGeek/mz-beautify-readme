#!/usr/bin/env node
import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const workspace = mkdtempSync(join(tmpdir(), 'mz-readme-render-'));
const script = join(import.meta.dirname, 'render_readme_review.mjs');
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=', 'base64');
function run(repo, out, readme = 'README.md') { return spawnSync(process.execPath, [script, '--root', repo, '--readme', readme, '--locale', 'en', '--out', out], { encoding: 'utf8', env: process.env }); }
try {
  const positive = join(workspace, 'positive'); const positiveOut = join(workspace, 'positive-review'); mkdirSync(join(positive, 'docs', 'assets'), { recursive: true });
  writeFileSync(join(positive, 'docs', 'assets', 'green.svg'), '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10" fill="#00aa00"/></svg>');
  writeFileSync(join(positive, 'docs', 'assets', 'dark.svg'), '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10" fill="#0000ff"/></svg>');
  writeFileSync(join(positive, 'docs', 'assets', 'huge.svg'), '<svg viewBox="0 0 100000 10" width="100000" height="10" xmlns="http://www.w3.org/2000/svg"><rect width="100000" height="10" fill="#ff0000"/></svg>');
  writeFileSync(join(positive, 'docs', 'README.md'), `# Valid fixture

![nested image](assets/green.svg)
![wide but contained](assets/huge.svg)

[markdown source](assets/green.svg)
<a href="assets/dark.svg">raw source</a>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark.svg"><img src="assets/green.svg" alt="theme image"></picture>

\`<img src="not-an-image.png" onerror="keep literal">\`

\`\`\`html
<img src="also-not-an-image.png" onerror="keep literal">
\`\`\`
`);
  let result = run(positive, positiveOut, 'docs/README.md'); assert.equal(result.status, 0, result.stdout + result.stderr);
  let report = JSON.parse(readFileSync(join(positiveOut, 'render-report.json'), 'utf8')); assert.equal(report.status, 'PASS'); assert.equal(report.captures.length, 8);
  assert.ok(report.inputs.some((entry) => entry.path === 'docs/assets/green.svg'), 'nested README relative resource is input-hashed');
  assert.ok(report.inputs.some((entry) => entry.path === 'docs/assets/dark.svg'), 'every picture candidate is input-hashed'); assert.ok(report.inputs.some((entry) => entry.path === 'docs/assets/huge.svg'), 'large intrinsic SVG is input-hashed');
  for (const capture of report.captures) { assert.deepEqual(capture.problems, []); assert.ok(capture.sha256); assert.ok(capture.selectedSources.every((source) => source.naturalWidth > 0 && source.naturalHeight > 0 && source.visible)); }
  const dark = report.captures.find((capture) => capture.width === 900 && capture.theme === 'dark' && capture.images); const light = report.captures.find((capture) => capture.width === 900 && capture.theme === 'light' && capture.images);
  assert.ok(dark.selectedSources.some((source) => source.source?.endsWith('.svg'))); assert.notDeepEqual(dark.selectedSources, light.selectedSources, 'dark picture selection is recorded separately');
  const index = readFileSync(join(positiveOut, 'preview.en.html'), 'utf8'); const enabled = readFileSync(join(positiveOut, 'preview.en.900.light.images.html'), 'utf8'); const disabled = readFileSync(join(positiveOut, 'preview.en.900.light.images-disabled.html'), 'utf8');
  assert.ok(index.includes('preview.en.360.dark.images-disabled.html')); assert.ok(enabled.includes('resources/')); assert.ok(disabled.includes('Image disabled: nested image')); assert.ok(enabled.includes('not-an-image.png') && enabled.includes('also-not-an-image.png') && !enabled.includes('resources/not-an-image'), 'inline-code and fenced HTML remain code text');
  const previewUrl = pathToFileURL(join(positiveOut, 'preview.en.900.light.images.html')); const localLinks = [...enabled.matchAll(/href="([^"]+\.svg)"/g)].map((match) => match[1]); assert.equal(localLinks.length, 2); for (const href of localLinks) assert.ok(existsSync(fileURLToPath(new URL(href, previewUrl))), `rewritten link exists: ${href}`);

  const negative = join(workspace, 'negative'); const negativeOut = join(workspace, 'negative-review'); mkdirSync(join(negative, 'assets'), { recursive: true }); writeFileSync(join(negative, 'assets', 'good.png'), png); writeFileSync(join(negative, 'assets', 'bad.png'), Buffer.from('not a png')); writeFileSync(join(negative, 'assets', 'bad.svg'), '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'); writeFileSync(join(negative, 'assets', 'relative.svg'), '<svg xmlns="http://www.w3.org/2000/svg"><image href="good.png" width="1" height="1"/></svg>');
  writeFileSync(join(negative, 'README.md'), `# Invalid fixture
![good](assets/good.png)
![bad bytes](assets/bad.png)
![unsafe svg](assets/bad.svg)
![relative svg dependency](assets/relative.svg)
![missing](assets/missing.png)
![remote](https://example.invalid/image.png)
<img src="assets/bad.svg" alt="unsafe" onerror="fetch('https://example.invalid/leak')">
<img src=assets/good.png alt=unquoted>
<script>fetch('https://example.invalid/script')</script>

| a | b | c | d | e | f | g | h |
| - | - | - | - | - | - | - | - |
| one | two | three | four | five | six | seven | eight |
`);
  const external = join(workspace, 'external'); mkdirSync(external); writeFileSync(join(external, 'outside.png'), png); let linked = false; try { symlinkSync(external, join(negative, 'outside-link'), 'junction'); linked = true; writeFileSync(join(negative, 'README.md'), `${readFileSync(join(negative, 'README.md'), 'utf8')}\n![junction](outside-link/outside.png)\n`); } catch { /* Link privileges vary; realpath containment is still exercised when available. */ }
  result = run(negative, negativeOut); assert.equal(result.status, 1, result.stdout + result.stderr); report = JSON.parse(readFileSync(join(negativeOut, 'render-report.json'), 'utf8')); assert.equal(report.status, 'FAIL');
  const problems = report.captures.flatMap((capture) => capture.problems).join('\n'); assert.match(problems, /MISSING_LOCAL_RESOURCE/); assert.match(problems, /UNSAFE_HTML/); assert.match(problems, /UNSAFE_SVG: assets\/relative\.svg/); assert.match(problems, /BROKEN_RENDERED_IMAGE/); if (linked) assert.match(problems, /RESOURCE_OUTSIDE_ROOT/); assert.ok(report.remoteUrls.includes('https://example.invalid/image.png'));
  const malformedLocale = spawnSync(process.execPath, [script, '--root', positive, '--readme', 'docs/README.md', '--locale', '../bad', '--out', join(workspace, 'bad-locale')], { encoding: 'utf8', env: process.env }); assert.equal(malformedLocale.status, 2);
  console.log('render_readme_review behaviour test passed');
} finally { rmSync(workspace, { recursive: true, force: true }); }
