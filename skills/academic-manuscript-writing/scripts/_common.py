from __future__ import annotations
import hashlib, json, os, re
from pathlib import Path

TEXT_EXTS = {'.md','.txt','.csv','.tsv','.json','.jsonl','.yaml','.yml','.tex','.py','.r','.R'}

def load_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def load_jsonl(path: Path):
    rows=[]
    if not path.exists():
        return rows
    with path.open('r', encoding='utf-8') as f:
        for i,line in enumerate(f,1):
            s=line.strip()
            if not s:
                continue
            try:
                obj=json.loads(s)
            except Exception as e:
                raise ValueError(f'{path}:{i}: invalid JSON: {e}')
            if not isinstance(obj, dict):
                raise ValueError(f'{path}:{i}: expected JSON object')
            rows.append(obj)
    return rows

def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def rel_files(root: Path):
    skip={'.git','__pycache__'}
    for p in sorted(root.rglob('*')):
        if p.is_file() and not any(part in skip for part in p.parts):
            yield p.relative_to(root)

def extract_numeric_tokens(text: str):
    # scientific-number tokens including decimals, percentages, exponents, and p-like values
    return re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?%?', text or '')

DEFAULT_SECTION_ROLES = {
    'title': {'title'},
    'abstract': {'abstract'},
    'introduction': {'introduction'},
    'background': {'introduction'},
    'methods': {'methods'},
    'method': {'methods'},
    'materials and methods': {'methods'},
    'materials methods': {'methods'},
    'results': {'results'},
    'discussion': {'discussion'},
    'conclusion': {'conclusion'},
    'conclusions': {'conclusion'},
}


def _norm_section_name(value):
    return re.sub(r'\s+', ' ', str(value or '').strip()).casefold()


def load_section_role_map(root: Path):
    """Map actual manuscript section names to scientific roles.

    v2 manuscript contracts may rename/combine sections (for example, Experiments
    or Results and Discussion). Historical workspaces fall back to conventional
    heading aliases.
    """
    mapping = {k: set(v) for k, v in DEFAULT_SECTION_ROLES.items()}
    path = Path(root) / 'manuscript_contract.json'
    if path.exists():
        try:
            contract = load_json(path)
            for sec in contract.get('sections') or []:
                name = _norm_section_name(sec.get('name'))
                roles = {str(x).strip().casefold() for x in (sec.get('scientific_roles') or []) if str(x).strip()}
                if name and roles:
                    mapping[name] = roles
        except Exception:
            pass
    return mapping


def section_roles(root: Path, section):
    name = _norm_section_name(section)
    mapping = load_section_role_map(root)
    return mapping.get(name, set())
