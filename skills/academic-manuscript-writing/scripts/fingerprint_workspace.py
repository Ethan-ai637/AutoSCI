#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from _common import load_jsonl, sha256_file

def main():
    ap=argparse.ArgumentParser(description='Fingerprint declared manuscript sources and core workspace artifacts.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--output', default='fingerprints.current.json')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    sources=load_jsonl(root/'sources.jsonl')
    source_fps={}
    for s in sources:
        sid=s.get('source_id')
        p=s.get('path')
        item={'source_id':sid,'path':p,'exists':False,'sha256':None,'version':s.get('version')}
        if p:
            fp=(root/p).resolve()
            try:
                fp.relative_to(root)
                inside=True
            except ValueError:
                inside=False
            if inside and fp.is_file():
                item['exists']=True
                item['sha256']=sha256_file(fp)
        source_fps[sid]=item
    writing_source_fps={}
    wsp=root/'writing_sources.jsonl'
    if wsp.exists():
        for s in load_jsonl(wsp):
            sid=s.get('writing_source_id'); rel=s.get('path')
            item={'writing_source_id':sid,'path':rel,'url':s.get('url'),'retrieved_at':s.get('retrieved_at'),'exists':False,'sha256':None}
            if rel and '://' not in str(rel):
                fp=(root/rel).resolve()
                try: fp.relative_to(root); inside=True
                except ValueError: inside=False
                if inside and fp.is_file():
                    item['exists']=True; item['sha256']=sha256_file(fp)
            if sid: writing_source_fps[sid]=item
    core={}
    for name in ['project.json','section_plan.json','sources.jsonl','evidence.jsonl','claims.jsonl','writing_sources.jsonl','writing_profile.json','manuscript_contract.json','manuscript.md','revision_log.jsonl','reviewer_response_map.jsonl','revision_obligations.jsonl','reporting_contracts.jsonl','paragraph_contracts.jsonl']:
        p=root/name
        if p.is_file(): core[name]=sha256_file(p)
    out={'schema_version':1,'sources':source_fps,'writing_sources':writing_source_fps,'core':core}
    (root/args.output).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(str(root/args.output))

if __name__=='__main__': main()
