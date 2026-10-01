#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from datetime import datetime
from _common import load_json, load_jsonl, sha256_file

SPECIFICITY_RANK = {'generic': 0, 'discipline': 1, 'venue': 2}
VALID_AUTHORITY = {'official', 'publisher', 'society', 'secondary', 'user'}
AUTHORITATIVE_LEVELS = {'official', 'publisher', 'society'}
VALID_PROFILE_STATUS = {'unresolved', 'partial', 'resolved', 'not_required'}
VALID_READINESS = {'generic', 'discipline', 'venue'}
VALID_STRENGTH = {'required', 'recommended', 'prohibited', 'informational'}
VALID_VERIFICATION = {'verified', 'needs_review', 'blocked'}
OFFICIAL_BASES = {'official_guideline', 'official_template', 'official_checklist'}
VALID_PRESENCE = {'required', 'optional', 'forbidden'}
VALID_COVERAGE = {'required', 'optional', 'none'}
VALID_MACHINE_TYPES = {'section_presence', 'section_absence', 'section_order', 'max_words'}


def norm(value):
    return re.sub(r'\s+', ' ', str(value or '').strip()).casefold()


def v2_workspace(project):
    raw = str(project.get('skill_version') or '')
    try:
        return int(raw.split('.', 1)[0]) >= 2
    except Exception:
        return bool(project.get('writing_context'))


def add(profile, errors, warnings, message, hard=True):
    if profile == 'release' and hard:
        errors.append(message)
    else:
        warnings.append(message)


def context_subset(obj):
    obj = obj or {}
    return {
        'discipline': obj.get('discipline'),
        'subfield': obj.get('subfield'),
        'article_type': obj.get('article_type'),
        'venue': obj.get('venue'),
        'track': obj.get('track'),
        'venue_year': obj.get('venue_year'),
        'submission_stage': obj.get('submission_stage'),
        'target_specificity': obj.get('target_specificity'),
        'language': obj.get('language'),
    }


def same_context(a, b):
    aa, bb = context_subset(a), context_subset(b)
    for key in aa:
        if key == 'venue_year':
            if aa.get(key) != bb.get(key):
                return False
        elif norm(aa.get(key)) != norm(bb.get(key)):
            return False
    return True


def parse_iso(value):
    if not value:
        return None
    text = str(value).strip()
    try:
        if text.endswith('Z'):
            text = text[:-1] + '+00:00'
        return datetime.fromisoformat(text)
    except Exception:
        return None


def markdown_sections(text):
    """Return heading order and section text for Markdown headings.

    The first level-1 heading is also exposed as Title for generic max_words checks.
    """
    lines = text.splitlines()
    headings=[]
    for i, line in enumerate(lines):
        m=re.match(r'^(#{1,6})\s+(.+?)\s*$', line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2).strip()))
    order=[]; sections={}
    for pos,(line_no,level,title) in enumerate(headings):
        end=len(lines)
        for nxt in headings[pos+1:]:
            if nxt[1] <= level:
                end=nxt[0]; break
        body='\n'.join(lines[line_no+1:end]).strip()
        order.append(title)
        sections.setdefault(norm(title), {'title':title,'body':body,'index':pos})
    if headings and headings[0][1] == 1:
        sections.setdefault('title', {'title':'Title','body':headings[0][2],'index':-1})
    return order, sections


def word_count(text):
    # Strip Markdown/HTML anchors enough for deterministic limits.
    text=re.sub(r'<!--.*?-->', ' ', text, flags=re.S)
    text=re.sub(r'`[^`]*`', ' ', text)
    text=re.sub(r'\[[^\]]+\]\([^\)]+\)', ' ', text)
    return len(re.findall(r"\b[\w][\w'’-]*\b", text, flags=re.UNICODE))


