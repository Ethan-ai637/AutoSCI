#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from _common import load_json, load_jsonl

VALID_STATUS={'unresolved','resolved'}
VALID_DISPOSITIONS={'blocking','disclose_and_scope','historical_only','resolved'}


def severity(profile, errors, warnings, msg):
    (errors if profile=='release' else warnings).append(msg)


def anchor_present(manuscript, anchor):
    return bool(anchor and anchor in manuscript)


def literal_token_present(text, token):
    return str(token).strip().lower() in str(text or '').lower()


NUMERIC_RE = re.compile(r'(?<![A-Za-z0-9_])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][-+]?\d+)?%?(?![A-Za-z0-9_])')

def normalize_numeric_token(token):
    t=str(token or '').strip().lower().replace(',', '')
    if t.startswith('+'):
        t=t[1:]
    return t

def numeric_tokens(text):
    return {normalize_numeric_token(m.group(0)) for m in NUMERIC_RE.finditer(str(text or ''))}

def paragraph_for_anchor(manuscript, anchor):
    if not anchor:
        return ''
    for para in re.split(r'\n\s*\n', manuscript):
        if anchor in para:
            return para
    return ''

def claim_conflict_sides(claim, sides, evidence_map):
    """Return conflict-side IDs represented by a claim through evidence/source linkage or literal side values."""
    represented=set()
    evids=set(claim.get('evidence_ids') or [])
    text=str(claim.get('text') or '')
    linked_sources={evidence_map[eid].get('source_id') for eid in evids if eid in evidence_map}
    for side in sides:
        sid=side.get('side_id')
        if not sid:
            continue
        side_evidence=set(side.get('evidence_ids') or [])
        side_sources=set(side.get('source_ids') or [])
        side_values=[str(x) for x in (side.get('value_tokens') or []) if str(x).strip()]
        if evids & side_evidence or linked_sources & side_sources:
            represented.add(sid)
            continue
        if side_values and any(literal_token_present(text,tok) for tok in side_values):
            represented.add(sid)
    return represented


