#!/usr/bin/env node
/** Offline GitHub-like README review; it is not evidence of GitHub's live sanitizer. */
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { delimiter, dirname, extname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const FATAL = /^(?:MISSING_LOCAL_(?:RESOURCE|LINK)|UNSAFE_|RESOURCE_OUTSIDE_ROOT|HORIZONTAL_OVERFLOW|PAGE_ERROR|CAPTURE_ERROR|BROWSER_UNAVAILABLE|BLOCKED_NETWORK_REQUEST|BROKEN_RENDERED_IMAGE)/;
const REMOTE = /^(?:https?:)?\/\//i;
const SAFE_MEDIA = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.svg', '.mp4', '.webm', '.mp3', '.ogg', '.wav']);
const ALLOWED = new Set(['details', 'summary', 'picture', 'source', 'img', 'video', 'audio', 'br', 'kbd', 'sub', 'sup', 'mark', 'del', 'ins', 'div', 'span', 'p', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td']);
const FORBIDDEN = new Set(['script', 'style', 'iframe', 'object', 'embed', 'link', 'meta', 'base', 'form']);

function usage() { console.error('usage: node scripts/render_readme_review.mjs --root REPOSITORY --readme README.md --locale en --out OUTPUT'); }
function parseArgs(argv) {
  const values = {};
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (!['--root', '--readme', '--locale', '--out'].includes(key)) throw new Error(`Unknown option: ${key}`);
    const value = argv[++i];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for ${key}`);
    if (key === '--locale' && values.locale) throw new Error('Run once per locale so each report has one locale.');
    values[key.slice(2)] = value;
  }
  if (!values.root || !values.readme || !values.locale || !values.out) throw new Error('root, readme, locale, and out are required');
  if (!/^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$/.test(values.locale)) throw new Error('locale must use a BCP 47-like tag such as en or zh-CN');
  return values;
}
function sha256(value) { return createHash('sha256').update(value).digest('hex'); }
function fileHash(file) { return sha256(readFileSync(file)); }
function slash(path) { return path.split(sep).join('/'); }
function relFrom(root, file) { return slash(relative(root, file)); }
function inside(root, candidate) { const rel = relative(root, candidate); return rel !== '' && rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel); }
function escapeHtml(value) { return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;'); }
function attr(raw, name) { return new RegExp(`\\b${name}\\s*=\\s*(["'])(.*?)\\1`, 'i').exec(raw)?.[2] ?? null; }
function boolAttr(raw, name) { return new RegExp(`\\b${name}(?:\\s|>|$)`, 'i').test(raw); }

function loadDependency(name) {
  const candidates = [];
  if (process.env.MZ_NODE_MODULES) candidates.push(...process.env.MZ_NODE_MODULES.split(delimiter).filter(Boolean));
  if (process.env.NODE_PATH) candidates.push(...process.env.NODE_PATH.split(delimiter).filter(Boolean));
  candidates.push(join(dirname(process.execPath), 'node_modules'));
  for (const candidate of candidates) {
    try { return createRequire(join(resolve(candidate), '_mz_readme_review.cjs'))(name); } catch { /* try next */ }
  }
  try { return createRequire(import.meta.url)(name); } catch { throw new Error(`${name} is unavailable. Set MZ_NODE_MODULES to a directory containing it; dependencies are not installed automatically.`); }
}
function safeSvg(path) {
  const source = readFileSync(path, 'utf8');
  const hrefs = [...source.matchAll(/(?:xlink:)?href\s*=\s*["']([^"']*)["']/gi)].map((match) => match[1].trim());
  const urls = [...source.matchAll(/url\(\s*["']?\s*([^\s"')]+)[^)]*\)/gi)].map((match) => match[1].trim());
  return !(/<\s*(?:script|foreignObject|iframe|object|embed)\b/i.test(source)
    || /\bon\w+\s*=/i.test(source)
    || /(?:href|src)\s*=\s*["']\s*(?:https?:|\/\/|data:)/i.test(source)
    || /url\(\s*["']?\s*(?:https?:|\/\/|data:)/i.test(source)
    || hrefs.some((href) => href && !href.startsWith('#'))
    || urls.some((url) => url && !url.startsWith('#')));
}

function makeRouter({ root, readme, out, inputs, remoteUrls, problems, images }) {
  const resources = join(out, 'resources'); mkdirSync(resources, { recursive: true }); const readmeDir = dirname(readme);
  const disabled = (alt) => `<span class="image-disabled">Image disabled: ${escapeHtml(alt || 'image')}</span>`;
  return (raw, alt = 'image', kind = 'image') => {
    const source = (raw || '').trim();
    if (!source || /^\s*(?:data:|file:|javascript:)/i.test(source)) { problems.add(`UNSAFE_RESOURCE_URL: ${source || '(empty)'}`); return disabled(alt); }
    if (REMOTE.test(source)) { remoteUrls.add(source); return `<span class="remote-disabled" data-unverified="true">Remote ${escapeHtml(kind)} unavailable offline: ${escapeHtml(alt || source)}</span>`; }
    if (source.startsWith('#')) return disabled(alt);
    let clean;
    try { clean = decodeURIComponent(source.split('#', 1)[0].split('?', 1)[0]); } catch { problems.add(`UNSAFE_RESOURCE_URL: ${source}`); return disabled(alt); }
    const candidate = resolve(clean.startsWith('/') ? root : readmeDir, clean.startsWith('/') ? `.${clean}` : clean);
    if (!inside(root, candidate) || !existsSync(candidate)) { problems.add(`${inside(root, candidate) ? 'MISSING_LOCAL_RESOURCE' : 'RESOURCE_OUTSIDE_ROOT'}: ${source}`); return `<span class="broken-resource">Missing ${escapeHtml(kind)}: ${escapeHtml(alt || source)}</span>`; }
    let local;
    try { local = realpathSync(candidate); } catch { problems.add(`MISSING_LOCAL_RESOURCE: ${source}`); return `<span class="broken-resource">Missing ${escapeHtml(kind)}: ${escapeHtml(alt || source)}</span>`; }
    if (!inside(root, local)) { problems.add(`RESOURCE_OUTSIDE_ROOT: ${source}`); return `<span class="broken-resource">Rejected ${escapeHtml(kind)}: ${escapeHtml(alt || source)}</span>`; }
    const extension = extname(local).toLowerCase();
    if (!SAFE_MEDIA.has(extension)) { problems.add(`UNSAFE_RESOURCE_TYPE: ${source}`); return `<span class="broken-resource">Rejected ${escapeHtml(kind)}: ${escapeHtml(alt || source)}</span>`; }
    if (extension === '.svg' && !safeSvg(local)) { problems.add(`UNSAFE_SVG: ${source}`); return `<span class="broken-resource">Rejected SVG: ${escapeHtml(alt || source)}</span>`; }
    const digest = fileHash(local); inputs.set(relFrom(root, local), digest); const copied = `${digest.slice(0, 16)}${extension}`; const target = join(resources, copied);
    if (!existsSync(target)) copyFileSync(local, target);
    if (!images && kind === 'image') return disabled(alt);
    return `resources/${copied}`;
  };
}
function routeSrcset(value, route, alt) {
  return value.split(',').map((candidate) => { const parts = candidate.trim().split(/\s+/); const routed = route(parts.shift(), alt, 'image'); return routed.includes('<') ? '' : [routed, ...parts].join(' '); }).filter(Boolean).join(', ');
}
function routeLink(raw, root, readme, out, problems) {
  const href = (raw || '').trim();
  if (!href || href.startsWith('#')) return href;
  if (/^(?:https?:|mailto:)/i.test(href)) return href;
  if (REMOTE.test(href)) { problems.add(`UNSAFE_LINK_URL: ${href}`); return '#'; }
  if (/^(?:data:|file:|javascript:|[^/]+:)/i.test(href)) { problems.add(`UNSAFE_LINK_URL: ${href}`); return '#'; }
  const match = /^([^?#]*)([?#][\s\S]*)?$/.exec(href);
  let clean;
  try { clean = decodeURIComponent(match?.[1] || ''); } catch { problems.add(`UNSAFE_LINK_URL: ${href}`); return '#'; }
  const candidate = resolve(clean.startsWith('/') ? root : dirname(readme), clean.startsWith('/') ? `.${clean}` : clean);
  if (!inside(root, candidate) || !existsSync(candidate)) { problems.add(`${inside(root, candidate) ? 'MISSING_LOCAL_LINK' : 'RESOURCE_OUTSIDE_ROOT'}: ${href}`); return '#'; }
  let target;
  try { target = realpathSync(candidate); } catch { problems.add(`MISSING_LOCAL_LINK: ${href}`); return '#'; }
  if (!inside(root, target)) { problems.add(`RESOURCE_OUTSIDE_ROOT: ${href}`); return '#'; }
  const targetHref = slash(relative(out, target));
  return `${targetHref.startsWith('.') ? targetHref : `./${targetHref}`}${match?.[2] || ''}`;
}
function blockedHtml(tag, problems, reason = tag) { problems.add(`UNSAFE_HTML: <${reason}>`); return `<span class="broken-resource">Rejected HTML: ${escapeHtml(reason)}</span>`; }
function sanitizeHtml(raw, route, problems) {
  return raw.replace(/<\s*(\/)?\s*([a-zA-Z0-9-]+)([^>]*)>/g, (whole, closing, original, rawAttrs) => {
    const tag = original.toLowerCase();
    if (FORBIDDEN.has(tag) || !ALLOWED.has(tag)) return blockedHtml(tag, problems);
    if (closing) return `</${tag}>`;
    const event = /\bon\w+\s*=/i.exec(rawAttrs); if (event) return blockedHtml(tag, problems, `${tag} ${event[0].trim()}`);
    if (/\b[\w:-]+\s*=\s*(?!["'])[^\s>]+/i.test(rawAttrs)) return blockedHtml(tag, problems, `${tag} unquoted-attribute`);
    if (/\bstyle\s*=/i.test(rawAttrs)) return blockedHtml(tag, problems, `${tag} style`);
    const title = attr(rawAttrs, 'title'); const alt = attr(rawAttrs, 'alt') || title || tag; const attrs = [];
    if (tag === 'details' && boolAttr(rawAttrs, 'open')) attrs.push('open');
    if (title && ['img', 'a'].includes(tag)) attrs.push(`title="${escapeHtml(title)}"`);
    if (tag === 'a') { const href = attr(rawAttrs, 'href'); const routed = route.link(href); if (href && routed === '#') return blockedHtml(tag, problems, 'a href'); if (href) attrs.push(`href="${escapeHtml(routed)}"`); }
    if (tag === 'img') { const routed = route(attr(rawAttrs, 'src'), alt, 'image'); if (routed.includes('<')) return routed; attrs.push(`class="readme-image" data-local-resource="true" src="${escapeHtml(routed)}" alt="${escapeHtml(alt)}"`); for (const field of ['width', 'height']) { const value = attr(rawAttrs, field); if (value && /^\d{1,5}$/.test(value)) attrs.push(`${field}="${value}"`); } }
    if (tag === 'source') { const srcset = attr(rawAttrs, 'srcset'); const src = attr(rawAttrs, 'src'); if (srcset) { const routed = routeSrcset(srcset, route, alt); if (routed) attrs.push(`srcset="${escapeHtml(routed)}"`); } else if (src) { const routed = route(src, alt, 'media'); if (!routed.includes('<')) attrs.push(`src="${escapeHtml(routed)}"`); } for (const field of ['media', 'type', 'sizes']) { const value = attr(rawAttrs, field); if (value) attrs.push(`${field}="${escapeHtml(value)}"`); } }
    if (tag === 'video' || tag === 'audio') { const source = attr(rawAttrs, 'src'); if (source) { const routed = route(source, alt, 'media'); if (!routed.includes('<')) attrs.push(`src="${escapeHtml(routed)}"`); } attrs.push('controls preload="metadata" class="readme-media"'); }
    return `<${tag}${attrs.length ? ` ${attrs.join(' ')}` : ''}>`;
  });
}
function css(theme, width) {
  const dark = theme === 'dark'; const bg = dark ? '#0d1117' : '#ffffff'; const ink = dark ? '#c9d1d9' : '#1f2328'; const edge = dark ? '#30363d' : '#d1d9e0';
  return `<style>html{background:${bg};color:${ink};color-scheme:${theme};font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}*{box-sizing:border-box}body{margin:0;min-width:100%;background:${bg}}#surface{padding:24px;overflow-x:auto}#readme{width:${width}px;min-height:100vh;margin:0 auto;overflow-wrap:anywhere}h1,h2{border-bottom:1px solid ${edge};padding-bottom:.3em}a{color:${dark ? '#58a6ff' : '#0969da'}}pre{overflow-x:auto;padding:16px;background:${dark ? '#161b22' : '#f6f8fa'};border-radius:6px}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}table{display:block;max-width:100%;overflow-x:auto;border-spacing:0;border-collapse:collapse}th,td{padding:6px 13px;border:1px solid ${edge}}blockquote{margin:0;padding:0 1em;color:${dark ? '#8b949e' : '#59636e'};border-left:4px solid ${dark ? '#3d444d' : '#d1d9e0'}}.readme-image,.readme-media{display:block;max-width:100%;height:auto;margin:.8em 0}.image-disabled,.remote-disabled,.broken-resource{display:inline-block;padding:.35em .5em;border-radius:6px;background:${dark ? '#21262d' : '#f6f8fa'};color:${dark ? '#8b949e' : '#59636e'};font-size:.9em}.broken-resource{color:${dark ? '#ff7b72' : '#cf222e'}}details{padding:.25em 0}summary{cursor:pointer}</style>`;
}
function buildDocument({ locale, theme, width, images, rendered }) { return `<!doctype html><html lang="${escapeHtml(locale)}"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; media-src 'self'; style-src 'unsafe-inline'"><title>README review ${escapeHtml(locale)} ${width} ${theme}</title>${css(theme, width)}</head><body><div id="surface"><main id="readme" data-images="${images}">${rendered}</main></div></body></html>`; }
function indexDocument(locale, files) { return `<!doctype html><meta charset="utf-8"><title>README review ${escapeHtml(locale)}</title><h1>Offline README review</h1><p>Local GitHub-like previews only; this is not GitHub sanitizer proof.</p><ul>${files.map((file) => `<li><a href="${escapeHtml(file)}">${escapeHtml(file)}</a></li>`).join('')}</ul>`; }
async function findBrowser(playwright) {
  const candidates = [process.env.MZ_BROWSER_EXECUTABLE, process.platform === 'win32' ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' : null, process.platform === 'win32' ? 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe' : null].filter(Boolean);
  for (const executablePath of candidates) if (existsSync(executablePath)) return playwright.chromium.launch({ headless: true, executablePath, args: ['--no-first-run', '--no-default-browser-check'] });
  try { return await playwright.chromium.launch({ headless: true }); } catch (error) { throw new Error(`BROWSER_UNAVAILABLE: ${error.message}`); }
}
async function main() {
  let options; try { options = parseArgs(process.argv.slice(2)); } catch (error) { usage(); throw error; }
  const root = realpathSync(resolve(options.root)); const readmeInput = resolve(root, options.readme);
  if (!inside(root, readmeInput) || !existsSync(readmeInput)) throw new Error('README must exist inside --root');
  const readme = realpathSync(readmeInput); if (!inside(root, readme)) throw new Error('README resolves outside --root');
  const out = resolve(options.out); mkdirSync(out, { recursive: true, }); const reportPath = join(out, 'render-report.json');
  const inputs = new Map([[relFrom(root, readme), fileHash(readme)]]); const remoteUrls = new Set(); const markdown = readFileSync(readme, 'utf8'); const markedModule = loadDependency('marked'); const playwright = loadDependency('playwright'); const marked = markedModule.marked || markedModule;
  const captures = []; const previewFiles = []; let browser; let browserProblem = null; try { browser = await findBrowser(playwright); } catch (error) { browserProblem = error.message; }
  for (const width of [900, 360]) for (const theme of ['light', 'dark']) for (const images of [true, false]) {
    const problems = new Set(browserProblem ? [browserProblem] : []); const warnings = new Set(); const router = makeRouter({ root, readme, out, inputs, remoteUrls, problems, images }); router.link = (href) => routeLink(href, root, readme, out, problems); const renderer = new marked.Renderer();
    renderer.html = (token) => sanitizeHtml(typeof token === 'string' ? token : token.raw, router, problems);
    renderer.image = ({ href, title, text }) => { const routed = router(href, text || title || 'image', 'image'); return routed.includes('<') ? routed : `<img class="readme-image" data-local-resource="true" src="${escapeHtml(routed)}" alt="${escapeHtml(text || '')}"${title ? ` title="${escapeHtml(title)}"` : ''}>`; };
    renderer.link = function renderLink({ href, title, tokens }) { const text = this.parser.parseInline(tokens); const routed = router.link(href); return routed === '#' && href ? `<span class="broken-resource">Rejected link: ${text}</span>` : `<a href="${escapeHtml(routed)}"${title ? ` title="${escapeHtml(title)}"` : ''}>${text}</a>`; };
    const rendered = marked.parse(markdown, { gfm: true, breaks: false, renderer }); const document = buildDocument({ locale: options.locale, theme, width, images, rendered });
    const htmlName = `preview.${options.locale}.${width}.${theme}.${images ? 'images' : 'images-disabled'}.html`; const htmlPath = join(out, htmlName); writeFileSync(htmlPath, document, 'utf8'); previewFiles.push(htmlName);
    const captureName = `readme.${options.locale}.${width}.${theme}.${images ? 'images' : 'images-disabled'}.png`; const capturePath = join(out, captureName); let selectedSources = [];
    if (browser) {
      let page;
      try {
        page = await browser.newPage({ viewport: { width: width + 48, height: 800 }, deviceScaleFactor: 1, colorScheme: theme });
        await page.route('**/*', async (route) => { const url = route.request().url(); const scheme = new URL(url).protocol; if (scheme === 'file:' || scheme === 'data:') await route.continue(); else { problems.add(`BLOCKED_NETWORK_REQUEST: ${url}`); await route.abort(); } });
        page.on('pageerror', (error) => problems.add(`PAGE_ERROR: ${error.message}`)); await page.goto(pathToFileURL(htmlPath).toString(), { waitUntil: 'load' });
        const renderedImages = await page.evaluate(async () => { if (document.fonts?.ready) await document.fonts.ready; const images = [...document.querySelectorAll('img[data-local-resource="true"]')]; await Promise.all(images.map((image) => image.decode().catch(() => undefined))); return images.map((image) => ({ alt: image.alt, src: image.getAttribute('src'), currentSrc: image.currentSrc, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight, visible: image.getBoundingClientRect().width > 0 && image.getBoundingClientRect().height > 0 })); });
        if (images) for (const image of renderedImages) if (!image.naturalWidth || !image.naturalHeight || !image.visible) problems.add(`BROKEN_RENDERED_IMAGE: ${image.src || image.alt}`);
        selectedSources = renderedImages.map((image) => ({ alt: image.alt, source: image.currentSrc ? decodeURIComponent(new URL(image.currentSrc).pathname).split('/').pop() : image.src, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight, visible: image.visible }));
        const overflow = await page.evaluate(() => { const page = document.documentElement; const readme = document.querySelector('#readme'); const localScroll = [...document.querySelectorAll('pre, table')].some((node) => node.scrollWidth > node.clientWidth + 1); return { page: page.scrollWidth > page.clientWidth + 1, readme: readme?.scrollWidth > readme?.clientWidth + 1, readmeWidth: readme?.clientWidth, localScroll }; });
        if (overflow.readmeWidth !== width) problems.add(`HORIZONTAL_OVERFLOW: rendered content width ${overflow.readmeWidth} differs from requested ${width}`); if (overflow.readme) problems.add('HORIZONTAL_OVERFLOW: README content exceeds its container'); if (overflow.page) problems.add('HORIZONTAL_OVERFLOW: page content exceeds capture viewport'); if (overflow.localScroll) warnings.add('LOCAL_SCROLL_OVERFLOW: code or table uses its intended horizontal scroll container'); await page.locator('#surface').screenshot({ path: capturePath });
      } catch (error) { problems.add(`CAPTURE_ERROR: ${error.message}`); } finally { await page?.close(); }
    }
    captures.push({ width, theme, images, path: relFrom(dirname(reportPath), capturePath), sha256: existsSync(capturePath) ? fileHash(capturePath) : null, problems: [...problems].sort(), warnings: [...warnings].sort(), selectedSources });
  }
  await browser?.close(); writeFileSync(join(out, `preview.${options.locale}.html`), indexDocument(options.locale, previewFiles), 'utf8');
  const report = { format: 'mz.readme-render/1', locale: options.locale, readme: { path: relFrom(root, readme), sha256: fileHash(readme) }, inputs: [...inputs.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([path, digest]) => ({ path, sha256: digest })), captures, renderer: { markdown: 'marked', browser: 'playwright', mode: 'offline-github-like', network: 'blocked' }, remoteUrls: [...remoteUrls].sort(), limitations: ['This is an offline GitHub-like local preview, not proof of GitHub live sanitizer, renderer, CDN, or browser-specific behaviour.', 'Remote URLs are not requested and remain unverified.', 'The tool reports structural rendering problems; it does not automatically judge visual quality.'], status: captures.some((capture) => capture.problems.some((problem) => FATAL.test(problem))) ? 'FAIL' : 'PASS' };
  writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8'); console.log(`${report.status}: ${reportPath}`); if (report.status === 'FAIL') process.exitCode = 1;
}
main().catch((error) => { console.error(`FAIL: ${error.message}`); process.exitCode = 2; });
