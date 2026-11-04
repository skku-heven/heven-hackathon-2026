#!/usr/bin/env python3
"""HEVEN requirements: opt-in setup, validation and GitHub UID links (Python 3.11)."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    'software': ['software'],
    'stakeholder-software': ['stakeholder', 'software'],
    'system-software': ['system', 'software'],
    'stakeholder-system-software': ['stakeholder', 'system', 'software'],
    'full': ['business', 'stakeholder', 'system', 'software'],
}
PREFIX = {'BR': 'business', 'STK': 'stakeholder', 'STR': 'stakeholder',
          'SYS': 'system', 'SW': 'software', 'SWR': 'software'}
STATUS = {'Draft', 'In Review', 'Approved', 'Retired'}
CATEGORY = {'Functional', 'Non-functional/Performance Efficiency', 'Non-functional/Other'}
START = '<!-- heven:requirements:start -->'
END = '<!-- heven:requirements:end -->'


def configuration(root):
    data = tomllib.loads((root / 'heven.toml').read_text())['requirements']
    if type(data.get('enabled')) is not bool or data.get('profile') not in PROFILES:
        raise ValueError('heven.toml: enabled must be true/false; select a documented profile.')
    return data


def initialize(root, profile):
    directory = root / 'docs/requirements'
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / '.heven-profile'
    if marker.exists() and marker.read_text().strip() != profile:
        raise ValueError('Profile changed: review migration of existing requirements before updating .heven-profile.')
    planned = {'strictdoc_config.py': (ROOT / 'tools/requirements/strictdoc_config.py').read_text()}
    for level in PROFILES[profile]:
        grammar = (ROOT / f'tools/requirements/{level}.sgra').read_text()
        planned[f'docs/requirements/{level}.sdoc'] = (
            f'[DOCUMENT]\nTITLE: {level.title()} requirements\n\n{grammar}')
    for name, content in planned.items():
        path = root / name
        if not path.exists():
            path.write_text(content)
    if not marker.exists():
        marker.write_text(profile + '\n')


def runtime(root):
    """Only enabled commands install StrictDoc. Reuse a pinned, isolated environment."""
    env = root / 'build/requirements-venv'
    python = env / 'bin/python'
    installed = subprocess.run([str(python), '-c',
        'import strictdoc,sys;sys.exit(strictdoc.__version__ != "0.30.4" or sys.version_info < (3,11))'],
        capture_output=True).returncode == 0 if python.exists() else False
    if not installed:
        subprocess.run([sys.executable, '-m', 'venv', str(env)], check=True)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r',
                        str(ROOT / 'tools/requirements.txt')], check=True, stdout=sys.stderr)
    if Path(sys.executable).absolute() != python.absolute():
        os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])


def read_nodes(root):
    from strictdoc.backend.sdoc.reader import SDReader
    records = []
    def walk(contents, path):
        for node in contents:
            if hasattr(node, 'ordered_fields_lookup') and node.node_type == 'REQUIREMENT':
                fields = {key: values[0].get_text_value()
                          for key, values in node.ordered_fields_lookup.items()}
                records.append({'fields': fields, 'path': str(path.relative_to(root)),
                    'line': getattr(node, 'ng_line_start', 1),
                    'parents': [r.ref_uid for r in node.relations if r.ref_type == 'Parent']})
            walk(getattr(node, 'section_contents', []), path)
    for path in sorted((root / 'docs/requirements').rglob('*.sdoc')):
        doc = SDReader.read(path.read_text(), str(path))
        walk(doc.section_contents, path)
    return records


def validate(root, profile):
    errors, index = [], {}
    def error(record, message):
        errors.append({'path': record['path'], 'line': record['line'], 'message': message})
    for record in read_nodes(root):
        fields = record['fields']
        uid = fields.get('UID', '')
        if not uid or uid in index:
            error(record, f'Missing/duplicate UID {uid!r}: assign a unique stable UID.')
            continue
        record['level'] = PREFIX.get(uid.split('-')[0])
        if record['level'] is None:
            path = Path(record['path'])
            record['level'] = next((level for level in PROFILES[profile]
                if level == path.stem or level in path.parts), None)
        if record['level'] not in PROFILES[profile]:
            error(record, f'{uid}: UID level is outside profile {profile}; review the profile or UID.')
        for name in ('TITLE', 'STATEMENT', 'STATUS'):
            if not fields.get(name, '').strip():
                error(record, f'{uid}: fill required field {name}.')
        if fields.get('STATUS') not in STATUS:
            error(record, f'{uid}: STATUS must be Draft, In Review, Approved or Retired.')
        if record['level'] == 'software' and fields.get('CATEGORY') not in CATEGORY:
            error(record, f'{uid}: select one supported CATEGORY.')
        if record['level'] == 'stakeholder' and 'CATEGORY' in fields:
            error(record, f'{uid}: CATEGORY belongs to software requirements only.')
        if fields.get('STATUS') == 'Retired' and not fields.get('COMMENT', '').strip():
            error(record, f'{uid}: explain retirement in COMMENT.')
        index[uid] = record
    for uid, record in index.items():
        for parent in record['parents']:
            if parent not in index:
                error(record, f'{uid}: parent {parent} does not exist; correct the relation.')
        levels = PROFILES[profile]
        level = record['level']
        if record['fields'].get('STATUS') == 'Approved' and level in levels:
            position = levels.index(level)
            if position and not any(index.get(p, {}).get('level') == levels[position-1]
                                    for p in record['parents']):
                error(record, f'{uid}: Approved requirement needs a parent at {levels[position-1]} level.')
            if position < len(levels)-1 and not any(
                uid in child['parents'] and child['level'] == levels[position+1]
                for child in index.values()):
                error(record, f'{uid}: Approved requirement needs a child at {levels[position+1]} level.')
    active, visited = set(), set()
    def visit(uid):
        if uid in active:
            error(index[uid], f'{uid}: cyclic Parent relations; remove the cycle.')
            return
        if uid in visited: return
        active.add(uid)
        for parent in index[uid]['parents']:
            if parent in index: visit(parent)
        active.remove(uid)
        visited.add(uid)
    for uid in index: visit(uid)
    return index, errors


def block_ids(body):
    body = body or ''
    if START not in body and END not in body: return []
    if body.count(START) != 1 or body.count(END) != 1 or body.index(END) < body.index(START):
        raise ValueError('Ambiguous requirements block: keep exactly one matching start/end pair.')
    middle = body.split(START)[1].split(END)[0]
    ids = []
    for line in middle.splitlines():
        if not line.strip(): continue
        match = re.fullmatch(r'- ([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)', line.strip())
        if not match: raise ValueError(f'Invalid UID block entry {line!r}: use "- STK-001" per line.')
        ids.append(match[1])
    return sorted(set(ids))


def with_block(body, ids):
    body = body or ''
    block_ids(body)  # Refuse ambiguous edits, preserve all human-written text.
    block = START + '\n' + ''.join(f'- {uid}\n' for uid in sorted(set(ids))) + END
    if START in body:
        before, tail = body.split(START)
        _, after = tail.split(END)
        return before + block + after
    return body + ('\n\n' if body else '') + block


class GitHub:
    def call(self, endpoint, payload=None):
        args = ['gh', 'api', endpoint]
        if payload is not None: args += ['--method', 'POST' if endpoint == 'graphql' else 'PATCH', '--input', '-']
        for attempt in range(3):
            result = subprocess.run(args, input=json.dumps(payload) if payload is not None else None,
                                    text=True, capture_output=True)
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout.strip() else None
            if attempt < 2 and re.search(r'HTTP (429|5\d\d)|rate limit', result.stderr, re.I):
                time.sleep(2 ** attempt)
                continue
            raise ValueError(f'GitHub request failed ({endpoint}): {result.stderr.strip()}')

    def pages(self, endpoint):
        result, page = [], 1
        while True:
            rows = self.call(f'{endpoint}{"&" if "?" in endpoint else "?"}per_page=100&page={page}')
            result += rows
            if len(rows) < 100: return result
            page += 1

    def linked(self, repo, number):
        owner, name = repo.split('/')
        result, cursor = [], None
        query = '''query($owner:String!,$name:String!,$number:Int!,$cursor:String){
          repository(owner:$owner,name:$name){pullRequest(number:$number){
            closingIssuesReferences(first:100,after:$cursor){
              nodes{number body repository{nameWithOwner}}
              pageInfo{hasNextPage endCursor}}}}}'''
        while True:
            response = self.call('graphql', dict(query=query, variables=dict(
                owner=owner, name=name, number=number, cursor=cursor)))
            if response.get('errors'): raise ValueError(str(response['errors']))
            connection = response['data']['repository']['pullRequest']['closingIssuesReferences']
            result += [i for i in connection['nodes'] if i['repository']['nameWithOwner'] == repo]
            if not connection['pageInfo']['hasNextPage']: return result
            cursor = connection['pageInfo']['endCursor']


def synchronize(root, index, repo, api, apply=False):
    errors, plans, reverse = [], [], {}
    # Include closed issues: closing an issue does not discard traceability.
    for issue in api.pages(f'repos/{repo}/issues?state=all'):
        if 'pull_request' in issue: continue
        ids = block_ids(issue.get('body'))
        for uid in ids:
            if uid not in index: errors.append(f'Issue #{issue["number"]}: unknown UID {uid}; correct the issue or requirements.')
            reverse.setdefault(uid, []).append(issue['number'])
    for pr in api.pages(f'repos/{repo}/pulls?state=open'):
        for uid in block_ids(pr.get('body')):
            if uid not in index: errors.append(f'PR #{pr["number"]}: unknown UID {uid}; correct before synchronization.')
        ids = set()
        for issue in api.linked(repo, pr['number']): ids.update(block_ids(issue.get('body')))
        for uid in ids:
            if uid not in index: errors.append(f'PR #{pr["number"]}: unknown UID {uid}; no automatic removal.')
        body = with_block(pr.get('body'), ids)
        if body != (pr.get('body') or ''): plans.append((pr['number'], body))
    if errors: raise ValueError('\n'.join(errors))
    if apply:
        for number, body in plans:
            # Re-read before mutation so concurrent edits are not silently overwritten.
            ids = set()
            for issue in api.linked(repo, number): ids.update(block_ids(issue.get('body')))
            if ids - index.keys(): raise ValueError('Requirements changed during synchronization; rerun after validation.')
            current = api.call(f'repos/{repo}/pulls/{number}')
            desired = with_block(current.get('body'), ids)
            if desired != (current.get('body') or ''):
                api.call(f'repos/{repo}/pulls/{number}', {'body': desired})
    return {'updated_prs' if apply else 'pending_prs': [n for n, _ in plans], 'issues_by_uid': reverse}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'setup', 'check', 'docs', 'serve', 'sync'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--port', type=int, default=5111)
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY'))
    parser.add_argument('--apply', action='store_true', help='Update PR managed blocks; otherwise dry-run.')
    args = parser.parse_args()
    root = args.root.resolve()
    report = {'status': 'passed', 'errors': []}
    try:
        config = configuration(root)
        if not config['enabled']:
            print('StrictDoc disabled: skipped (no dependency installation or GitHub writes).')
            return 0
        initialize(root, config['profile'])
        if args.command != 'init': runtime(root)
        if args.command in ('check', 'sync', 'docs', 'serve'):
            index, errors = validate(root, config['profile'])
            report.update(requirements=len(index), errors=errors)
            if errors: raise ValueError('Requirements validation failed; see locations below.')
        binary = str(Path(sys.executable).parent / 'strictdoc')
        if args.command in ('check', 'docs'):
            result = subprocess.run([binary, 'export', 'docs/requirements', '--config', 'strictdoc_config.py',
                '--output-dir', 'build/strictdoc', '--no-parallelization'], cwd=root,
                text=True, capture_output=True)
            if result.returncode: raise ValueError(result.stdout + result.stderr)
        elif args.command == 'serve':
            return subprocess.call([binary, 'server', 'docs/requirements', '--config', 'strictdoc_config.py',
                '--output-path', 'build/strictdoc-server', '--host', '127.0.0.1', '--port', str(args.port)], cwd=root)
        elif args.command == 'sync':
            if not args.repo or not re.fullmatch(r'[\w.-]+/[\w.-]+', args.repo):
                raise ValueError('Specify --repo owner/name or GITHUB_REPOSITORY.')
            report.update(synchronize(root, index, args.repo, GitHub(), args.apply))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        report['status'] = 'failed'
        report['errors'].append({'path': 'requirements', 'line': 1, 'message': str(exc)})
    except Exception as exc:
        # StrictDoc parse/semantic errors carry their own file and line information.
        report['status'] = 'failed'
        report['errors'].append({'path': 'StrictDoc', 'line': 1, 'message': str(exc)})
    output = root / 'build/requirements-report.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    for error in report['errors']:
        print(f'{error["path"]}:{error["line"]}: {error["message"]}', file=sys.stderr)
    print(json.dumps(report, ensure_ascii=False))
    return int(report['status'] == 'failed')

if __name__ == '__main__':
    sys.exit(main())
