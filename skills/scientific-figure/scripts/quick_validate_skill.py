#!/usr/bin/env python3
import re, sys
from pathlib import Path

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
    errors=[]; warnings=[]
    skill=root/"SKILL.md"
    if not skill.exists(): errors.append("missing SKILL.md")
    else:
        text=skill.read_text(encoding="utf-8")
        if not text.startswith("---\n"): errors.append("SKILL.md missing YAML frontmatter")
        m=re.match(r"---\n(.*?)\n---\n",text,re.S)
        if not m: errors.append("could not parse frontmatter block")
        else:
            fm=m.group(1)
            name=re.search(r"^name:\s*(.+)$",fm,re.M)
            desc=re.search(r"^description:\s*(.+)$",fm,re.M)
            if not name: errors.append("frontmatter missing name")
            else:
                n=name.group(1).strip()
                if not re.fullmatch(r"[a-z0-9-]{1,64}",n): errors.append(f"invalid skill name: {n}")
                if root.name!=n: warnings.append(f"folder name {root.name!r} differs from skill name {n!r}")
            if not desc or not desc.group(1).strip(): errors.append("frontmatter missing description")
            extra=[]
            for line in fm.splitlines():
                if re.match(r"^[A-Za-z0-9_-]+\s*:",line):
                    key=line.split(":",1)[0].strip()
                    if key not in ("name","description"): extra.append(key)
            if extra: errors.append("unsupported frontmatter keys: "+", ".join(extra))
    for rel in ["STABILITY.md","agents/openai.yaml","references/figure_modes.md","references/figure_schema.md","references/design_system.md","references/critic_rubric.md","references/pattern_library.md","references/source_grounding.md","references/layout_tournament.md","references/publication_robustness.md","assets/figure_spec.template.json","assets/layout_tournament.template.json","scripts/source_audit.py","scripts/freeze_spec.py","scripts/complexity_gate.py","scripts/robustness_audit.py","scripts/target_legibility.py","scripts/render_package.py","scripts/geometry_audit.py","scripts/notation_audit.py","scripts/artifact_manifest.py","scripts/finalize_figure.py","references/geometry_contract.md","references/math_fidelity.md","references/release_portability.md","scripts/doctor.py","scripts/fingerprint_source.py","scripts/portability_audit.py","scripts/export_vector.py","scripts/verify_release.py","references/workflow_profiles.md","scripts/profile_audit.py","scripts/set_profile.py","references/orchestration.md","assets/workflow_state.template.json","scripts/orchestrate.py","scripts/critic_gate.py","references/benchmarking.md","assets/benchmark_case.template.json","assets/benchmark_evaluation.template.json","assets/benchmark_suite.template.json","scripts/benchmark.py","scripts/benchmark_suite.py"]:
        if not (root/rel).exists(): warnings.append(f"recommended resource missing: {rel}")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: skill structure looks valid -> {root}")
    return 0

if __name__=="__main__": sys.exit(main())
