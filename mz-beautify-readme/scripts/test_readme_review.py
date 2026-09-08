#!/usr/bin/env python3
"""Behavioral regressions for evidence freshness, coverage, and Markdown diagnostics."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from audit_readme_quality import audit
from validate_readme_review import record, validate
from validate_asset_manifest import validate as validate_asset
from test_mz_beautify_readme import valid_brief, UPSTREAM


def dump(path, data):
    path.write_text(json.dumps(data), encoding='utf-8')


def fixture(root):
    (root / 'README.md').write_text('# Example\n\nReadable output.\n', encoding='utf-8')
    (root / 'evidence.md').write_text('Test fixture evidence; not an aesthetic judgment.', encoding='utf-8')
    Image.new('RGB', (90, 40), '#32546d').save(root / 'hero.png')
    b = valid_brief(); b['scope'] = 'readme'
    dump(root / 'brief.json', b); dump(root / 'visual.json', b['visualBrief'])
    rr = {'format': 'mz.readme-render/1', 'locale': 'en', 'status': 'PASS', 'readme': record(root / 'README.md', root),
          'inputs': [record(root / n, root) for n in ['README.md', 'hero.png']], 'captures': []}
    observations = []
    for width in (900, 360):
        for theme in ('light', 'dark'):
            for images in (True, False):
                name = f'{width}-{theme}-{images}.png'
                Image.new('RGB', (width, 60), '#132536' if theme == 'dark' else '#f5f3ec').save(root / name)
                shot = {**record(root / name, root), 'width': width, 'theme': theme, 'images': images, 'problems': []}
                rr['captures'].append(shot)
                observations.append({'locale': 'en', 'width': width, 'theme': theme, 'images': images, 'captureSha256': shot['sha256'],
                                     'verdict': 'PASS', 'findings': 'Synthetic unit fixture only; actual use must inspect the image.'})
    dump(root / 'render.json', rr)
    review = {'format': 'mz.readme-review/1', 'scope': 'readme', 'status': 'READY_FOR_REVIEW', 'userAcceptance': 'PENDING',
              'inputs': [record(root / n, root) for n in ['README.md', 'hero.png', 'brief.json', 'visual.json']],
              'readmes': {'en': record(root / 'README.md', root)}, 'renders': [record(root / 'render.json', root)],
              'checks': [{'id': k, 'status': 'PASS', 'note': 'Synthetic fixture', 'evidence': [record(root / 'evidence.md', root)]}
                         for k in ('truth', 'first-use', 'copy', 'visual', 'scope')], 'observations': observations}
    dump(root / 'review.json', review)
    manifest = {'format': 'mz.readme-asset/3', 'status': 'READY_FOR_REVIEW', 'repository': b['repository'],
                'upstreamCore': {'repository': 'oil-oil/beautify-github-readme', 'commit': UPSTREAM},
                'brief': record(root / 'brief.json', root), 'visualBrief': record(root / 'visual.json', root),
                'publishedAsset': record(root / 'hero.png', root), 'sources': [record(root / 'hero.png', root)],
                'validation': {'safe': True}, 'review': record(root / 'review.json', root)}
    return review, rr, manifest


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.review, self.render, self.manifest = fixture(self.root)

    def test_complete_evidence_passes(self):
        self.assertEqual([], validate(self.review, self.root))
        self.assertEqual([], validate_asset(self.manifest, self.root))

    def test_boolean_only_ready_cannot_pass(self):
        del self.manifest['review']
        self.assertTrue(validate_asset(self.manifest, self.root))

    def test_stale_readme_fails(self):
        (self.root / 'README.md').write_text('# Changed', encoding='utf-8')
        self.assertTrue(any('stale' in e for e in validate(self.review, self.root)))

    def test_stale_asset_fails(self):
        Image.new('RGB', (90, 40), 'red').save(self.root / 'hero.png')
        self.assertTrue(validate(self.review, self.root))

    def test_evidence_changed_fails(self):
        (self.root / 'evidence.md').write_text('changed result', encoding='utf-8')
        self.assertTrue(validate(self.review, self.root))

    def test_screenshot_changed_fails(self):
        shot = self.render['captures'][0]
        (self.root / shot['path']).write_bytes(b'not a screenshot')
        self.assertTrue(validate(self.review, self.root))

    def test_missing_mobile_dark_cannot_be_averaged_away(self):
        self.render['captures'] = [s for s in self.render['captures'] if not (s['width'] == 360 and s['theme'] == 'dark')]
        dump(self.root / 'render.json', self.render)
        self.review['renders'] = [record(self.root / 'render.json', self.root)]
        self.assertTrue(any('incomplete' in e for e in validate(self.review, self.root)))

    def test_successful_render_without_observation_fails(self):
        self.review['observations'].pop()
        self.assertTrue(any('visually inspected' in e for e in validate(self.review, self.root)))

    def test_observation_of_old_capture_fails(self):
        self.review['observations'][0]['captureSha256'] = 'f' * 64
        self.assertTrue(validate(self.review, self.root))

    def test_user_approval_cannot_be_technical_status(self):
        self.review['userAcceptance'] = 'ACCEPTED'
        self.assertTrue(validate(self.review, self.root))

    def test_expected_locale_cannot_be_omitted(self):
        self.assertTrue(validate(self.review, self.root, expected_locales=['en', 'zh-CN']))

    def test_unknown_check_does_not_replace_required_check(self):
        self.review['checks'][0]['id'] = 'looks-great'
        self.assertTrue(validate(self.review, self.root))

    def test_unverified_first_use_fails(self):
        self.review['checks'][1]['status'] = 'UNVERIFIED'
        self.assertTrue(validate(self.review, self.root))

    def test_review_must_bind_all_manifest_sources(self):
        (self.root / 'layout.svg').write_text('source layer', encoding='utf-8')
        self.manifest['sources'].append(record(self.root / 'layout.svg', self.root))
        self.assertTrue(any('does not bind' in e for e in validate_asset(self.manifest, self.root)))

    def test_path_escape_fails(self):
        self.review['inputs'][0]['path'] = '../outside.md'
        self.assertTrue(validate(self.review, self.root))

    def test_forged_non_image_file_fails(self):
        shot = self.render['captures'][0]
        (self.root / shot['path']).write_text('fake', encoding='utf-8')
        shot.update(record(self.root / shot['path'], self.root))
        self.review['observations'][0]['captureSha256'] = shot['sha256']
        dump(self.root / 'render.json', self.render); self.review['renders'] = [record(self.root / 'render.json', self.root)]
        self.assertTrue(any('invalid screenshot' in e for e in validate(self.review, self.root)))


class QualityTests(unittest.TestCase):
    def run_audit(self, source):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); path = root / 'README.md'; path.write_text(source, encoding='utf-8')
            return audit(path, root)

    def test_reference_image_missing_detected(self):
        self.assertEqual('FAIL', self.run_audit('# X\n\n![proof][p]\n\n[p]: missing.svg')['status'])

    def test_code_examples_do_not_become_links_or_headings(self):
        result = self.run_audit('# X\n\n```md\n![x](missing.png)\n### fake\n```\n')
        self.assertEqual('PASS', result['status']); self.assertEqual(1, len(result['headings']))

    def test_markdown_empty_alt_fails(self):
        self.assertTrue(any('alt' in p for p in self.run_audit('# X\n\n![](https://example.invalid/x.png)')['problems']))

    def test_remote_is_unverified_not_fetched(self):
        result = self.run_audit('# X\n\n[docs](https://example.invalid/docs)')
        self.assertEqual(['https://example.invalid/docs'], result['unverifiedRemoteReferences'])

    def test_cjk_does_not_use_english_word_limit(self):
        result = self.run_audit('# 示例\n\n' + '清楚解释结果。' * 20)
        self.assertGreater(result['metrics']['cjkCharacters'], 0)
        self.assertEqual(0, result['metrics']['longEnglishSentences'])

    def test_nested_encoded_local_link(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); (root / 'docs').mkdir(); (root / 'a file.md').write_text('ok', encoding='utf-8')
            path = root / 'docs' / 'README.md'; path.write_text('# X\n\n[local](../a%20file.md)', encoding='utf-8')
            self.assertEqual('PASS', audit(path, root)['status'])


if __name__ == '__main__': unittest.main()
