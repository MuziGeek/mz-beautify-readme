#!/usr/bin/env python3
"""Bind README review evidence to current files. Never infer user satisfaction."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

CHECKS = {'truth', 'first-use', 'copy', 'visual', 'scope'}
SHA = re.compile(r'^[0-9a-f]{64}$')


def record(path: Path, root: Path) -> dict:
    return {'path': path.resolve().relative_to(root.resolve()).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def read_ref(ref: object, root: Path, errors: list, label: str) -> Path | None:
    if not isinstance(ref, dict) or not isinstance(ref.get('path'), str) or not isinstance(ref.get('sha256'), str):
        errors.append(f'{label}: requires path and sha256'); return None
    relative = ref['path']
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or '..' in pure.parts or '\\' in relative or ':' in relative:
        errors.append(f'{label}: unsafe relative path'); return None
    path = (root / relative).resolve()
    try: path.relative_to(root.resolve())
    except ValueError: errors.append(f'{label}: path escapes root'); return None
    if not SHA.fullmatch(ref['sha256']): errors.append(f'{label}: invalid SHA-256'); return None
    if not path.is_file(): errors.append(f'{label}: missing {relative}'); return None
    if hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
        errors.append(f'{label}: stale evidence {relative}'); return None
    return path


def read_json(path: Path | None, errors: list, label: str) -> dict:
    if path is None: return {}
    try: data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError): errors.append(f'{label}: invalid JSON'); return {}
    if not isinstance(data, dict): errors.append(f'{label}: expected object'); return {}
    return data


def validate(data: object, root: Path, expected_files: list[dict] | None = None, expected_locales: list[str] | None = None) -> list[str]:
    if not isinstance(data, dict): return ['review must be an object']
    errors = []
    if data.get('format') != 'mz.readme-review/1': errors.append('format must be mz.readme-review/1')
    if data.get('status') != 'READY_FOR_REVIEW': errors.append('review is not READY_FOR_REVIEW')
    if data.get('scope') not in {'readme', 'asset-only'}: errors.append('review scope must be readme or asset-only')
    if data.get('userAcceptance') != 'PENDING': errors.append('technical review must leave userAcceptance PENDING')
    inputs = data.get('inputs')
    if not isinstance(inputs, list) or not inputs: errors.append('inputs must bind current deliverables'); inputs = []
    bound = {}
    for i, ref in enumerate(inputs):
        if read_ref(ref, root, errors, f'inputs[{i}]'):
            if ref['path'] in bound: errors.append('duplicate input path')
            bound[ref['path']] = ref['sha256']
    for ref in expected_files or []:
        if bound.get(ref.get('path')) != ref.get('sha256'): errors.append(f"review does not bind deliverable: {ref.get('path')}")
    readmes = data.get('readmes')
    if not isinstance(readmes, dict) or not readmes: errors.append('readmes must map every locale to its preview subject'); readmes = {}
    if expected_locales is not None and set(readmes) != set(expected_locales): errors.append('review locales differ from declared output locales')
    for locale, ref in readmes.items():
        if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', locale): errors.append('invalid review locale')
        if read_ref(ref, root, errors, f'readmes.{locale}') and bound.get(ref['path']) != ref['sha256']:
            errors.append(f'{locale}: README not bound in inputs')
        if isinstance(ref, dict) and bound.get(ref.get('path')) == ref.get('sha256'):
            from audit_readme_quality import audit
            try:
                diagnostics = audit(root / ref['path'], root)
                errors.extend(f'{locale}: {p}' for p in diagnostics['problems'])
            except (OSError, ValueError, RuntimeError) as exc: errors.append(f'{locale}: quality audit unavailable: {exc}')
    checks = data.get('checks')
    if not isinstance(checks, list): checks = []
    ids = [c.get('id') for c in checks if isinstance(c, dict) and isinstance(c.get('id'), str)]
    if len(ids) != len(set(ids)) or set(ids) != CHECKS: errors.append('checks must contain truth, first-use, copy, visual, scope exactly once')
    for check in checks:
        if not isinstance(check, dict): errors.append('invalid check'); continue
        key = check.get('id')
        status = check.get('status')
        if status != 'PASS' and not (key == 'first-use' and status == 'NOT_APPLICABLE'):
            errors.append(f'{key}: unresolved check')
        if not isinstance(check.get('note'), str) or not check['note'].strip(): errors.append(f'{key}: concrete observation is required')
        evidence = check.get('evidence')
        if not isinstance(evidence, list) or not evidence: errors.append(f'{key}: file evidence is required'); evidence = []
        for i, ref in enumerate(evidence): read_ref(ref, root, errors, f'{key}.evidence[{i}]')
    renders = data.get('renders')
    if not isinstance(renders, list) or not renders: errors.append('render reports are required'); renders = []
    seen_locales, captures = set(), set()
    for i, ref in enumerate(renders):
        report_path = read_ref(ref, root, errors, f'renders[{i}]')
        report = read_json(report_path, errors, f'renders[{i}]')
        locale = report.get('locale')
        if not isinstance(locale, str) or locale not in readmes: errors.append('render locale missing from readmes'); continue
        if locale in seen_locales: errors.append('duplicate render locale')
        seen_locales.add(locale)
        if report.get('format') != 'mz.readme-render/1' or report.get('status') != 'PASS': errors.append(f'{locale}: render did not pass')
        if report.get('readme') != readmes[locale]: errors.append(f'{locale}: render refers to another README revision')
        render_inputs = report.get('inputs')
        if not isinstance(render_inputs, list) or not render_inputs: errors.append(f'{locale}: render input hashes missing'); render_inputs = []
        for item in render_inputs:
            if read_ref(item, root, errors, f'{locale}.renderInput') and bound.get(item['path']) != item['sha256']:
                errors.append(f'{locale}: rendered input absent from review inputs')
        shots = report.get('captures')
        if not isinstance(shots, list): shots = []
        matrix = set()
        for shot in shots:
            if not isinstance(shot, dict): errors.append('invalid capture'); continue
            width, theme, images = shot.get('width'), shot.get('theme'), shot.get('images')
            if width not in (900, 360) or theme not in ('light', 'dark') or not isinstance(images, bool):
                errors.append(f'{locale}: invalid capture coordinates'); continue
            key = (width, theme, images)
            if key in matrix: errors.append(f'{locale}: duplicate capture coordinates')
            matrix.add(key)
            if shot.get('problems') != []: errors.append(f'{locale}: capture has unresolved problems')
            path = read_ref(shot, report_path.parent, errors, f'{locale}.capture') if report_path else None
            if path:
                try:
                    from PIL import Image
                    with Image.open(path) as im:
                        if im.width < width: errors.append(f'{locale}: screenshot narrower than declared content width')
                        im.verify()
                except (OSError, ValueError): errors.append(f'{locale}: invalid screenshot image')
                captures.add((locale, width, theme, images, shot['sha256']))
        required = {(w, t, True) for w in (900, 360) for t in ('light', 'dark')} | {(360, t, False) for t in ('light', 'dark')}
        if not required <= matrix: errors.append(f'{locale}: incomplete desktop/mobile, light/dark, image-fallback matrix')
    if seen_locales != set(readmes): errors.append('every locale requires a render report')
    observations = data.get('observations')
    if not isinstance(observations, list): observations = []
    inspected = set()
    for observation in observations:
        if not isinstance(observation, dict): errors.append('invalid visual observation'); continue
        coordinates = (observation.get('locale'), observation.get('width'), observation.get('theme'), observation.get('images'), observation.get('captureSha256'))
        try: matched = coordinates in captures
        except TypeError: matched = False
        if not matched: errors.append('observation does not match a current screenshot'); continue
        if coordinates in inspected: errors.append('duplicate visual observation')
        inspected.add(coordinates)
        if observation.get('verdict') != 'PASS': errors.append('unresolved visual observation')
        if not isinstance(observation.get('findings'), str) or not observation['findings'].strip(): errors.append('visual observation needs findings')
    if inspected != captures: errors.append('every screenshot must be visually inspected; generation alone is insufficient')
    return list(dict.fromkeys(errors))


def initialize(root: Path, render_paths: list[Path], extra: list[Path], scope: str) -> dict:
    inputs, readmes, renders, observations = {}, {}, [], []
    for path in render_paths:
        report = json.loads(path.read_text(encoding='utf-8'))
        locale = report['locale']
        if locale in readmes: raise ValueError('duplicate locale')
        readmes[locale] = report['readme']
        renders.append(record(path, root))
        for ref in report['inputs']: inputs[ref['path']] = ref
        for shot in report['captures']:
            observations.append({'locale': locale, 'width': shot['width'], 'theme': shot['theme'], 'images': shot['images'],
                                 'captureSha256': shot['sha256'], 'verdict': 'UNVERIFIED', 'findings': ''})
    for path in extra:
        ref = record(path, root); inputs[ref['path']] = ref
    return {'format': 'mz.readme-review/1', 'scope': scope, 'status': 'DRAFT', 'userAcceptance': 'PENDING',
            'inputs': list(inputs.values()), 'readmes': readmes, 'renders': renders,
            'checks': [{'id': key, 'status': 'UNVERIFIED', 'note': '', 'evidence': []} for key in sorted(CHECKS)],
            'observations': observations}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('review', type=Path, help='Place the review JSON at the target repository root')
    parser.add_argument('--init', action='store_true', help='Create a DRAFT; never invent review outcomes')
    parser.add_argument('--render', action='append', default=[], type=Path)
    parser.add_argument('--input', action='append', default=[], type=Path)
    parser.add_argument('--scope', choices=['readme', 'asset-only'], default='readme')
    args = parser.parse_args()
    path = args.review.resolve()
    try:
        if args.init:
            if path.exists(): raise ValueError('refusing to overwrite an existing review; use a new revision path')
            if not args.render: raise ValueError('--init needs at least one --render')
            data = initialize(path.parent, [p.resolve() for p in args.render], [p.resolve() for p in args.input], args.scope)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(f'DRAFT created: {path}. Inspect screenshots and attach factual evidence before validation.'); return 0
        data = json.loads(path.read_text(encoding='utf-8'))
        errors = validate(data, path.parent)
    except (OSError, ValueError, KeyError) as exc: parser.error(str(exc))
    if errors: print('REVIEW VALIDATION FAILED\n' + '\n'.join(f'- {e}' for e in errors)); return 1
    print('READY_FOR_REVIEW evidence verified. User acceptance remains PENDING.'); return 0


if __name__ == '__main__': raise SystemExit(main())