def main():
    ap=argparse.ArgumentParser(description='Audit source-conflict disposition, disclosure, claim scoping, and conflict-side provenance.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    errors=[]; warnings=[]; details=[]

    project=load_json(root/'project.json')
    sources=load_jsonl(root/'sources.jsonl') if (root/'sources.jsonl').exists() else []
    evidence=load_jsonl(root/'evidence.jsonl') if (root/'evidence.jsonl').exists() else []
    claims=load_jsonl(root/'claims.jsonl') if (root/'claims.jsonl').exists() else []
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    sm={s.get('source_id'):s for s in sources if s.get('source_id')}
    em={e.get('evidence_id'):e for e in evidence if e.get('evidence_id')}
    cm={c.get('claim_id'):c for c in claims if c.get('claim_id')}
    active={cid:c for cid,c in cm.items() if (c.get('lifecycle_state') or 'active')=='active'}

    rows=project.get('unresolved_conflicts') or []
    if not isinstance(rows,list):
        errors.append('project.unresolved_conflicts must be a list')
        rows=[]

    seen=set(); normalized=[]
    for i,row in enumerate(rows,1):
        # v1.6 and earlier used free-form strings. Keep them legal but conservative.
        if isinstance(row,str):
            cid=f'LEGACY-{i}'
            normalized.append({'conflict_id':cid,'status':'unresolved','release_disposition':'blocking','summary':row,'legacy':True})
            continue
        if not isinstance(row,dict):
            errors.append(f'unresolved_conflicts item {i} must be a string or object')
            continue
        cid=row.get('conflict_id')
        if not cid:
            errors.append(f'unresolved_conflicts item {i} missing conflict_id')
            continue
        if cid in seen:
            errors.append(f'duplicate conflict_id: {cid}')
        seen.add(cid)
        normalized.append(dict(row))

    for row in normalized:
        cid=row.get('conflict_id','?')
        status=row.get('status','unresolved')
        disposition=row.get('release_disposition','blocking' if status!='resolved' else 'resolved')
        if status not in VALID_STATUS:
            errors.append(f'{cid}: invalid conflict status={status!r}')
        if disposition not in VALID_DISPOSITIONS:
            errors.append(f'{cid}: invalid release_disposition={disposition!r}')

        for sid in row.get('affected_source_ids') or []:
            if sid not in sm: errors.append(f'{cid}: unknown affected_source_id {sid}')
        for eid in row.get('affected_evidence_ids') or []:
            if eid not in em: errors.append(f'{cid}: unknown affected_evidence_id {eid}')
        affected=row.get('affected_claim_ids') or []
        scoped=row.get('scoped_claim_ids') or affected
        disclosure=row.get('disclosure_claim_ids') or []
        cross_side=row.get('cross_side_claim_ids') or []
        for key,ids in [('affected_claim_ids',affected),('scoped_claim_ids',scoped),('disclosure_claim_ids',disclosure),('cross_side_claim_ids',cross_side),('blocks_claim_ids',row.get('blocks_claim_ids') or [])]:
            for claim_id in ids:
                if claim_id not in cm: errors.append(f'{cid}: unknown {key[:-1]} {claim_id}')

        # v1.7.1 optional conflict-side provenance. If present, it becomes a release contract.
        sides=row.get('conflict_sides') or []
        if sides and not isinstance(sides,list):
            errors.append(f'{cid}: conflict_sides must be a list')
            sides=[]
        side_ids=set(); normalized_sides=[]
        for j,side in enumerate(sides,1):
            if not isinstance(side,dict):
                errors.append(f'{cid}: conflict_sides item {j} must be an object'); continue
            side_id=side.get('side_id')
            if not side_id:
                errors.append(f'{cid}: conflict_sides item {j} missing side_id'); continue
            if side_id in side_ids:
                errors.append(f'{cid}: duplicate conflict side_id {side_id}')
            side_ids.add(side_id)
            srcs=side.get('source_ids') or []
            evids=side.get('evidence_ids') or []
            vals=side.get('value_tokens') or []
            attrs=side.get('attribution_tokens') or []
            if not srcs and not evids:
                severity(args.profile,errors,warnings,f'{cid}/{side_id}: conflict side requires source_ids or evidence_ids')
            for sid in srcs:
                if sid not in sm: errors.append(f'{cid}/{side_id}: unknown source_id {sid}')
            for eid in evids:
                if eid not in em: errors.append(f'{cid}/{side_id}: unknown evidence_id {eid}')
                elif srcs and em[eid].get('source_id') not in srcs:
                    severity(args.profile,errors,warnings,
                             f'{cid}/{side_id}: evidence {eid} belongs to source {em[eid].get("source_id")}, not declared side source_ids {srcs}')
            normalized_sides.append({'side_id':side_id,'source_ids':srcs,'evidence_ids':evids,
                                     'value_tokens':[str(x) for x in vals],
                                     'attribution_tokens':[str(x) for x in attrs]})

        # v1.7.2: any numeric token in a cross-side disclosure that is not a declared
        # side value must be explicitly registered as a derived/context exception.
        numeric_exceptions=row.get('cross_side_numeric_exceptions') or []
        if numeric_exceptions and not isinstance(numeric_exceptions,list):
            errors.append(f'{cid}: cross_side_numeric_exceptions must be a list')
            numeric_exceptions=[]
        normalized_exceptions=[]
        for j,ex in enumerate(numeric_exceptions,1):
            if not isinstance(ex,dict):
                errors.append(f'{cid}: cross_side_numeric_exceptions item {j} must be an object'); continue
            claim_id=ex.get('claim_id')
            value_token=str(ex.get('value_token') or '').strip()
            role=ex.get('role')
            reason=str(ex.get('reason') or '').strip()
            src_side_ids=ex.get('source_side_ids') or []
            if not claim_id:
                errors.append(f'{cid}: cross_side_numeric_exceptions item {j} missing claim_id')
            elif claim_id not in cm:
                errors.append(f'{cid}: cross_side_numeric_exceptions item {j} unknown claim_id {claim_id}')
            if not value_token:
                errors.append(f'{cid}: cross_side_numeric_exceptions item {j} missing value_token')
                ex_nums=set()
            else:
                ex_nums=numeric_tokens(value_token)
                if len(ex_nums)!=1:
                    errors.append(f'{cid}: numeric exception {value_token!r} must contain exactly one numeric token')
            if role not in {'derived','context'}:
                errors.append(f'{cid}: numeric exception {value_token!r} has invalid role={role!r}')
            if not reason:
                errors.append(f'{cid}: numeric exception {value_token!r} requires reason')
            if src_side_ids and (not isinstance(src_side_ids,list) or not all(isinstance(x,str) and x for x in src_side_ids)):
                errors.append(f'{cid}: numeric exception {value_token!r} source_side_ids must be a list of side IDs')
                src_side_ids=[]
            unknown_side_ids=[x for x in src_side_ids if x not in side_ids]
            if unknown_side_ids:
                errors.append(f'{cid}: numeric exception {value_token!r} references unknown conflict sides {unknown_side_ids}')
            if role=='derived':
                if len(set(src_side_ids)) < 2:
                    severity(args.profile,errors,warnings,
                             f'{cid}: derived numeric exception {value_token!r} must name at least two source_side_ids')
            normalized_exceptions.append({'claim_id':claim_id,'value_token':value_token,'numeric_tokens':sorted(ex_nums),
                                          'role':role,'reason':reason,'source_side_ids':src_side_ids})

        if status=='resolved':
            if disposition!='resolved':
                errors.append(f'{cid}: status=resolved requires release_disposition=resolved')
            if not str(row.get('resolution') or row.get('reason') or '').strip():
                warnings.append(f'{cid}: resolved conflict has no resolution/reason text')
            details.append({'conflict_id':cid,'status':status,'release_disposition':disposition,'release_blocking':False})
            continue

        if disposition=='resolved':
            errors.append(f'{cid}: unresolved conflict cannot use release_disposition=resolved')
            continue

        # Claims explicitly linked to an object-style conflict use source_conflict_ids.
        for claim_id in set(scoped+disclosure+cross_side):
            c=cm.get(claim_id)
            if not c: continue
            refs=c.get('source_conflict_ids') or []
            if cid not in refs:
                severity(args.profile,errors,warnings,f'{cid}: linked claim {claim_id} does not declare source_conflict_ids containing {cid}')

        if disposition=='blocking':
            severity(args.profile,errors,warnings,f'{cid}: unresolved source conflict is release-blocking')
            details.append({'conflict_id':cid,'status':status,'release_disposition':disposition,'release_blocking':True})
            continue

        if disposition=='historical_only':
            if not affected:
                severity(args.profile,errors,warnings,f'{cid}: historical_only conflict requires affected_claim_ids')
            active_affected=[x for x in affected if x in active]
            if active_affected:
                severity(args.profile,errors,warnings,f'{cid}: historical_only conflict still affects active claims {active_affected}')
            details.append({'conflict_id':cid,'status':status,'release_disposition':disposition,'release_blocking':bool(active_affected)})
            continue

        # disclose_and_scope: fact conflict remains unresolved, but publication can proceed only
        # when the current manuscript carries explicit scoped disclosure tied to current claims.
        if disposition=='disclose_and_scope':
            if not str(row.get('reason') or '').strip():
                severity(args.profile,errors,warnings,f'{cid}: disclose_and_scope requires a reason explaining why release can proceed')
            if not disclosure:
                severity(args.profile,errors,warnings,f'{cid}: disclose_and_scope requires disclosure_claim_ids')
            if not scoped:
                severity(args.profile,errors,warnings,f'{cid}: disclose_and_scope requires scoped_claim_ids or affected_claim_ids')

            missing_disclosure=[]
            for claim_id in disclosure:
                c=active.get(claim_id)
                if not c:
                    missing_disclosure.append(claim_id); continue
                if not anchor_present(manuscript,c.get('manuscript_anchor')):
                    missing_disclosure.append(claim_id)
            if missing_disclosure:
                severity(args.profile,errors,warnings,f'{cid}: disclosure claims are not active and represented in the manuscript: {missing_disclosure}')

            missing_scoped=[]
            for claim_id in scoped:
                c=active.get(claim_id)
                if not c:
                    missing_scoped.append(claim_id); continue
                presence=c.get('manuscript_presence') or 'required'
                if presence=='required' and not anchor_present(manuscript,c.get('manuscript_anchor')):
                    missing_scoped.append(claim_id)
            if missing_scoped:
                severity(args.profile,errors,warnings,f'{cid}: scoped claims are not active/current manuscript claims: {missing_scoped}')

            # Optional literal disclosure tokens guarantee the qualified fact made it into the
            # exact disclosure block rather than existing only in a ledger.
            blocks=[]
            for claim_id in disclosure:
                c=active.get(claim_id)
                anchor=c.get('manuscript_anchor') if c else None
                if not anchor: continue
                for para in re.split(r'\n\s*\n',manuscript):
                    if anchor in para: blocks.append(para)
            disclosure_text='\n'.join(blocks).lower()
            for tok in row.get('required_disclosure_text_tokens') or []:
                if str(tok).lower() not in disclosure_text:
                    severity(args.profile,errors,warnings,f'{cid}: required disclosure text token not found in disclosure claim block: {tok}')

            side_detail={}
            if normalized_sides:
                # Side-aware contracts close the v1.7 gap where disclosure existed but a scoped claim
                # could still silently blend evidence from competing provenance streams.
                if len(normalized_sides) < 2:
                    severity(args.profile,errors,warnings,f'{cid}: disclose_and_scope conflict_sides must describe at least two competing sides')
                if not cross_side:
                    severity(args.profile,errors,warnings,f'{cid}: conflict_sides requires cross_side_claim_ids for explicit manuscript disclosure of competing provenance')
                for claim_id in cross_side:
                    if claim_id not in disclosure:
                        severity(args.profile,errors,warnings,f'{cid}: cross_side_claim_id {claim_id} must also be a disclosure_claim_id')

                for claim_id in set(scoped+disclosure):
                    c=active.get(claim_id)
                    if not c: continue
                    represented=claim_conflict_sides(c, normalized_sides, em)
                    side_detail[claim_id]=sorted(represented)
                    if claim_id in cross_side:
                        if len(represented) < 2:
                            severity(args.profile,errors,warnings,
                                     f'{cid}: cross-side disclosure claim {claim_id} does not represent at least two conflict sides; found {sorted(represented)}')
                        # Each represented side must be visibly attributed in the cross-side claim text.
                        txt=str(c.get('text') or '').lower()
                        for side in normalized_sides:
                            if side['side_id'] not in represented: continue
                            attrs=[x.lower() for x in side.get('attribution_tokens') or [] if x.strip()]
                            if not attrs:
                                severity(args.profile,errors,warnings,
                                         f'{cid}/{side["side_id"]}: cross-side disclosure requires attribution_tokens')
                            elif not any(tok in txt for tok in attrs):
                                severity(args.profile,errors,warnings,
                                         f'{cid}: cross-side disclosure claim {claim_id} lacks attribution for side {side["side_id"]}; expected one of {side.get("attribution_tokens")}')

                        # Numeric provenance closure: every numeric token in the cross-side claim
                        # must be either a source-side value or an explicitly registered derived/context value.
                        side_nums=set()
                        for side in normalized_sides:
                            if side['side_id'] in represented:
                                for tok in side.get('value_tokens') or []:
                                    side_nums |= numeric_tokens(tok)
                        claim_ex=[x for x in normalized_exceptions if x.get('claim_id')==claim_id]
                        exception_nums=set()
                        for ex in claim_ex:
                            exception_nums |= set(ex.get('numeric_tokens') or [])
                            if ex.get('numeric_tokens') and not (set(ex['numeric_tokens']) & numeric_tokens(c.get('text') or '')):
                                severity(args.profile,errors,warnings,
                                         f'{cid}: registered numeric exception {ex.get("value_token")!r} is not present in cross-side claim {claim_id}')
                        claim_nums=numeric_tokens(c.get('text') or '')
                        unexpected=sorted(claim_nums - side_nums - exception_nums)
                        if unexpected:
                            severity(args.profile,errors,warnings,
                                     f'{cid}: cross-side disclosure claim {claim_id} contains undeclared numeric token(s) {unexpected}; add them to a conflict side value_tokens or register cross_side_numeric_exceptions')

                        # Also audit the anchored manuscript paragraph. Numeric tokens belonging to
                        # other registered claims in the same paragraph are allowed; unregistered
                        # prose-level numbers are not.
                        para=paragraph_for_anchor(manuscript,c.get('manuscript_anchor'))
                        if para:
                            para_claim_ids=[]
                            for m in re.finditer(r'<!--\s*CLAIM:([A-Za-z0-9_.:-]+)\s*-->', para):
                                para_claim_ids.append(m.group(1))
                            other_claim_nums=set()
                            for other_id in para_claim_ids:
                                if other_id==claim_id or other_id not in active:
                                    continue
                                other_claim_nums |= numeric_tokens(active[other_id].get('text') or '')
                            para_nums=numeric_tokens(re.sub(r'<!--.*?-->', ' ', para, flags=re.S))
                            para_unexpected=sorted(para_nums - side_nums - exception_nums - other_claim_nums)
                            if para_unexpected:
                                severity(args.profile,errors,warnings,
                                         f'{cid}: manuscript paragraph for cross-side disclosure claim {claim_id} contains unregistered numeric token(s) {para_unexpected}')
                    elif claim_id in scoped:
                        if len(represented) != 1:
                            severity(args.profile,errors,warnings,
                                     f'{cid}: scoped claim {claim_id} must resolve to exactly one conflict side, found {sorted(represented)}; split source-specific claims or move cross-source comparison into a disclosure claim')

                for ex in normalized_exceptions:
                    if ex.get('claim_id') not in cross_side:
                        severity(args.profile,errors,warnings,
                                 f'{cid}: numeric exception {ex.get("value_token")!r} is attached to {ex.get("claim_id")}, which is not a cross_side_claim_id')

                represented_cross=[x for x in cross_side if len(set(side_detail.get(x,[]))) >= 2]
                if not represented_cross:
                    severity(args.profile,errors,warnings,f'{cid}: no cross-side disclosure claim actually represents the competing conflict sides')

            details.append({'conflict_id':cid,'status':status,'release_disposition':disposition,'release_blocking':False,
                            'disclosure_claim_ids':disclosure,'scoped_claim_ids':scoped,
                            'cross_side_claim_ids':cross_side,'claim_side_map':side_detail})

    report={'ok':not errors,'profile':args.profile,'details':details,'errors':errors,'warnings':warnings,
            'summary':{'conflict_count':len(normalized),'error_count':len(errors),'warning_count':len(warnings),
                       'blocking_count':sum(1 for x in details if x.get('release_blocking'))}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
