#!/usr/bin/env python3
"""Create an isolated raw README task; never overwrite an existing evaluation."""
import argparse
from pathlib import Path

SOURCE = '''"""Build a deterministic JSON index of non-empty text lines."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = [{'line': n, 'text': text.strip()} for n, text in enumerate(args.input.read_text(encoding='utf-8').splitlines(), 1) if text.strip()]
    result = {'count': len(rows), 'rows': rows}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
    print(f'{len(rows)} rows written to {args.output.name}')


if __name__ == '__main__':
    main()
'''
BASELINE = '''# Linepack

A powerful blazing-fast AI-powered universal data pipeline with enterprise support and CSV export. Streamline heterogeneous workflows with comprehensive high-performance features.

## Architecture

Uses Python internals and standard library modules to process files.

## Install

Python 3.10 or later. No third-party packages.

## Usage

```sh
python linepack.py --file sample.txt --out result.csv
```

It handles your data seamlessly.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    if root.exists(): parser.error('output must be a new directory')
    root.mkdir(parents=True)
    (root / 'linepack.py').write_text(SOURCE, encoding='utf-8')
    (root / 'sample.txt').write_text('red fox\n\nblue bird\n', encoding='utf-8')
    (root / 'README.md').write_text(BASELINE, encoding='utf-8')
    print(root)


if __name__ == '__main__': main()
