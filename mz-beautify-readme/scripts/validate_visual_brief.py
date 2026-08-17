#!/usr/bin/env python3
"""Validate an Engine brief against the bundled README snapshot."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("brief")
    parser.add_argument("--extension")
    args = parser.parse_args()
    snapshot = Path(__file__).resolve().parents[1] / "references" / "visual-engine"
    sys.path.insert(0, str(snapshot / "scripts"))
    from engine_lib import ContractError, load_catalog, validate_brief
    try:
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        catalog = load_catalog(snapshot, extension_root=Path(args.extension) if args.extension else None)
        validate_brief(brief, catalog)
        if brief.get("status") != "RESOLVED" or brief.get("asset", {}).get("profile") != "readme-visual":
            raise ContractError("brief is not a resolved README visual handoff")
        if brief.get("target") != {"skill": "mz-beautify-readme", "mode": "readme"}:
            raise ContractError("brief target does not match the README Skill")
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
