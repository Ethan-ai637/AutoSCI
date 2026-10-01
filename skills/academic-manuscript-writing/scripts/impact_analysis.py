#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from _common import load_json, load_jsonl

def main():
    ap=argparse.ArgumentParser(description='Identify active manuscript claims affected by changed/missing source fingerprints, with historical inactive-claim reporting.')
    ap.add_argument('--old', required=True)
    ap.add_argument('--new', required=True)
    ap.add_argument('--claims', default='claims.jsonl')
    ap.add_argument('--sources', default='sources.jsonl')
    ap.add_argument('--evidence', default='evidence.jsonl')
    ap.add_argument('--report', default='impact_report.json')
    args=ap.parse_args()
    old=load_json(Path(args.old)); new=load_json(Path(args.new))
    claims=load_jsonl(Path(args.claims)); evidence=load_jsonl(Path(args.evidence))
    ev_by_id={e.get('evidence_id'):e for e in evidence}
    old_s=old.get('sources',{}); new_s=new.get('sources',{})
    changed=[]
    for sid in sorted(set(old_s)|set(new_s)):
        a=old_s.get(sid); b=new_s.get(sid)
        if a is None or b is None or a.get('sha256')!=b.get('sha256') or a.get('exists')!=b.get('exists') or a.get('version')!=b.get('version'):
            changed.append(sid)
    old_ws=old.get('writing_sources',{}); new_ws=new.get('writing_sources',{})
    changed_writing=[]
    for sid in sorted(set(old_ws)|set(new_ws)):
        a=old_ws.get(sid); b=new_ws.get(sid)
        if a is None or b is None or a.get('sha256')!=b.get('sha256') or a.get('exists')!=b.get('exists') or a.get('retrieved_at')!=b.get('retrieved_at') or a.get('url')!=b.get('url'):
            changed_writing.append(sid)
    changed_set=set(changed)
    direct=[]; historical=[]; affected_family_ids=set()
    for c in claims:
        srcs=[]
        for eid in c.get('evidence_ids') or []:
            e=ev_by_id.get(eid)
            if e and e.get('source_id'): srcs.append(e['source_id'])
        hit=sorted(set(srcs)&changed_set)
        if not hit:
            continue
        state=c.get('lifecycle_state') or 'active'
        item={'claim_id':c.get('claim_id'),'claim_family_id':c.get('claim_family_id'),'section':c.get('section'),
              'reason':'direct_source_change','changed_source_ids':hit,'status':c.get('status'),
              'lifecycle_state':state,'text':c.get('text','')}
        if state=='active':
            fid=c.get('claim_family_id')
            if fid: affected_family_ids.add(fid)
            direct.append(item)
        else:
            historical.append(item)
    direct_ids={x['claim_id'] for x in direct}
    propagated=[]
    for c in claims:
        if (c.get('lifecycle_state') or 'active')!='active':
            continue
        if c.get('claim_id') in direct_ids: continue
        fid=c.get('claim_family_id')
        if fid and fid in affected_family_ids:
            propagated.append({'claim_id':c.get('claim_id'),'claim_family_id':fid,'section':c.get('section'),
                               'reason':'claim_family_dependency','changed_source_ids':[],'status':c.get('status'),
                               'lifecycle_state':'active','text':c.get('text','')})
    affected=direct+propagated
    report={
      'changed_source_ids':changed,
      'changed_writing_source_ids':changed_writing,
      'writing_profile_review_required':bool(changed_writing),
      'writing_artifacts_to_review':['writing_profile.json','manuscript_contract.json','section_plan.json','manuscript.md'] if changed_writing else [],
      'affected_claim_family_ids':sorted(affected_family_ids),
      'directly_affected_claims':direct,
      'family_propagated_claims':propagated,
      'affected_claims':affected,
      'historical_inactive_claims_linked_to_changed_sources':historical,
      'affected_sections':sorted({x.get('section') for x in affected if x.get('section')})
    }
    Path(args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
