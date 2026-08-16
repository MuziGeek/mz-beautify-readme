#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f"{name}.py"); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
brief=load("validate_brief"); asset=load("validate_asset_manifest"); router=load("resolve_overlay"); comparator=load("compare_core_decisions"); planner=load("plan_localized_assets"); balance=load("audit_visual_balance")
UPSTREAM="55bdb1c05414cd7a0cf911d02e55ece79777206e"

def valid_brief():
    return {"format":"mz.readme-brief/2","scope":"readme","repository":"MuziGeek/example","audience":"Developers","oneSentenceValue":"Show real output first.","primaryProof":"output.png","firstSuccessfulAction":"Run it.","coreDecision":{"upstreamCommit":UPSTREAM,"compositionMode":"artifact-wall","implementation":"hybrid","motion":"none","motionAuthorized":False,"themeSpec":{"palette":"project native","typography":"project native","shape":"artifact cards","motif":"real output","composition":"artifact wall"}},"overlay":{"id":"muzi","activationReason":"ownership-default","characterMode":"none","companionMode":"exclude","displayFont":"pfanhututi"},"proofSources":["output.png"],"heroCopy":{"title":"Example","value":"Show real output first."},"lockedCopy":["Example","Show real output first."],"status":"READY_FOR_REVIEW"}

class BriefTests(unittest.TestCase):
    def test_valid_v2(self): self.assertEqual([],brief.validate(valid_brief()))
    def test_flexible_copy(self):
        data=valid_brief(); data["heroCopy"].update(context="Context",processCue="Input to output",proofLabels=["REAL"]); data["lockedCopy"] += ["Context","Input to output","REAL"]; self.assertEqual([],brief.validate(data))
    def test_none_overlay_invariant(self):
        data=valid_brief(); data["overlay"]={"id":"none","activationReason":"third-party-default","characterMode":"muzi","companionMode":"exclude","displayFont":"project-native"}; self.assertIn("overlay none must use no character, no companion, and project-native font",brief.validate(data))
    def test_cat_and_pf_constraints(self):
        data=valid_brief(); data["overlay"]={"id":"none","activationReason":"third-party-default","characterMode":"none","companionMode":"include","displayFont":"pfanhututi"}; errors=brief.validate(data); self.assertTrue(any("cat requires" in e for e in errors)); self.assertTrue(any("PFanHuTuTi" in e for e in errors))
    def test_gif_authorization(self):
        data=valid_brief(); data["coreDecision"].update(motion="gif",motionAuthorized=False); self.assertIn("GIF requires explicit motion authorization",brief.validate(data))
    def test_localized_copy_lock(self):
        data=valid_brief(); data["localization"]={"primaryLocale":"en","outputLocales":["en","zh-CN"],"assetStrategy":"localized-assets","readmeFiles":{"en":"README.md","zh-CN":"README.zh-CN.md"}}; data["localizedHeroCopy"]={"zh-CN":{"title":"示例","value":"展示真实结果。"}}; self.assertTrue(any("lockedCopy" in e for e in brief.validate(data)))
    def test_localization_requires_all_secondary_copy(self):
        data=valid_brief(); data["localization"]={"primaryLocale":"en","outputLocales":["en","zh-CN","ja"],"assetStrategy":"localized-assets","readmeFiles":{"en":"README.md","zh-CN":"README.zh-CN.md","ja":"README.ja.md"}}; data["localizedHeroCopy"]={"zh-CN":{"title":"示例","value":"展示真实结果。"}}; self.assertIn("localizedHeroCopy keys must exactly match non-primary outputLocales",brief.validate(data))
    def test_localized_copy_requires_metadata(self):
        data=valid_brief(); data["localizedHeroCopy"]={"zh-CN":{"title":"示例","value":"展示真实结果。"}}; self.assertIn("localizedHeroCopy requires localization metadata",brief.validate(data))
    def test_invariance(self):
        left=valid_brief(); right=valid_brief(); right["overlay"]={"id":"none","activationReason":"explicit-disable","characterMode":"none","companionMode":"exclude","displayFont":"project-native"}; self.assertEqual([],comparator.compare(left,right)); right["coreDecision"]["compositionMode"]="split"; self.assertTrue(comparator.compare(left,right))

