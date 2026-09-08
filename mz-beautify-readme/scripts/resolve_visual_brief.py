#!/usr/bin/env python3
"""Resolve an explicit README intent using the bundled public Engine snapshot."""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('intent', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--extension', type=Path)
    args = parser.parse_args()
    snapshot = Path(__file__).resolve().parents[1] / 'references' / 'visual-engine'
    sys.path.insert(0, str(snapshot / 'scripts'))
    from engine_lib import ContractError, load_catalog, resolve_intent, validate_brief
    try:
        intent = json.loads(args.intent.read_text(encoding='utf-8'))
        if intent.get('asset', {}).get('profile') != 'readme-visual': raise ValueError('intent must target readme-visual')
        catalog = load_catalog(snapshot, extension_root=args.extension)
        brief = resolve_intent(intent, catalog)
        validate_brief(brief, catalog)
        if brief.get('status') != 'RESOLVED': raise ValueError('intent did not resolve; inspect the requested preset and Extension')
        with args.output.open('x', encoding='utf-8') as stream: stream.write(json.dumps(brief, ensure_ascii=False, indent=2) + '\n')
    except (OSError, ValueError, ContractError) as exc: parser.error(str(exc))
    print(f'RESOLVED: {args.output}'); return 0


if __name__ == '__main__': raise SystemExit(main())
