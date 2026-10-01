#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from _state import build_state


def main():
    ap = argparse.ArgumentParser(description='Capture a semantic workspace checkpoint for revision lineage and provenance auditing.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--output', default='workspace_state.current.json')
    args = ap.parse_args()
    root = Path(args.workspace).resolve()
    state, _ = build_state(root)
    out = root/args.output
    out.write_text(json.dumps(state, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'state_id': state['state_id']}, indent=2))

if __name__ == '__main__':
    main()