class RouterTests(unittest.TestCase):
    def test_owner_default(self): self.assertEqual("muzi",router.resolve("MuziGeek/icons")["id"])
    def test_third_party_and_mz_name(self): self.assertEqual("none",router.resolve("other/MZ-tools")["id"])
    def test_uncertain(self): self.assertEqual("uncertain-default",router.resolve("local")["activationReason"])
    def test_explicit_wins(self): self.assertEqual("none",router.resolve("MuziGeek/icons","disable")["id"]); self.assertEqual("muzi",router.resolve("other/repo","enable")["id"])

class LocalizationPlanTests(unittest.TestCase):
    def test_stable_multilingual_names(self):
        result=planner.plan("en",["en","zh-CN"],"webp",True)
        self.assertEqual({"desktop":"hero.webp","mobile":"hero.mobile.webp"},result["assets"]["en"])
        self.assertEqual({"desktop":"hero.zh-CN.webp","mobile":"hero.zh-CN.mobile.webp"},result["assets"]["zh-CN"])
    def test_primary_must_be_present(self):
        with self.assertRaises(ValueError): planner.plan("en",["zh-CN"],"svg",False)

class VisualBalanceTests(unittest.TestCase):
    def test_balanced_canvas_passes(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/"balanced.png"; image=Image.new("RGB",(200,100),(250,247,239)); ImageDraw.Draw(image).rectangle((20,10,180,88),fill=(23,53,87)); image.save(path)
            self.assertEqual([],balance.validate(balance.measure(path)))
    def test_dominant_bottom_band_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/"bottom-heavy.png"; image=Image.new("RGB",(200,100),(250,247,239)); ImageDraw.Draw(image).rectangle((20,8,180,48),fill=(23,53,87)); image.save(path)
            self.assertIn("dominant empty bottom band",balance.validate(balance.measure(path)))
    def test_dominant_internal_band_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/"split.png"; image=Image.new("RGB",(200,100),(250,247,239)); draw=ImageDraw.Draw(image); draw.rectangle((20,5,180,25),fill=(23,53,87)); draw.rectangle((20,65,180,92),fill=(23,53,87)); image.save(path)
            self.assertIn("dominant empty internal band",balance.validate(balance.measure(path)))

class AssetTests(unittest.TestCase):
    def test_v2_hashes(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw); (root/"hero.svg").write_text("<svg/>"); (root/"brief.json").write_text("{}")
            record=lambda name:{"path":name,"sha256":hashlib.sha256((root/name).read_bytes()).hexdigest()}
            data={"format":"mz.readme-asset/2","status":"READY_FOR_REVIEW","repository":"MuziGeek/example","upstreamCore":{"repository":"oil-oil/beautify-github-readme","commit":UPSTREAM},"overlayId":"muzi","brief":record("brief.json"),"publishedAsset":record("hero.svg"),"sources":[record("hero.svg")],"validation":{"safe":True}}
            self.assertEqual([],asset.validate(data,root)); data["publishedAsset"]["sha256"]="0"*64; self.assertTrue(any("hash mismatch" in e for e in asset.validate(data,root)))
    def test_multilingual_variant_coverage(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)
            for name in ("hero.webp","hero.mobile.webp","hero.zh-CN.webp","hero.zh-CN.mobile.webp","brief.json"): (root/name).write_bytes(name.encode())
            record=lambda name,locale,viewport:{"path":name,"sha256":hashlib.sha256((root/name).read_bytes()).hexdigest(),"locale":locale,"viewport":viewport}
            brief_record={"path":"brief.json","sha256":hashlib.sha256((root/"brief.json").read_bytes()).hexdigest()}
            data={"format":"mz.readme-asset/2","status":"READY_FOR_REVIEW","repository":"MuziGeek/example","upstreamCore":{"repository":"oil-oil/beautify-github-readme","commit":UPSTREAM},"overlayId":"muzi","localization":{"primaryLocale":"en","outputLocales":["en","zh-CN"]},"brief":brief_record,"publishedAsset":record("hero.webp","en","desktop"),"variants":[record("hero.mobile.webp","en","mobile"),record("hero.zh-CN.webp","zh-CN","desktop"),record("hero.zh-CN.mobile.webp","zh-CN","mobile")],"sources":[brief_record],"validation":{"safe":True}}
            self.assertEqual([],asset.validate(data,root)); data["variants"].pop(); self.assertIn("every output locale must provide the same viewport set",asset.validate(data,root))

if __name__=="__main__": unittest.main()
