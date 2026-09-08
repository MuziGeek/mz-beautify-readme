#!/usr/bin/env python3
"""Offline structural diagnostics, not a beauty score or a claim verifier."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def audit(path: Path, root: Path) -> dict:
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise RuntimeError('Install the declared markdown-it-py dependency to parse Markdown accurately.') from exc
    from audit_readme import audit_svg
    from html.parser import HTMLParser
    text = path.read_text(encoding='utf-8')
    parser = MarkdownIt('commonmark', {'html': True}).enable('table')
    tokens = parser.parse(text)
    problems, warnings, remote, targets, paragraphs = [], [], [], [], []
    headings, fences, previous = [], [], 0

    class HTMLReferences(HTMLParser):
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'img':
                if not attrs.get('alt', '').strip(): problems.append('HTML image has no useful alt text')
                if attrs.get('src'): targets.append((attrs['src'], True))
            if tag == 'source' and attrs.get('srcset'):
                targets.extend((s.strip().split()[0], True) for s in attrs['srcset'].split(',') if s.strip())
            if tag == 'a' and attrs.get('href'): targets.append((attrs['href'], False))
            if tag in {'script', 'iframe', 'object', 'embed', 'style'} or any(k.lower().startswith('on') for k in attrs):
                problems.append(f'Unsupported active HTML: {tag}')

    html = HTMLReferences()
    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            level = int(token.tag[1:])
            title = tokens[index + 1].content
            headings.append({'level': level, 'text': title, 'line': token.map[0] + 1})
            if previous and level > previous + 1: warnings.append(f'Heading level skips at {title}')
            previous = level
        if token.type == 'fence':
            fences.append({'line': token.map[0] + 1, 'language': token.info})
            if not token.info.strip(): warnings.append(f'Code fence lacks a language at line {token.map[0] + 1}')
        if token.type in {'html_block', 'html_inline'}: html.feed(token.content)
        if token.type != 'inline': continue
        if index and tokens[index - 1].type == 'paragraph_open': paragraphs.append(token.content)
        for child in token.children or []:
            if child.type == 'image':
                if not child.content.strip(): problems.append('Markdown image has no useful alt text')
                targets.append((child.attrGet('src') or '', True))
            elif child.type == 'link_open': targets.append((child.attrGet('href') or '', False))
            elif child.type == 'html_inline': html.feed(child.content)
    if not headings: warnings.append('No Markdown headings; inspect the reading hierarchy')
    local = []
    for target, is_image in dict.fromkeys(targets):
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            if parts.scheme in {'http', 'https'} or parts.netloc: remote.append(target)
            elif parts.scheme not in {'mailto'}: problems.append(f'Unsupported URL scheme: {parts.scheme}')
            continue
        if not parts.path: continue  # Anchor semantics need the final renderer.
        resolved = (root / unquote(parts.path).lstrip('/') if parts.path.startswith('/') else path.parent / unquote(parts.path)).resolve()
        try: relative = resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            problems.append(f'Local reference escapes repository: {target}'); continue
        if not resolved.exists(): problems.append(f'Missing local reference: {target}'); continue
        if is_image and not resolved.is_file(): problems.append(f'Image is not a file: {target}'); continue
        local.append(relative)
        if is_image and resolved.suffix.lower() == '.svg': problems.extend(f'{target}: {p}' for p in audit_svg(resolved))
    prose = '\n'.join(paragraphs)
    sentences = [s for s in re.split(r'[.!?。！？]+', prose) if s.strip()]
    cjk = len(re.findall(r'[\u3400-\u9fff]', prose))
    words = re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", prose)
    long_sentences = sum(len(re.findall(r'\b[A-Za-z]+\b', s)) > 35 for s in sentences)
    if long_sentences: warnings.append(f'{long_sentences} long English sentences: inspect, do not split mechanically')
    if any(re.search(r'\b(TODO|TBD|YOUR_PROJECT|YOUR_USERNAME)\b', p) for p in paragraphs):
        warnings.append('Possible placeholders in prose; verify against repository context')
    return {
        'format': 'mz.readme-quality/1',
        'readme': {'path': path.resolve().relative_to(root.resolve()).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
        'status': 'FAIL' if problems else 'PASS', 'problems': list(dict.fromkeys(problems)),
        'warnings': list(dict.fromkeys(warnings)), 'headings': headings, 'codeFences': fences,
        'metrics': {'englishWords': len(words), 'cjkCharacters': cjk, 'paragraphs': len(paragraphs), 'longEnglishSentences': long_sentences},
        'localReferences': sorted(set(local)), 'unverifiedRemoteReferences': sorted(set(remote)),
        'limitations': ['No truth, aesthetic, command-execution, remote-link, or live GitHub validation.',
                        'English sentence lengths are diagnostic only; they are not Chinese readability thresholds.'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('readme', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try: report = audit(args.readme.resolve(), args.root.resolve())
    except (OSError, ValueError, RuntimeError) as exc: parser.error(str(exc))
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + '\n', encoding='utf-8')
    print(payload)
    return 1 if report['status'] == 'FAIL' else 0


if __name__ == '__main__': raise SystemExit(main())
