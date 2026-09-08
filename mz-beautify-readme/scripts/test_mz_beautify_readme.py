#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import importlib.util
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


brief = load("validate_brief")
asset = load("validate_asset_manifest")
comparator = load("compare_core_decisions")
planner = load("plan_localized_assets")
balance = load("audit_visual_balance")
UPSTREAM = "55bdb1c05414cd7a0cf911d02e55ece79777206e"
HASH = "1" * 64


def visual_brief(preset="mz-readme-project-native-v1", extension=None):
    value = {
        "format": "mz.visual-brief/1", "engineVersion": "2.0.0", "status": "RESOLVED",
        "asset": {"profile": "readme-visual"}, "style": {"preset": {"id": preset}},
        "target": {"skill": "mz-beautify-readme", "mode": "readme"},
        "engineCompat": {"format": "mz.engine-compat/1", "engineVersion": "2.0.0", "target": "readme", "snapshotHash": HASH, "sourceCatalogHash": HASH},
    }
    if extension: value["extension"] = extension
    return value


def valid_brief():
    return {
        "format": "mz.readme-brief/3", "scope": "readme", "repository": "owner/example",
        "audience": "Developers", "oneSentenceValue": "Show real output first.", "primaryProof": "output.png", "firstSuccessfulAction": "Run it.",
        "coreDecision": {"upstreamCommit": UPSTREAM, "compositionMode": "artifact-wall", "implementation": "hybrid", "motion": "none", "motionAuthorized": False,
                         "themeSpec": {"palette": "project native", "typography": "project native", "shape": "artifact cards", "motif": "real output", "composition": "artifact wall"}},
        "visualBrief": visual_brief(), "proofSources": ["output.png"],
        "heroCopy": {"title": "Example", "value": "Show real output first."},
        "lockedCopy": ["Example", "Show real output first."], "status": "READY_FOR_REVIEW",
    }


