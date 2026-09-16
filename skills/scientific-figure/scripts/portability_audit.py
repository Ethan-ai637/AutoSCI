#!/usr/bin/env python3
import argparse, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

GENERIC_FONTS={'serif','sans-serif','monospace','cursive','fantasy','system-ui','ui-sans-serif','ui-serif','ui-monospace'}
URL_FUNC_RE=re.compile(r'url\(\s*["\']?([^"\')]+)')
IMPORT_RE=re.compile(r'@import\b',re.I)
EVENT_RE=re.compile(r'^on[a-z]+$',re.I)

def local(tag): return tag.split('}',1)[-1]
def href_of(el): return el.get('href') or el.get('{http://www.w3.org/1999/xlink}href') or ''
def safe_ref(v): return (not v) or v.startswith('#') or v.startswith('data:')
def font_family(el):
    raw=el.get('font-family')
    if raw: return raw
    style=el.get('style','')
    m=re.search(r'font-family\s*:\s*([^;]+)',style,re.I)
    return m.group(1).strip() if m else ''
def has_generic_fallback(raw):
    fams=[x.strip().strip('"\'').lower() for x in raw.split(',') if x.strip()]
    return bool(set(fams)&GENERIC_FONTS)

def main():
    ap=argparse.ArgumentParser(description='Audit an SVG for self-contained, cross-machine release portability')
    ap.add_argument('spec'); ap.add_argument('svg'); args=ap.parse_args()
    import json
    try: spec=json.loads(Path(args.spec).read_text(encoding='utf-8'))
    except Exception as e: print(f'ERROR: cannot read spec: {e}'); return 2
    try: root=ET.fromstring(Path(args.svg).read_text(encoding='utf-8'))
    except Exception as e: print(f'ERROR: invalid SVG/XML: {e}'); return 2
    qa=spec.get('qa',{}) or {}; mode=qa.get('portability_audit','required')
    if mode=='off': print('OK: portability audit disabled by spec'); return 0
    allow_external=bool(qa.get('allow_external_resources',False))
    allow_raster=bool(qa.get('allow_embedded_raster',True))
    require_fallback=bool(qa.get('require_generic_font_fallback',False))
    errors=[]; warnings=[]; font_stacks=set(); embedded_raster=0
    for el in root.iter():
        tag=local(el.tag)
        for k,v in el.attrib.items():
            if EVENT_RE.match(local(k)): errors.append(f'event handler attribute is not portable/safe: {local(k)} on <{tag}>')
            for ref in URL_FUNC_RE.findall(str(v)):
                if not safe_ref(ref) and not allow_external: errors.append(f'external CSS/SVG url() dependency on <{tag}>: {ref}')
        if tag=='script': errors.append('<script> is forbidden in a publication SVG release')
        if tag=='style':
            txt=''.join(el.itertext())
            if IMPORT_RE.search(txt): errors.append('@import in SVG CSS is an external dependency')
            for ref in URL_FUNC_RE.findall(txt):
                if not safe_ref(ref) and not allow_external: errors.append(f'external CSS url() dependency: {ref}')
        if tag in ('image','use','feImage'):
            href=href_of(el)
            if tag=='image' and href.startswith('data:'): embedded_raster+=1
            elif href and not safe_ref(href) and not allow_external:
                errors.append(f'<{tag}> depends on external/local resource: {href}')
        ff=font_family(el)
        if ff: font_stacks.add(ff)
    if embedded_raster and not allow_raster: errors.append(f'contains {embedded_raster} embedded raster image(s) but qa.allow_embedded_raster=false')
    elif embedded_raster: warnings.append(f'contains {embedded_raster} embedded raster image(s); verify resolution/licensing and prefer vector when practical')
    for ff in sorted(font_stacks):
        if not has_generic_fallback(ff):
            msg=f"font stack has no generic fallback: {ff!r}"
            (errors if require_fallback else warnings).append(msg)
    for w in warnings: print('WARN:',w)
    for e in errors: print('ERROR:',e)
    if errors and mode=='required': return 1
    if errors and mode=='recommended':
        print('WARN: portability issues are advisory because qa.portability_audit=recommended')
        return 0
    print(f'OK: portability audit (font_stacks={len(font_stacks)}, embedded_raster={embedded_raster}, external_allowed={allow_external})')
    return 0
if __name__=='__main__': raise SystemExit(main())
