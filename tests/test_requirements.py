import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('requirements', Path(__file__).parents[1] / 'tools/requirements.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def req(uid, status='Draft', parent=None, category=None):
    result = f'\n[REQUIREMENT]\nUID: {uid}\nTITLE: Example\nSTATEMENT: The user shall repeat a run.\nSTATUS: {status}\n'
    if category: result += f'CATEGORY: {category}\n'
    if parent: result += f'RELATIONS:\n- TYPE: Parent\n  VALUE: {parent}\n'
    return result


class FakeGitHub:
    def __init__(self):
        self.issue = {'number': 1, 'state': 'closed', 'body': r.with_block('User text', ['SW-001'])}
        self.pr = {'number': 2, 'body': 'Human PR description\nResolves #1'}
        self.writes = []
    def pages(self, endpoint):
        return [self.issue] if '/issues?' in endpoint else [self.pr]
    def linked(self, repo, number): return [self.issue]
    def call(self, endpoint, payload=None):
        if payload:
            self.writes.append(payload)
            self.pr.update(payload)
        return self.pr.copy()


class RequirementsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def initialize(self, profile='stakeholder-software'):
        r.initialize(self.root, profile)
    def add(self, level, text):
        path = self.root / f'docs/requirements/{level}.sdoc'
        path.write_text(path.read_text() + text)
    def test_init_preserves_content_and_rejects_profile_switch(self):
        self.initialize()
        self.add('stakeholder', req('STK-001'))
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.initialize()
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        with self.assertRaises(ValueError): self.initialize('software')
    def test_draft_partial_then_approved_relations(self):
        self.initialize()
        self.add('stakeholder', req('STK-001'))
        self.add('software', req('SW-001', category='Functional'))
        self.assertFalse(r.validate(self.root, 'stakeholder-software')[1])
        path = self.root / 'docs/requirements/software.sdoc'
        path.write_text(path.read_text().replace('STATUS: Draft', 'STATUS: Approved'))
        self.assertTrue(r.validate(self.root, 'stakeholder-software')[1])
        path.write_text(path.read_text() + 'RELATIONS:\n- TYPE: Parent\n  VALUE: STK-001\n')
        self.assertFalse(r.validate(self.root, 'stakeholder-software')[1])
    def test_duplicate_unknown_parent_category_and_retired(self):
        self.initialize()
        self.add('software', req('SW-001', 'Retired', 'MISSING-1', 'bad'))
        self.add('software', req('SW-001', category='Functional'))
        errors = str(r.validate(self.root, 'stakeholder-software')[1])
        for word in ('duplicate', 'CATEGORY', 'retirement', 'does not exist'):
            self.assertIn(word, errors)
    def test_all_profiles_and_software_only_approval(self):
        for profile in r.PROFILES:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                r.initialize(root, profile)
                self.assertEqual(set(p.stem for p in (root / 'docs/requirements').glob('*.sdoc')), set(r.PROFILES[profile]))
        self.initialize('software')
        self.add('software', req('SW-001', 'Approved', category='Functional'))
        self.assertFalse(r.validate(self.root, 'software')[1])
    def test_existing_uid_is_preserved_by_document_level(self):
        self.initialize('software')
        self.add('software', req('REQ-LEGACY-001', category='Functional'))
        index, errors = r.validate(self.root, 'software')
        self.assertFalse(errors)
        self.assertIn('REQ-LEGACY-001', index)

    def test_cyclic_relations(self):
        self.initialize()
        self.add('stakeholder', req('STK-001', parent='SW-001'))
        self.add('software', req('SW-001', parent='STK-001', category='Functional'))
        self.assertIn('cyclic', str(r.validate(self.root, 'stakeholder-software')[1]))
    def test_blocks_preserve_text_empty_and_ambiguous(self):
        body = 'Before\n' + r.with_block('', ['SW-002', 'SW-001']) + '\nAfter'
        new = r.with_block(body, [])
        self.assertTrue(new.startswith('Before\n'))
        self.assertTrue(new.endswith('\nAfter'))
        self.assertEqual([], r.block_ids(new))
        self.assertEqual(new, r.with_block(new, []))
        with self.assertRaises(ValueError): r.with_block(body + r.START, [])
    def test_sync_closed_issue_union_idempotency_and_unknown(self):
        api = FakeGitHub()
        r.synchronize(self.root, {'SW-001': {}}, 'a/b', api, True)
        self.assertEqual(1, len(api.writes))
        self.assertTrue(api.pr['body'].startswith('Human PR description\nResolves #1'))
        self.assertEqual(['SW-001'], r.block_ids(api.pr['body']))
        r.synchronize(self.root, {'SW-001': {}}, 'a/b', api, True)
        self.assertEqual(1, len(api.writes))
        api.issue['body'] = r.with_block('', ['SW-UNKNOWN'])
        with self.assertRaises(ValueError): r.synchronize(self.root, {}, 'a/b', api, True)
        self.assertEqual(1, len(api.writes))
    def test_sync_preserves_edit_during_link_lookup(self):
        api = FakeGitHub()
        original = api.linked
        calls = []
        def linked(repo, number):
            calls.append(number)
            if len(calls) == 2:
                api.pr['body'] = 'Fresh human edit\nResolves #1'
            return original(repo, number)
        api.linked = linked
        r.synchronize(self.root, {'SW-001': {}}, 'a/b', api, True)
        self.assertTrue(api.pr['body'].startswith('Fresh human edit\nResolves #1'))

    def test_strictdoc_export_with_real_grammar_and_links(self):
        import subprocess
        import shutil
        self.initialize()
        self.add('stakeholder', req('STK-001'))
        self.add('software', req('SW-001', parent='STK-001', category='Functional'))
        result = subprocess.run([shutil.which('strictdoc'), 'export', 'docs/requirements',
            '--config', 'strictdoc_config.py', '--output-dir', 'build/html', '--no-parallelization'],
            cwd=self.root, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue(list((self.root/'build/html').rglob('*.html')))

    def test_off_runs_without_strictdoc_and_without_changes(self):
        import subprocess
        (self.root / 'heven.toml').write_text('[requirements]\nenabled=false\nprofile="software"\n')
        import sys
        result = subprocess.run([sys.executable, str(r.ROOT/'tools/requirements.py'), 'sync', '--root', str(self.root), '--apply'], capture_output=True)
        self.assertEqual(0, result.returncode)
        self.assertEqual(['heven.toml'], [p.name for p in self.root.iterdir()])

if __name__ == '__main__': unittest.main()
