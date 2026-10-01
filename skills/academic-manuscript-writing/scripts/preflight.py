#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, subprocess, sys
from _common import load_json, load_jsonl, sha256_file

CAUSAL_TERMS=re.compile(r'\b(caused?|causes|causing|led to|leads to|drives?|mediates?|reduced risk|increased risk|effect of)\b', re.I)
OBS_HINTS=re.compile(r'\b(observational|retrospective|cross[- ]sectional|case[- ]control|cohort|correlational|association)\b', re.I)

def norm(s): return re.sub(r'\s+',' ',str(s or '').strip().lower())

def anchor_paragraph(manuscript, anchor):
    if not anchor or anchor not in manuscript: return ''
    for para in re.split(r'\n\s*\n', manuscript):
        if anchor in para: return para
    return ''

def run_audit(script, root, profile):
    proc=subprocess.run([sys.executable,str(Path(__file__).with_name(script)),str(root),'--profile',profile],capture_output=True,text=True)
    try: return json.loads(proc.stdout)
    except Exception:
        return {'ok':False,'errors':[proc.stderr or proc.stdout or f'{script} failed'],'warnings':[]}

def main():
    ap=argparse.ArgumentParser(description='Run deterministic manuscript preflight checks.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'])
    ap.add_argument('--report', default='qa_report.json')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    project=load_json(root/'project.json')
    profile=args.profile or project.get('profile','standard')
    errors=[]; warnings=[]; checks=[]

    base=run_audit('validate_workspace.py',root,profile)
    errors.extend(base.get('errors',[])); warnings.extend(base.get('warnings',[]))
    checks.append({'name':'workspace_validation','ok':base.get('ok',False)})

    sources=load_jsonl(root/'sources.jsonl'); evidence=load_jsonl(root/'evidence.jsonl'); claims=load_jsonl(root/'claims.jsonl')
    active_claims=[c for c in claims if (c.get('lifecycle_state') or 'active')=='active']
    ev={e.get('evidence_id'):e for e in evidence}; sm={s.get('source_id'):s for s in sources}
    study_design=project.get('study_design',''); observational=bool(OBS_HINTS.search(study_design))
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''

    for c in active_claims:
        cid=c.get('claim_id','?'); txt=c.get('text',''); linked=[ev[eid] for eid in (c.get('evidence_ids') or []) if eid in ev]
        if c.get('claim_type') in {'result','method'} and linked and profile in {'standard','release'} and not any(e.get('verification')=='verified' for e in linked):
            msg=f'{cid}: linked evidence has no verified item'
            (errors if profile=='release' else warnings).append(msg)
        evidence_tokens=[]
        for e in linked: evidence_tokens += [str(x) for x in (e.get('value_tokens') or []) if str(x)]
        required_tokens=c.get('required_value_tokens')
        if required_tokens is None:
            required_tokens=evidence_tokens if c.get('claim_type')=='result' else []
        for tok in [str(x) for x in (required_tokens or []) if str(x)]:
            if tok not in txt:
                msg=f'{cid}: required value token not found in active claim text: {tok}'
                (errors if profile=='release' else warnings).append(msg)
        if c.get('strength')=='causal' and observational:
            errors.append(f'{cid}: causal strength conflicts with observational study_design={study_design!r}')
        elif observational and CAUSAL_TERMS.search(txt) and c.get('claim_type') in {'result','interpretation'}:
            warnings.append(f'{cid}: possible causal wording in observational design')
        anchor_context=anchor_paragraph(manuscript, c.get('manuscript_anchor'))
        for ref in c.get('object_refs') or []:
            label=ref.get('label') if isinstance(ref,dict) else None
            if label and norm(label) not in norm(txt) and norm(label) not in norm(anchor_context):
                msg=f'{cid}: declared figure/table reference not found in active claim text or anchored manuscript paragraph: {label}'
                (errors if profile=='release' else warnings).append(msg)
        if c.get('claim_type')=='literature_context' and profile in {'standard','release'}:
            lit_sources={e.get('source_id') for e in linked if e.get('evidence_type')=='literature_context'}
            expected_keys={sm[sid].get('citation_key') for sid in lit_sources if sid in sm and sm[sid].get('citation_key')}
            declared=set(c.get('citation_keys') or [])
            missing_keys=expected_keys-declared
            if missing_keys:
                msg=f'{cid}: literature claim missing citation_keys for linked literature sources: {sorted(missing_keys)}'
                (errors if profile=='release' else warnings).append(msg)

    audits=[
        ('writing_profile','audit_writing_profile.py'),
        ('claim_lifecycle','audit_claim_lifecycle.py'),
        ('claim_family_consistency','audit_claim_families.py'),
        ('source_conflicts','audit_source_conflicts.py'),
        ('claim_atomicity','audit_claim_atomicity.py'),
        ('claim_spans','audit_claim_spans.py'),
        ('manuscript_consistency','audit_manuscript_consistency.py'),
        ('manuscript_coverage','audit_manuscript_coverage.py'),
        ('paragraph_composition','audit_paragraph_composition.py'),
        ('reporting_contracts','audit_reporting_contracts.py'),
        ('revision_obligations','audit_revision_obligations.py'),
        ('revision_locality','audit_revision_locality.py'),
        ('change_provenance','audit_change_provenance.py'),
    ]
    for name,script in audits:
        result=run_audit(script,root,profile)
        errors.extend(result.get('errors',[])); warnings.extend(result.get('warnings',[]))
        checks.append({'name':name,'ok':result.get('ok',False)})

    # If a prior fingerprint snapshot exists, identify stale active direct claims and active claim-family dependents.
    prev_path=root/'fingerprints.previous.json'
    if prev_path.exists():
        try:
            prev=load_json(prev_path).get('sources',{}); current={}
            for s in sources:
                sid=s.get('source_id'); rel=s.get('path'); item={'exists':False,'sha256':None,'version':s.get('version')}
                if rel and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', str(rel)):
                    fp=(root/rel).resolve()
                    try: fp.relative_to(root); inside=True
                    except ValueError: inside=False
                    if inside and fp.is_file(): item={'exists':True,'sha256':sha256_file(fp),'version':s.get('version')}
                current[sid]=item
            changed={sid for sid in set(prev)|set(current) if (prev.get(sid,{}).get('exists'),prev.get(sid,{}).get('sha256'),prev.get(sid,{}).get('version')) != (current.get(sid,{}).get('exists'),current.get(sid,{}).get('sha256'),current.get(sid,{}).get('version'))}
            direct_families=set(); direct_claims=[]
            for c in active_claims:
                linked_sources={ev[eid].get('source_id') for eid in (c.get('evidence_ids') or []) if eid in ev}
                hit=sorted(x for x in linked_sources if x in changed)
                if hit:
                    direct_claims.append(c.get('claim_id'))
                    if c.get('claim_family_id'): direct_families.add(c.get('claim_family_id'))
                    msg=f"{c.get('claim_id')}: linked source changed since fingerprints.previous.json: {', '.join(hit)}"
                    (errors if profile=='release' else warnings).append(msg)
            for c in active_claims:
                if c.get('claim_id') not in direct_claims and c.get('claim_family_id') in direct_families:
                    msg=f"{c.get('claim_id')}: active claim family {c.get('claim_family_id')} depends on a changed source elsewhere in the manuscript"
                    (errors if profile=='release' else warnings).append(msg)
            checks.append({'name':'stale_claim_detection','ok':not changed or profile!='release'})
        except Exception as e: warnings.append(f'could not evaluate fingerprints.previous.json: {e}')

    checks.append({'name':'claim_numeric_scope_reference_checks','ok':not any('causal strength conflicts' in e for e in errors)})

    report={'ok':not errors,'profile':profile,'checks':checks,'errors':errors,'warnings':warnings,
            'summary':{'error_count':len(errors),'warning_count':len(warnings),'active_claim_count':len(active_claims),'total_claim_count':len(claims)}}
    (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
