#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from _common import rel_files, sha256_file, load_json
from _state import build_state


def main():
    ap=argparse.ArgumentParser(description='Write a SHA-256 release manifest with semantic workspace-state lineage.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--output', default='manifest.json')
    args=ap.parse_args()
    root=Path(args.workspace).resolve(); out=(root/args.output).resolve()
    project=load_json(root/'project.json') if (root/'project.json').exists() else {}
    state,_=build_state(root)
    state_path=root/'workspace_state.current.json'
    state_path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    entries=[]
    for rel in rel_files(root):
        p=root/rel
        if p.resolve()==out: continue
        entries.append({'path':rel.as_posix(),'size':p.stat().st_size,'sha256':sha256_file(p)})

    baseline_path=root/'workspace_state.previous.json'
    baseline=load_json(baseline_path) if baseline_path.exists() else {}
    manifest={
        'schema_version':2,
        'project_id':project.get('project_id'),
        'skill_version':project.get('skill_version'),
        'profile':project.get('profile'),
        'mode':project.get('mode'),
        'workspace_state_id':state.get('state_id'),
        'parent_workspace_state_id':baseline.get('state_id'),
        'files':entries,
    }
    out.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'workspace_state_id':state.get('state_id'),'parent_workspace_state_id':baseline.get('state_id')},indent=2))

if __name__=='__main__': main()