def main():
    ap=argparse.ArgumentParser(description='Audit dynamic discipline/article-type/venue writing profile and manuscript contract.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    errors=[]; warnings=[]
    project=load_json(root/'project.json')

    if not v2_workspace(project):
        report={'ok':True,'profile':args.profile,'v2_workspace':False,'errors':[],'warnings':[],
                'summary':{'target_specificity':'legacy','writing_source_count':0,'constraint_count':0}}
        if args.report:
            (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,ensure_ascii=False)); return

    ctx=project.get('writing_context') or {}
    policy=project.get('writing_profile_policy') or {}
    specificity=ctx.get('target_specificity') or 'generic'
    if specificity not in SPECIFICITY_RANK:
        errors.append(f'writing_context.target_specificity invalid: {specificity!r}')
        specificity='generic'
    if specificity in {'discipline','venue'}:
        if not str(ctx.get('discipline') or '').strip():
            add(args.profile,errors,warnings,'writing_context.discipline is required for discipline/venue-specific writing',True)
        if not str(ctx.get('article_type') or '').strip():
            add(args.profile,errors,warnings,'writing_context.article_type is required for discipline/venue-specific writing',True)
    if specificity=='venue':
        for key in ['venue','venue_year','submission_stage']:
            if ctx.get(key) in {None,''}:
                add(args.profile,errors,warnings,f'writing_context.{key} is required for venue-specific writing',True)

    src_path=root/'writing_sources.jsonl'
    prof_path=root/'writing_profile.json'
    contract_path=root/'manuscript_contract.json'
    writing_sources=load_jsonl(src_path) if src_path.exists() else []
    writing_profile=load_json(prof_path) if prof_path.exists() else {}
    contract=load_json(contract_path) if contract_path.exists() else {}

    scope=project.get('manuscript_scope','full_manuscript')
    if args.profile=='release' and scope in {'full_manuscript','multi_section'} and policy.get('require_contract_for_full_manuscript_release',True):
        if not contract:
            errors.append('v2 full/multi-section release requires manuscript_contract.json')
        elif contract.get('contract_status')!='verified' or not (contract.get('sections') or []):
            errors.append('v2 full/multi-section release requires a verified non-empty manuscript_contract')

    if specificity!='generic':
        for path,label in [(src_path,'writing_sources.jsonl'),(prof_path,'writing_profile.json'),(contract_path,'manuscript_contract.json')]:
            if not path.exists():
                add(args.profile,errors,warnings,f'{label} is required for {specificity}-specific writing',True)

    source_map={}; official_source_ids=set()
    for i,row in enumerate(writing_sources,1):
        sid=row.get('writing_source_id')
        if not sid:
            errors.append(f'writing_sources.jsonl row {i} missing writing_source_id'); continue
        if sid in source_map:
            errors.append(f'duplicate writing_source_id: {sid}'); continue
        source_map[sid]=row
        authority=row.get('authority_level')
        if authority not in VALID_AUTHORITY:
            errors.append(f'{sid}: invalid authority_level={authority!r}')
        if authority in AUTHORITATIVE_LEVELS: official_source_ids.add(sid)
        if not str(row.get('title') or '').strip():
            errors.append(f'{sid}: missing title')
        if not (str(row.get('url') or '').strip() or str(row.get('path') or '').strip()):
            errors.append(f'{sid}: writing source requires url or path')
        if row.get('retrieved_at') and not parse_iso(row.get('retrieved_at')):
            errors.append(f'{sid}: retrieved_at is not ISO-8601 parseable')
        elif specificity!='generic' and not row.get('retrieved_at'):
            add(args.profile,errors,warnings,f'{sid}: retrieved_at required for dynamic writing-profile sources',True)
        rel=row.get('path')
        if rel and '://' not in str(rel):
            fp=(root/str(rel)).resolve()
            try: fp.relative_to(root); inside=True
            except ValueError: inside=False
            if not inside:
                errors.append(f'{sid}: local writing source path escapes workspace: {rel}')
            elif not fp.exists():
                errors.append(f'{sid}: declared local writing source does not exist: {rel}')
            elif row.get('content_sha256') and sha256_file(fp) != row.get('content_sha256'):
                add(args.profile,errors,warnings,f'{sid}: content_sha256 does not match local writing source',True)
        if specificity=='venue' and authority in AUTHORITATIVE_LEVELS:
            if policy.get('require_year_match',True):
                years=row.get('applicable_years') or []
                if ctx.get('venue_year') not in years:
                    add(args.profile,errors,warnings,f'{sid}: official source does not declare venue_year {ctx.get("venue_year")} in applicable_years',True)
            if policy.get('require_stage_match',True):
                stages=[norm(x) for x in (row.get('applicable_stages') or [])]
                if norm(ctx.get('submission_stage')) not in stages:
                    add(args.profile,errors,warnings,f'{sid}: official source does not declare submission_stage {ctx.get("submission_stage")!r}',True)
            if row.get('venue') and norm(row.get('venue')) != norm(ctx.get('venue')):
                add(args.profile,errors,warnings,f'{sid}: writing-source venue {row.get("venue")!r} does not match target venue {ctx.get("venue")!r}',True)
            if policy.get('require_article_type_match',True):
                article_types=[norm(x) for x in (row.get('applicable_article_types') or [])]
                if not article_types:
                    add(args.profile,errors,warnings,f'{sid}: official source must declare applicable_article_types for venue-specific readiness',True)
                elif norm(ctx.get('article_type')) not in article_types:
                    add(args.profile,errors,warnings,f'{sid}: official source does not declare article_type {ctx.get("article_type")!r} in applicable_article_types',True)
            target_track=norm(ctx.get('track'))
            if target_track and policy.get('require_track_match_when_declared',True):
                tracks=[norm(x) for x in (row.get('applicable_tracks') or [])]
                if not tracks:
                    add(args.profile,errors,warnings,f'{sid}: target track {ctx.get("track")!r} is set but official source does not declare applicable_tracks',True)
                elif target_track not in tracks:
                    add(args.profile,errors,warnings,f'{sid}: official source does not declare track {ctx.get("track")!r} in applicable_tracks',True)
            if row.get('discipline') and norm(row.get('discipline')) != norm(ctx.get('discipline')):
                add(args.profile,errors,warnings,f'{sid}: writing-source discipline {row.get("discipline")!r} does not match target discipline {ctx.get("discipline")!r}',True)
            if row.get('subfield') and ctx.get('subfield') and norm(row.get('subfield')) != norm(ctx.get('subfield')):
                warnings.append(f'{sid}: writing-source subfield {row.get("subfield")!r} differs from target subfield {ctx.get("subfield")!r}')

    if specificity=='venue' and policy.get('require_official_sources_for_venue',True) and not official_source_ids:
        add(args.profile,errors,warnings,'venue-specific writing requires at least one authoritative official/publisher/society writing source',True)

    constraints=writing_profile.get('constraints') or []
    constraint_map={}
    if writing_profile:
        if writing_profile.get('status') not in VALID_PROFILE_STATUS:
            errors.append(f'writing_profile.status invalid: {writing_profile.get("status")!r}')
        if not same_context(ctx, writing_profile.get('context') or {}):
            add(args.profile,errors,warnings,'writing_profile.context does not match project writing_context',True)
        retrieval=writing_profile.get('retrieval') or {}
        if specificity!='generic':
            if not retrieval.get('performed'):
                add(args.profile,errors,warnings,'dynamic writing-profile retrieval was not recorded as performed',True)
            if not parse_iso(retrieval.get('retrieved_at')):
                add(args.profile,errors,warnings,'writing_profile.retrieval.retrieved_at must be an ISO-8601 timestamp',True)
        for i,c in enumerate(constraints,1):
            cid=c.get('constraint_id')
            if not cid:
                errors.append(f'writing_profile constraint {i} missing constraint_id'); continue
            if cid in constraint_map:
                errors.append(f'duplicate writing-profile constraint_id: {cid}'); continue
            constraint_map[cid]=c
            if not str(c.get('requirement') or '').strip(): errors.append(f'{cid}: missing requirement')
            if c.get('strength') not in VALID_STRENGTH: errors.append(f'{cid}: invalid strength={c.get("strength")!r}')
            if c.get('verification') not in VALID_VERIFICATION: errors.append(f'{cid}: invalid verification={c.get("verification")!r}')
            source_ids=c.get('source_ids') or []
            for sid in source_ids:
                if sid not in source_map: errors.append(f'{cid}: unknown writing_source_id {sid}')
            basis=c.get('basis')
            if basis in OFFICIAL_BASES:
                if not source_ids:
                    errors.append(f'{cid}: {basis} constraint requires source_ids')
                elif any(source_map.get(sid,{}).get('authority_level') not in AUTHORITATIVE_LEVELS for sid in source_ids):
                    errors.append(f'{cid}: {basis} constraint must cite only authoritative official/publisher/society sources')
            if basis!='user_instruction' and policy.get('require_constraint_provenance',True) and not source_ids:
                add(args.profile,errors,warnings,f'{cid}: constraint has no source provenance',True)
            if args.profile=='release' and specificity!='generic' and c.get('verification')!='verified':
                errors.append(f'{cid}: release writing constraint is not verified')
            applies=[norm(x) for x in (c.get('applies_to_stages') or [])]
            if specificity=='venue' and applies and norm(ctx.get('submission_stage')) not in applies:
                warnings.append(f'{cid}: constraint does not list current submission_stage={ctx.get("submission_stage")!r}')

        for conflict in writing_profile.get('guideline_conflicts') or []:
            gid=conflict.get('conflict_id','?')
            if conflict.get('disposition')=='blocking' and args.profile=='release' and specificity!='generic':
                errors.append(f'{gid}: blocking writing-guideline conflict remains unresolved')
            for sid in conflict.get('source_ids') or []:
                if sid not in source_map: errors.append(f'{gid}: unknown writing_source_id {sid}')

        readiness=writing_profile.get('readiness') or {}
        level=readiness.get('level') or 'generic'
        if level not in VALID_READINESS:
            errors.append(f'writing_profile.readiness.level invalid: {level!r}')
            level='generic'
        if SPECIFICITY_RANK.get(level,0) < SPECIFICITY_RANK.get(specificity,0):
            add(args.profile,errors,warnings,f'writing profile readiness={level} does not meet target_specificity={specificity}',True)
        if specificity in {'discipline','venue'} and args.profile=='release' and writing_profile.get('status')!='resolved':
            errors.append(f'{specificity}-specific release requires writing_profile.status=resolved')
        if specificity=='venue' and args.profile=='release' and not readiness.get('venue_ready'):
            errors.append('venue-specific release requires writing_profile.readiness.venue_ready=true')

    # Manuscript contract is the operational synthesis of retrieved writing constraints.
    if contract:
        if not same_context(ctx, contract.get('context') or {}):
            add(args.profile,errors,warnings,'manuscript_contract.context does not match project writing_context',True)
        expected_hash=sha256_file(prof_path) if prof_path.exists() else None
        recorded=contract.get('writing_profile_sha256')
        if policy.get('contract_must_match_profile_hash',True) and specificity!='generic':
            if not expected_hash or recorded != expected_hash:
                add(args.profile,errors,warnings,'manuscript_contract is stale: writing_profile_sha256 does not match writing_profile.json',True)
        if args.profile=='release' and specificity!='generic':
            if contract.get('contract_status')!='verified': errors.append('release requires manuscript_contract.contract_status=verified')
            if contract.get('unresolved_items'): errors.append('release manuscript_contract has unresolved_items')

        def check_constraint_refs(owner, ids):
            for cid in ids or []:
                if cid not in constraint_map:
                    errors.append(f'{owner}: unknown writing constraint_id {cid}')
        for i,sec in enumerate(contract.get('sections') or [],1):
            name=sec.get('name')
            if not name: errors.append(f'manuscript_contract section {i} missing name')
            if sec.get('presence') not in VALID_PRESENCE: errors.append(f'manuscript_contract section {name or i}: invalid presence')
            if sec.get('claim_coverage') not in VALID_COVERAGE: errors.append(f'manuscript_contract section {name or i}: invalid claim_coverage')
            roles=sec.get('scientific_roles') or []
            valid_roles={'title','abstract','introduction','methods','results','discussion','conclusion','mixed','other'}
            if not roles or any(r not in valid_roles for r in roles):
                errors.append(f'manuscript_contract section {name or i}: invalid or missing scientific_roles')
            check_constraint_refs(f'manuscript_contract section {name or i}', sec.get('constraint_ids'))
        for group in ['rules','manual_checks','machine_checks']:
            for i,row in enumerate(contract.get(group) or [],1):
                check_constraint_refs(f'{group} row {i}', row.get('constraint_ids'))
        for i,row in enumerate(contract.get('manual_checks') or [],1):
            status=row.get('status') or 'pending'
            label=row.get('check_id') or f'manual_check_{i}'
            if status not in {'pending','verified','not_applicable','blocked'}:
                errors.append(f'{label}: invalid manual-check status={status!r}')
            if status=='not_applicable' and not str(row.get('verification_notes') or '').strip():
                errors.append(f'{label}: not_applicable manual check requires verification_notes')
            if args.profile=='release' and specificity!='generic' and status not in {'verified','not_applicable'}:
                errors.append(f'{label}: venue-specific release manual check status={status!r}')
        for i,row in enumerate(contract.get('machine_checks') or [],1):
            if row.get('type') not in VALID_MACHINE_TYPES:
                errors.append(f'machine_checks row {i}: unsupported type={row.get("type")!r}')

        manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
        order, sections=markdown_sections(manuscript)
        order_norm=[norm(x) for x in order]
        contract_sections=contract.get('sections') or []
        for sec in contract_sections:
            name=sec.get('name'); key=norm(name)
            if not name: continue
            if sec.get('presence')=='required' and key not in sections:
                add(args.profile,errors,warnings,f'manuscript missing required contract section: {name}',True)
            if sec.get('presence')=='forbidden' and key in sections:
                add(args.profile,errors,warnings,f'manuscript contains forbidden contract section: {name}',True)
        if contract.get('enforce_section_order'):
            expected=[norm(s.get('name')) for s in contract_sections if s.get('presence')!='forbidden' and norm(s.get('name')) in order_norm]
            actual=[x for x in order_norm if x in set(expected)]
            if actual != expected:
                add(args.profile,errors,warnings,f'manuscript section order does not match manuscript_contract: expected={expected}, actual={actual}',True)

        plan=load_json(root/'section_plan.json') if (root/'section_plan.json').exists() else {}
        planned={norm(x) for x in (plan.get('sections') or {}).keys()}
        coverage_required={norm(x) for x in ((project.get('coverage_policy') or {}).get('required_sections') or [])}
        for sec in contract_sections:
            if sec.get('claim_coverage')=='required':
                if norm(sec.get('name')) not in planned:
                    add(args.profile,errors,warnings,f'section_plan does not include claim-covered contract section: {sec.get("name")}',True)
                if norm(sec.get('name')) not in coverage_required:
                    add(args.profile,errors,warnings,f'coverage_policy.required_sections does not include claim-covered contract section: {sec.get("name")}',True)

        for i,check in enumerate(contract.get('machine_checks') or [],1):
            ctype=check.get('type'); label=check.get('check_id') or f'machine_check_{i}'
            if ctype=='section_presence':
                name=check.get('section')
                if norm(name) not in sections: add(args.profile,errors,warnings,f'{label}: required section absent: {name}',True)
            elif ctype=='section_absence':
                name=check.get('section')
                if norm(name) in sections: add(args.profile,errors,warnings,f'{label}: prohibited section present: {name}',True)
            elif ctype=='section_order':
                names=[norm(x) for x in (check.get('sections') or [])]
                positions=[order_norm.index(x) for x in names if x in order_norm]
                if len(positions)!=len(names) or positions != sorted(positions):
                    add(args.profile,errors,warnings,f'{label}: section_order check failed',True)
            elif ctype=='max_words':
                name=check.get('section'); limit=check.get('max_words')
                if not isinstance(limit,int) or limit < 1:
                    errors.append(f'{label}: max_words must be a positive integer')
                elif norm(name) not in sections:
                    add(args.profile,errors,warnings,f'{label}: max_words target section absent: {name}',True)
                else:
                    count=word_count(sections[norm(name)]['body'])
                    if count > limit: add(args.profile,errors,warnings,f'{label}: {name} has {count} words > max_words={limit}',True)

    report={
        'ok':not errors,'profile':args.profile,'v2_workspace':True,'errors':errors,'warnings':warnings,
        'summary':{
            'target_specificity':specificity,
            'writing_source_count':len(writing_sources),
            'constraint_count':len(constraints),
            'contract_section_count':len(contract.get('sections') or []) if contract else 0,
            'venue_ready':bool((writing_profile.get('readiness') or {}).get('venue_ready')) if writing_profile else False,
        }
    }
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