class BriefTests(unittest.TestCase):
    def test_valid_v3(self): self.assertEqual([], brief.validate(valid_brief()))
    def test_extension_is_explicit_visual_data(self):
        data = valid_brief(); data["visualBrief"] = visual_brief("brand-readme-v1", {"id": "brand-system", "namespace": "brand", "version": "1.0.0", "manifestHash": "2" * 64})
        self.assertEqual([], brief.validate(data))
    def test_wrong_visual_target_fails(self):
        data = valid_brief(); data["visualBrief"]["target"] = {"skill": "other", "mode": "readme"}
        self.assertIn("visualBrief target must be mz-beautify-readme/readme", brief.validate(data))
    def test_owner_does_not_change_public_route(self):
        data = valid_brief(); data["repository"] = "MuziGeek/example"
        self.assertEqual("mz-readme-project-native-v1", data["visualBrief"]["style"]["preset"]["id"])
        self.assertEqual([], brief.validate(data))
    def test_gif_authorization(self):
        data = valid_brief(); data["coreDecision"].update(motion="gif", motionAuthorized=False)
        self.assertIn("GIF requires explicit motion authorization", brief.validate(data))
    def test_localized_copy_lock(self):
        data = valid_brief(); data["localization"] = {"primaryLocale": "en", "outputLocales": ["en", "zh-CN"], "assetStrategy": "localized-assets", "readmeFiles": {"en": "README.md", "zh-CN": "README.zh-CN.md"}}
        data["localizedHeroCopy"] = {"zh-CN": {"title": "示例", "value": "展示真实结果。"}}
        self.assertTrue(any("lockedCopy" in item for item in brief.validate(data)))
    def test_invariance(self):
        left = valid_brief(); right = valid_brief(); right["visualBrief"] = visual_brief("brand-readme-v1", {"id": "brand-system", "namespace": "brand", "version": "1.0.0", "manifestHash": "2" * 64})
        self.assertEqual([], comparator.compare(left, right))
        right["coreDecision"]["compositionMode"] = "split"
        self.assertTrue(comparator.compare(left, right))

    def test_public_engine_handoff_validates(self):
        snapshot = HERE.parent / "references" / "visual-engine"
        sys.path.insert(0, str(snapshot / "scripts"))
        from engine_lib import load_catalog, resolve_intent
        resolved = resolve_intent({
            "format": "mz.intent/1", "request": "README hero", "asset": {"profile": "readme-visual"},
            "style": {"preset": "mz-readme-project-native-v1", "modifiers": []},
        }, load_catalog(snapshot))
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "visual-brief.json"
            path.write_text(__import__("json").dumps(resolved), encoding="utf-8")
            result = subprocess.run([sys.executable, str(HERE / "validate_visual_brief.py"), str(path)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class LocalizationPlanTests(unittest.TestCase):
    def test_stable_multilingual_names(self):
        result = planner.plan("en", ["en", "zh-CN"], "webp", True)
        self.assertEqual({"desktop": "hero.webp", "mobile": "hero.mobile.webp"}, result["assets"]["en"])
        self.assertEqual({"desktop": "hero.zh-CN.webp", "mobile": "hero.zh-CN.mobile.webp"}, result["assets"]["zh-CN"])
    def test_primary_must_be_present(self):
        with self.assertRaises(ValueError): planner.plan("en", ["zh-CN"], "svg", False)


class VisualBalanceTests(unittest.TestCase):
    def test_balanced_canvas_passes(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "balanced.png"; image = Image.new("RGB", (200, 100), (250, 247, 239)); ImageDraw.Draw(image).rectangle((20, 10, 180, 88), fill=(23, 53, 87)); image.save(path)
            self.assertEqual([], balance.validate(balance.measure(path)))
    def test_dominant_bottom_band_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bottom-heavy.png"; image = Image.new("RGB", (200, 100), (250, 247, 239)); ImageDraw.Draw(image).rectangle((20, 8, 180, 48), fill=(23, 53, 87)); image.save(path)
            self.assertIn("dominant empty bottom band", balance.validate(balance.measure(path)))


class AssetTests(unittest.TestCase):
    def test_v3_hashes(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in ("hero.svg", "brief.json", "visual-brief.json"): (root / name).write_text(name, encoding="utf-8")
            record = lambda name: {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}
            data = {"format": "mz.readme-asset/3", "status": "DRAFT", "repository": "owner/example", "upstreamCore": {"repository": "oil-oil/beautify-github-readme", "commit": UPSTREAM}, "brief": record("brief.json"), "visualBrief": record("visual-brief.json"), "publishedAsset": record("hero.svg"), "sources": [record("hero.svg")], "validation": {"safe": True}}
            self.assertEqual([], asset.validate(data, root)); data["publishedAsset"]["sha256"] = "0" * 64; self.assertTrue(any("hash mismatch" in item for item in asset.validate(data, root)))
    def test_multilingual_variant_coverage(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for name in ("hero.webp", "hero.mobile.webp", "hero.zh-CN.webp", "hero.zh-CN.mobile.webp", "brief.json", "visual-brief.json"): (root / name).write_bytes(name.encode())
            record = lambda name, locale=None, viewport=None: {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest(), **({"locale": locale, "viewport": viewport} if locale else {})}
            data = {"format": "mz.readme-asset/3", "status": "DRAFT", "repository": "owner/example", "upstreamCore": {"repository": "oil-oil/beautify-github-readme", "commit": UPSTREAM}, "localization": {"primaryLocale": "en", "outputLocales": ["en", "zh-CN"]}, "brief": record("brief.json"), "visualBrief": record("visual-brief.json"), "publishedAsset": record("hero.webp", "en", "desktop"), "variants": [record("hero.mobile.webp", "en", "mobile"), record("hero.zh-CN.webp", "zh-CN", "desktop"), record("hero.zh-CN.mobile.webp", "zh-CN", "mobile")], "sources": [record("brief.json")], "validation": {"safe": True}}
            self.assertEqual([], asset.validate(data, root)); data["variants"].pop(); self.assertIn("every output locale must provide the same viewport set", asset.validate(data, root))


if __name__ == "__main__": unittest.main()
