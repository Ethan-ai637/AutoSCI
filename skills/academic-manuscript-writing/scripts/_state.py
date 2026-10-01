from __future__ import annotations
import hashlib, json
from pathlib import Path
from _common import load_json, load_jsonl, sha256_file

SEMANTIC_FILES = [
    'project.json',
    'section_plan.json',
    'sources.jsonl',
    'evidence.jsonl',
    'claims.jsonl',
    'reporting_contracts.jsonl',
    'paragraph_contracts.jsonl',
    'writing_sources.jsonl',
    'writing_profile.json',
    'manuscript_contract.json',
    'manuscript.md',
]

RECORD_SPECS = {
    'sources': ('sources.jsonl', 'source_id'),
    'evidence': ('evidence.jsonl', 'evidence_id'),
    'claims': ('claims.jsonl', 'claim_id'),
    'reporting_contracts': ('reporting_contracts.jsonl', 'contract_id'),
    'paragraph_contracts': ('paragraph_contracts.jsonl', 'paragraph_id'),
    'writing_sources': ('writing_sources.jsonl', 'writing_source_id'),
}


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def object_hash(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def build_state(root: Path):
    root = Path(root).resolve()
    project = load_json(root/'project.json') if (root/'project.json').exists() else {}
    files = {}
    for name in SEMANTIC_FILES:
        p = root/name
        if p.is_file():
            files[name] = sha256_file(p)

    source_files = {}
    for s in load_jsonl(root/'sources.jsonl') if (root/'sources.jsonl').exists() else []:
        sid = s.get('source_id')
        if not sid:
            continue
        rel = s.get('path')
        item = {'path': rel, 'version': s.get('version'), 'exists': False, 'sha256': None}
        if rel and '://' not in str(rel):
            fp = (root/rel).resolve()
            try:
                fp.relative_to(root)
                inside = True
            except ValueError:
                inside = False
            if inside and fp.is_file():
                item['exists'] = True
                item['sha256'] = sha256_file(fp)
        source_files[str(sid)] = item


    writing_source_files = {}
    wsp = root/'writing_sources.jsonl'
    if wsp.exists():
        for s in load_jsonl(wsp):
            sid = s.get('writing_source_id')
            if not sid:
                continue
            rel = s.get('path')
            item = {'path': rel, 'url': s.get('url'), 'retrieved_at': s.get('retrieved_at'), 'exists': False, 'sha256': None}
            if rel and '://' not in str(rel):
                fp = (root/rel).resolve()
                try:
                    fp.relative_to(root)
                    inside = True
                except ValueError:
                    inside = False
                if inside and fp.is_file():
                    item['exists'] = True
                    item['sha256'] = sha256_file(fp)
            writing_source_files[str(sid)] = item

    records = {}
    record_rows = {}
    for group, (filename, key) in RECORD_SPECS.items():
        p = root/filename
        # Optional semantic ledgers must not invalidate archived state IDs when absent.
        if group in {'paragraph_contracts','writing_sources'} and not p.exists():
            continue
        rows = load_jsonl(p) if p.exists() else []
        by_id = {}
        raw = {}
        for row in rows:
            rid = row.get(key)
            if not rid:
                continue
            by_id[str(rid)] = object_hash(row)
            raw[str(rid)] = row
        records[group] = by_id
        record_rows[group] = raw

    payload = {
        'project_id': project.get('project_id'),
        'skill_version': project.get('skill_version'),
        'mode': project.get('mode'),
        'files': files,
        'source_files': source_files,
        'records': records,
    }
    if wsp.exists():
        payload['writing_source_files'] = writing_source_files
    state_id = object_hash(payload)
    return {
        'schema_version': 1,
        'state_id': state_id,
        **payload,
    }, record_rows


def compare_record_maps(old_map, new_map):
    old_ids = set(old_map or {})
    new_ids = set(new_map or {})
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    changed = sorted(i for i in old_ids & new_ids if old_map.get(i) != new_map.get(i))
    unchanged = sorted(i for i in old_ids & new_ids if old_map.get(i) == new_map.get(i))
    return {'added': added, 'removed': removed, 'changed': changed, 'unchanged': unchanged}
