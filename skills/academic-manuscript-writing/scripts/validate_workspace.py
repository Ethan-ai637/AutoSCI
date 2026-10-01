#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from _common import load_json, load_jsonl

REQUIRED_PROJECT={'project_id','skill_version','profile','mode','study_design','research_question'}
VALID_PROFILES={'draft','standard','release'}
VALID_MODES={'build','revise','refresh','audit'}
VALID_SCOPE={'full_manuscript','multi_section','single_section'}
VALID_VERIFY={'verified','partial','unverified'}
VALID_STATUS={'draft','verified','needs_revision','blocked'}
VALID_LIFECYCLE={'active','superseded','retired'}
VALID_MANUSCRIPT_PRESENCE={'required','optional','not_in_manuscript'}
VALID_COMPANION_SCOPES={'same_paragraph','same_section','manuscript'}
VALID_PARAGRAPH_COMPOSITIONS={'additive','comparison','contrast','qualified','result_interpretation','synthesis','method_context'}
OBJECT_SOURCE_TYPES={'figure','figure_caption','result_table','table','supplement'}
VALID_ANCHOR_PRECISION={'paragraph','span'}


def main():
    ap=argparse.ArgumentParser(description='Validate academic-manuscript-writing workspace records.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=sorted(VALID_PROFILES))
    ap.add_argument('--json', dest='json_out')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    errors=[]; warnings=[]
    for n in ['project.json','sources.jsonl','evidence.jsonl','claims.jsonl']:
        if not (root/n).exists(): errors.append(f'missing required file: {n}')
    if errors:
        report={'ok':False,'errors':errors,'warnings':warnings}
        print(json.dumps(report,indent=2)); sys.exit(1)
    try: project=load_json(root/'project.json')
    except Exception as e: errors.append(f'project.json: {e}'); project={}
    missing=REQUIRED_PROJECT-set(project)
    if missing: errors.append('project.json missing fields: '+', '.join(sorted(missing)))
    profile=args.profile or project.get('profile','standard')
    if profile not in VALID_PROFILES: errors.append(f'invalid profile: {profile}')
    if project.get('mode') not in VALID_MODES: errors.append(f'invalid mode: {project.get("mode")}')
    scope=project.get('manuscript_scope','full_manuscript')
    if scope not in VALID_SCOPE: errors.append(f'invalid manuscript_scope: {scope}')
    coverage_policy=project.get('coverage_policy')
    if coverage_policy is not None:
        if not isinstance(coverage_policy,dict):
            errors.append('coverage_policy must be an object')
        else:
            rs=coverage_policy.get('required_sections')
            if rs is not None and (not isinstance(rs,list) or not all(isinstance(x,str) and x.strip() for x in rs)):
                errors.append('coverage_policy.required_sections must be a list of non-empty strings')
            ae=coverage_policy.get('allow_exemptions')
            if ae is not None and not isinstance(ae,bool):
                errors.append('coverage_policy.allow_exemptions must be boolean')
    span_policy=project.get('claim_span_policy')
    if span_policy is not None:
        if not isinstance(span_policy,dict):
            errors.append('claim_span_policy must be an object')
        else:
            rs=span_policy.get('required_sections')
            if rs is not None and (not isinstance(rs,list) or not all(isinstance(x,str) and x.strip() for x in rs)):
                errors.append('claim_span_policy.required_sections must be a list of non-empty strings')
            rt=span_policy.get('required_claim_types')
            if rt is not None and (not isinstance(rt,list) or not all(isinstance(x,str) and x.strip() for x in rt)):
                errors.append('claim_span_policy.required_claim_types must be a list of non-empty strings')
            for key in ['allow_exemptions','require_exact_claim_text','enforce_reverse_references']:
                if key in span_policy and not isinstance(span_policy[key],bool):
                    errors.append(f'claim_span_policy.{key} must be boolean')
            mx=span_policy.get('max_uncovered_words_per_paragraph')
            if mx is not None and (not isinstance(mx,int) or isinstance(mx,bool) or mx < 0):
                errors.append('claim_span_policy.max_uncovered_words_per_paragraph must be integer >= 0')
    atomicity_policy=project.get('claim_atomicity_policy')
    if atomicity_policy is not None:
        if not isinstance(atomicity_policy,dict): errors.append('claim_atomicity_policy must be an object')
        else:
            ect=atomicity_policy.get('enforce_claim_types')
            if ect is not None and (not isinstance(ect,list) or not all(isinstance(x,str) and x for x in ect)):
                errors.append('claim_atomicity_policy.enforce_claim_types must be a list of strings')
            mx=atomicity_policy.get('max_top_level_scientific_clauses')
            if mx is not None and (not isinstance(mx,int) or mx < 1): errors.append('claim_atomicity_policy.max_top_level_scientific_clauses must be integer >= 1')
            ae=atomicity_policy.get('allow_exemptions')
            if ae is not None and not isinstance(ae,bool): errors.append('claim_atomicity_policy.allow_exemptions must be boolean')
    revision_policy=project.get('revision_policy')
    if revision_policy is not None and not isinstance(revision_policy,dict):
        errors.append('revision_policy must be an object')
    elif isinstance(revision_policy,dict):
        for key in ['preserve_existing_manuscript','allow_global_rewrite','allow_title_change']:
            if key in revision_policy and not isinstance(revision_policy[key],bool):
                errors.append(f'revision_policy.{key} must be boolean')
        for key in ['min_prose_token_similarity','min_preserved_old_paragraph_fraction']:
            if key in revision_policy:
                val=revision_policy[key]
                if not isinstance(val,(int,float)) or isinstance(val,bool) or not 0 <= val <= 1:
                    errors.append(f'revision_policy.{key} must be a number between 0 and 1')
        terms=revision_policy.get('forbidden_meta_manuscript_terms')
        if terms is not None and (not isinstance(terms,list) or not all(isinstance(x,str) and x.strip() for x in terms)):
            errors.append('revision_policy.forbidden_meta_manuscript_terms must be a list of non-empty strings')
    try:
        version_major_minor=tuple(int(x) for x in str(project.get('skill_version','0.0')).split('.')[:2])
    except Exception:
        version_major_minor=(0,0)
    if version_major_minor >= (1,7) and project.get('mode') in {'revise','refresh'} and not isinstance(revision_policy,dict):
        msg='v1.7 revise/refresh workspace requires revision_policy'
        (errors if profile=='release' else warnings).append(msg)
    if version_major_minor >= (1,8) and not isinstance(span_policy,dict):
        msg='v1.8 workspace requires claim_span_policy'
        (errors if profile=='release' else warnings).append(msg)
    try: sources=load_jsonl(root/'sources.jsonl')
    except Exception as e: errors.append(str(e)); sources=[]
    try: evidence=load_jsonl(root/'evidence.jsonl')
    except Exception as e: errors.append(str(e)); evidence=[]
    try: claims=load_jsonl(root/'claims.jsonl')
    except Exception as e: errors.append(str(e)); claims=[]

    def index(rows,key,label):
        d={}
        for i,r in enumerate(rows,1):
            v=r.get(key)
            if not v: errors.append(f'{label} row {i} missing {key}'); continue
            if v in d: errors.append(f'duplicate {key}: {v}')
            d[v]=r
        return d
    sm=index(sources,'source_id','sources.jsonl')
    em=index(evidence,'evidence_id','evidence.jsonl')
    cm=index(claims,'claim_id','claims.jsonl')
    conflict_ids=set()
    raw_conflicts=project.get('unresolved_conflicts') or []
    if not isinstance(raw_conflicts,list):
        errors.append('project.unresolved_conflicts must be a list')
        raw_conflicts=[]
    for i,row in enumerate(raw_conflicts,1):
        if isinstance(row,dict):
            cid=row.get('conflict_id')
            if not cid: errors.append(f'unresolved_conflicts item {i} missing conflict_id')
            elif cid in conflict_ids: errors.append(f'duplicate conflict_id: {cid}')
            else: conflict_ids.add(cid)
        elif not isinstance(row,str):
            errors.append(f'unresolved_conflicts item {i} must be a string or object')

    citation_to_source={}
    for s in sources:
        ck=s.get('citation_key')
        if ck:
            if ck in citation_to_source: errors.append(f'duplicate citation_key: {ck}')
            citation_to_source[ck]=s.get('source_id')
        rel=s.get('path')
        if rel and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', str(rel)):
            fp=(root/rel).resolve()
            try: fp.relative_to(root); inside=True
            except ValueError: inside=False
            if not inside: warnings.append(f"{s.get('source_id')}: local source path escapes workspace: {rel}")
            elif not fp.exists(): warnings.append(f"{s.get('source_id')}: declared local source does not exist: {rel}")

    for e in evidence:
        sid=e.get('source_id')
        if sid not in sm: errors.append(f'{e.get("evidence_id")}: unknown source_id {sid}')
        if e.get('verification') not in VALID_VERIFY:
            warnings.append(f'{e.get("evidence_id")}: unusual verification={e.get("verification")}')

    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    family_ids={c.get('claim_family_id') for c in claims if c.get('claim_family_id') and (c.get('lifecycle_state') or 'active')=='active'}
    for c in claims:
        cid=c.get('claim_id'); status=c.get('status'); ctype=c.get('claim_type'); evids=c.get('evidence_ids') or []
        state=c.get('lifecycle_state') or 'active'
        if status not in VALID_STATUS: warnings.append(f'{cid}: unusual status={status}')
        if state not in VALID_LIFECYCLE: errors.append(f'{cid}: invalid lifecycle_state={state}')
        presence=c.get('manuscript_presence')
        if presence is not None and presence not in VALID_MANUSCRIPT_PRESENCE:
            errors.append(f'{cid}: invalid manuscript_presence={presence!r}')
        if presence=='not_in_manuscript' and not str(c.get('manuscript_presence_reason') or '').strip():
            msg=f'{cid}: manuscript_presence=not_in_manuscript requires manuscript_presence_reason'
            (errors if profile=='release' else warnings).append(msg)
        if ctype in {'result','method'} and state=='active' and profile in {'standard','release'} and not evids:
            errors.append(f'{cid}: active {ctype} claim has no evidence_ids')
        for eid in evids:
            if eid not in em: errors.append(f'{cid}: unknown evidence_id {eid}')
        for ck in c.get('citation_keys') or []:
            if ck not in citation_to_source: errors.append(f'{cid}: unknown citation_key {ck}')
        for ref in c.get('object_refs') or []:
            if not isinstance(ref,dict): errors.append(f'{cid}: object_refs entries must be objects'); continue
            sid=ref.get('source_id'); label=ref.get('label')
            if sid not in sm: errors.append(f'{cid}: object_ref unknown source_id {sid}')
            elif sm[sid].get('source_type') not in OBJECT_SOURCE_TYPES:
                warnings.append(f'{cid}: object_ref source {sid} has source_type={sm[sid].get("source_type")!r}')
            if not label: errors.append(f'{cid}: object_ref missing label')
        for conflict_id in c.get('source_conflict_ids') or []:
            if conflict_id not in conflict_ids:
                errors.append(f'{cid}: unknown source_conflict_id {conflict_id}')
        exemption=c.get('atomicity_exemption_reason')
        if exemption is not None and not isinstance(exemption,str):
            errors.append(f'{cid}: atomicity_exemption_reason must be a string')
        precision=c.get('anchor_precision')
        if precision is not None and precision not in VALID_ANCHOR_PRECISION:
            errors.append(f'{cid}: invalid anchor_precision={precision!r}')
        span_exemption=c.get('span_exemption_reason')
        if span_exemption is not None and not isinstance(span_exemption,str):
            errors.append(f'{cid}: span_exemption_reason must be a string')
        if precision=='span' and c.get('manuscript_anchor') and not str(c.get('manuscript_anchor')).startswith('CLAIM:'):
            errors.append(f'{cid}: anchor_precision=span requires manuscript_anchor in CLAIM:<id> form')
        companion_keys=set()
        for j,comp in enumerate(c.get('required_companions') or [],1):
            if not isinstance(comp,dict):
                errors.append(f'{cid}: required_companions entry {j} must be an object'); continue
            target=comp.get('claim_id'); cscope=comp.get('scope','same_paragraph')
            if target not in cm: errors.append(f'{cid}: required companion unknown claim_id {target}')
            if target==cid: errors.append(f'{cid}: claim cannot require itself as a companion')
            if cscope not in VALID_COMPANION_SCOPES: errors.append(f'{cid}: invalid required companion scope={cscope!r}')
            key=(target,cscope)
            if key in companion_keys: errors.append(f'{cid}: duplicate required companion {target} with scope={cscope}')
            companion_keys.add(key)
        for old_id in c.get('supersedes_claim_ids') or []:
            if old_id not in cm: errors.append(f'{cid}: supersedes unknown claim_id {old_id}')
        for new_id in c.get('superseded_by_claim_ids') or []:
            if new_id not in cm: errors.append(f'{cid}: superseded_by unknown claim_id {new_id}')
        if profile=='release' and state=='active' and status in {'draft','needs_revision','blocked'}:
            errors.append(f'{cid}: release profile disallows active status={status}')

    # Optional section plan becomes a structural contract for full-manuscript standard/release work.
    plan_path=root/'section_plan.json'
    if plan_path.exists():
        try: plan=load_json(plan_path)
        except Exception as e: errors.append(f'section_plan.json: {e}'); plan={}
        for fid in plan.get('main_claim_families') or []:
            if fid not in family_ids: warnings.append(f'section_plan: unknown/uninstantiated active claim_family_id {fid}')
        by_section={}
        for c in claims:
            if (c.get('lifecycle_state') or 'active')!='active': continue
            by_section.setdefault(c.get('section'),set()).add(c.get('claim_family_id'))
        for sec,cfg in (plan.get('sections') or {}).items():
            for fid in (cfg or {}).get('must_cover') or []:
                if fid not in by_section.get(sec,set()):
                    msg=f'section_plan: {sec} must cover {fid}, but no matching active claim exists'
                    (errors if profile=='release' else warnings).append(msg)
    elif scope=='full_manuscript' and profile in {'standard','release'}:
        (errors if profile=='release' else warnings).append('full_manuscript workspace has no section_plan.json')

    # Optional paragraph composition contracts become mandatory only when multi-claim paragraphs exist at release.
    pc_path=root/'paragraph_contracts.jsonl'
    if pc_path.exists():
        try: pcs=load_jsonl(pc_path)
        except Exception as e: errors.append(str(e)); pcs=[]
        seen=set()
        for i,row in enumerate(pcs,1):
            pid=row.get('paragraph_id')
            if not pid: errors.append(f'paragraph_contracts.jsonl row {i} missing paragraph_id'); continue
            if pid in seen: errors.append(f'duplicate paragraph_id: {pid}')
            seen.add(pid)
            if row.get('composition') not in VALID_PARAGRAPH_COMPOSITIONS:
                errors.append(f'{pid}: invalid paragraph composition={row.get("composition")!r}')
            claim_ids=row.get('claim_ids') or []
            for pcid in claim_ids:
                if pcid not in cm: errors.append(f'{pid}: unknown claim_id {pcid}')
            primary=row.get('primary_claim_id')
            if primary and primary not in claim_ids: errors.append(f'{pid}: primary_claim_id must be in claim_ids')
            qualifiers=row.get('qualifier_claim_ids') or []
            if any(q not in claim_ids for q in qualifiers): errors.append(f'{pid}: qualifier_claim_ids must be a subset of claim_ids')
            if row.get('composition')=='qualified' and not qualifiers: errors.append(f'{pid}: qualified composition requires qualifier_claim_ids')

    # Legacy reviewer response map remains accepted for backwards compatibility.
    rr_path=root/'reviewer_response_map.jsonl'
    if rr_path.exists():
        try: rr=load_jsonl(rr_path)
        except Exception as e: errors.append(str(e)); rr=[]
        try: revisions=load_jsonl(root/'revision_log.jsonl') if (root/'revision_log.jsonl').exists() else []
        except Exception as e: errors.append(str(e)); revisions=[]
        change_ids={r.get('change_id') for r in revisions if r.get('change_id')}
        claim_ids=set(cm)
        for row in rr:
            rid=row.get('comment_id','?')
            for ch in row.get('change_ids') or []:
                if ch not in change_ids: errors.append(f'{rid}: unknown revision change_id {ch}')
            for cid in row.get('affected_claim_ids') or []:
                if cid not in claim_ids: errors.append(f'{rid}: unknown affected claim_id {cid}')
            if profile=='release' and row.get('response_status') not in {'resolved','not_applicable'}:
                errors.append(f'{rid}: release reviewer response is not resolved')

    # Source-conflict release disposition is audited by audit_source_conflicts.py.
    if profile=='release':
        if re.search(r'\[(?:VERIFY|CITATION|METHOD|TODO|TBD)[^\]]*\]', manuscript, re.I):
            errors.append('release manuscript contains unresolved placeholder marker')
    report={'ok':not errors,'profile':profile,'counts':{'sources':len(sources),'evidence':len(evidence),'claims':len(claims)},'errors':errors,'warnings':warnings}
    if args.json_out: (root/args.json_out).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
