from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name: str, *args: str):
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def make_repo(root: Path) -> tuple[Path, str]:
    repo = root / "repo"; repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
    (repo / "eval.py").write_text('print("ok")\n')
    (repo / "config.yaml").write_text("x: 1\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    return repo, sha


def prepare_workspace(root: Path, repo: Path, sha: str, rule_kind="exact") -> Path:
    ws = root / "ws"
    cp = run_script("init_workspace.py", str(ws), "--mode", "REPO_REPRODUCE", "--profile", "release")
    assert cp.returncode == 0, cp.stderr
    contract = json.loads((ws / "reproduction_contract.json").read_text())
    contract.update({"skill_version":"1.2.0","target_claims":[{
        "claim_id":"claim_1","type":"table_result","paper_locator":"Table 1","metric":"accuracy",
        "reported":{"value":1.0,"unit":None,"variation":{"kind":"std","value":0.1} if rule_kind=="reported_variation" else None},
        "scope":{"dataset_id":"data_1","checkpoint_id":"ckpt_1","config":"config.yaml"},
        "comparison_rule":{"kind":rule_kind,"predeclared":True,"parameters":{}},"unknowns":[]
    }]})
    (ws / "reproduction_contract.json").write_text(json.dumps(contract, indent=2)+"\n")
    paper=json.loads((ws/'paper_manifest.json').read_text()); paper.update({"title":"Test","canonical_url":"https://example.invalid/paper"}); (ws/'paper_manifest.json').write_text(json.dumps(paper,indent=2)+"\n")
    repo_manifest={"schema_version":"1.1","repository_id":"repo_1","remote_url":"x","official_status":"author_official","identity_evidence":["paper link"],"source_revision":{"commit":sha,"branch":"main","tags_at_head":[],"release":None,"selection_basis":"paper_documented_commit","selection_evidence":["test"]},"git":{"dirty":False,"submodules":[],"lfs_detected":False},"detected":{},"notes":None}
    (ws/'repository_manifest.json').write_text(json.dumps(repo_manifest,indent=2)+"\n")
    plan={"schema_version":"1.1","plan_id":"p","created_at":None,"items":[{"plan_item_id":"s","stage":"smoke","claim_ids":["claim_1"],"scientific_target":False,"command":None},{"plan_item_id":"t","stage":"target","claim_ids":["claim_1"],"scientific_target":True,"command":None}]}
    (ws/'run_plan.json').write_text(json.dumps(plan,indent=2)+"\n")
    (ws/'claim_code_map.jsonl').write_text(json.dumps({"mapping_id":"m1","claim_id":"claim_1","paper_object":"Table 1","paper_locator":"Table 1","repo_artifacts":[{"path":"eval.py","role":"entrypoint","revision":sha}],"input_artifacts":[],"output_artifacts":[],"mapping_status":"verified","basis":"inspection","notes":None})+"\n")
    (ws/'data_manifest.json').write_text(json.dumps({"schema_version":"1.1","datasets":[{"dataset_id":"data_1","name":"d","retrieval_status":"available"}]},indent=2)+"\n")
    (ws/'checkpoint_manifest.jsonl').write_text(json.dumps({"checkpoint_id":"ckpt_1","claim_ids":["claim_1"],"retrieval_status":"available","sha256":"abc"})+"\n")
    (ws/'environment/resolved/system.json').write_text('{}\n')
    return ws


class SemanticGateTests(unittest.TestCase):
    def test_contract_change_after_target_run_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--config","config.yaml","--dataset-id","data_1","--checkpoint-id","ckpt_1","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py")
            self.assertEqual(cp.returncode,0,cp.stderr)
            contract=json.loads((ws/'reproduction_contract.json').read_text()); contract['notes']='changed after run'; (ws/'reproduction_contract.json').write_text(json.dumps(contract,indent=2)+"\n")
            cp=run_script("preflight.py",str(ws))
            self.assertNotEqual(cp.returncode,0)
            report=json.loads((ws/'preflight.json').read_text())
            self.assertIn('run_provenance_stale',{f['code'] for f in report['findings']})

    def test_deleted_provenance_manifest_after_target_run_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--config","config.yaml","--dataset-id","data_1","--checkpoint-id","ckpt_1","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py")
            self.assertEqual(cp.returncode,0,cp.stderr)
            (ws/'data_manifest.json').unlink()
            cp=run_script("preflight.py",str(ws)); self.assertNotEqual(cp.returncode,0)
            report=json.loads((ws/'preflight.json').read_text())
            self.assertIn('run_provenance_missing',{f['code'] for f in report['findings']})

    def test_target_run_with_incomplete_provenance_snapshot_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            (ws/'claim_code_map.jsonl').unlink()
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--dataset-id","data_1","--checkpoint-id","ckpt_1","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py")
            self.assertEqual(cp.returncode,0,cp.stderr)
            cp=run_script("preflight.py",str(ws)); self.assertNotEqual(cp.returncode,0)
            report=json.loads((ws/'preflight.json').read_text())
            self.assertIn('target_run_incomplete_snapshot',{f['code'] for f in report['findings']})

    def test_mismatched_metric_cannot_reconcile_to_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--dataset-id","data_1","--checkpoint-id","ckpt_1","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py")
            self.assertEqual(cp.returncode,0,cp.stderr)
            with (ws/'metrics.csv').open('w',newline='') as f:
                w=csv.writer(f); w.writerow(['run_id','claim_id','metric','value','unit','dataset','split','condition','aggregation','source_artifact','notes']); w.writerow(['r1','claim_1','loss','1.0','','','','','','',''])
            cp=run_script("reconcile_claims.py",str(ws)); self.assertEqual(cp.returncode,0,cp.stderr)
            cand=json.loads((ws/'reproduction_assessment.candidate.json').read_text())
            self.assertEqual(cand['assessments'],[])
            cp=run_script("preflight.py",str(ws)); self.assertNotEqual(cp.returncode,0)
            report=json.loads((ws/'preflight.json').read_text())
            self.assertIn('metric_name_mismatch',{f['code'] for f in report['findings']})

    def test_run_wrapper_filters_unrequested_environment_variables(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            command=[sys.executable,"-c","import os; print(os.getenv('PAPER_REPRO_TEST_SECRET', '<absent>')); print(os.getenv('PAPER_REPRO_TEST_PUBLIC', '<absent>'))"]
            import os
            previous_secret=os.environ.get('PAPER_REPRO_TEST_SECRET')
            previous_public=os.environ.get('PAPER_REPRO_TEST_PUBLIC')
            os.environ['PAPER_REPRO_TEST_SECRET']='must-not-leak'
            os.environ['PAPER_REPRO_TEST_PUBLIC']='explicit-value'
            try:
                cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--run-id","env_1","--claim-id","claim_1","--run-kind","diagnostic","--cwd",str(repo),"--logs-dir",str(ws/'logs'),"--env","PAPER_REPRO_TEST_PUBLIC","--",*command)
                self.assertEqual(cp.returncode,0,cp.stderr)
                row=json.loads((ws/'run_ledger.jsonl').read_text().strip())
                out=Path(row['stdout_path']).read_text()
                self.assertEqual(out.splitlines(),['<absent>','explicit-value'])
                self.assertIn('PAPER_REPRO_TEST_PUBLIC',row['environment_variable_names'])
                self.assertNotIn('PAPER_REPRO_TEST_SECRET',row['environment_variable_names'])
            finally:
                if previous_secret is None: os.environ.pop('PAPER_REPRO_TEST_SECRET',None)
                else: os.environ['PAPER_REPRO_TEST_SECRET']=previous_secret
                if previous_public is None: os.environ.pop('PAPER_REPRO_TEST_PUBLIC',None)
                else: os.environ['PAPER_REPRO_TEST_PUBLIC']=previous_public

    def test_run_wrapper_refuses_credential_like_environment_variables(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            for name in ['HF_TOKEN','GITHUB_PAT']:
                cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--run-id","env_1","--claim-id","claim_1","--run-kind","diagnostic","--cwd",str(repo),"--logs-dir",str(ws/'logs'),"--env",name,"--",sys.executable,"-c","print('should not run')")
                self.assertNotEqual(cp.returncode,0)
                self.assertIn('credential-like',cp.stderr)

    def test_unknown_checkpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha)
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--dataset-id","data_1","--checkpoint-id","missing_ckpt","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py")
            self.assertEqual(cp.returncode,0,cp.stderr)
            cp=run_script("preflight.py",str(ws)); self.assertNotEqual(cp.returncode,0)
            report=json.loads((ws/'preflight.json').read_text())
            self.assertIn('run_unknown_checkpoint',{f['code'] for f in report['findings']})

    def test_exact_reproduction_requires_exact_rule_and_clean_target_metric(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha,rule_kind='reported_variation')
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--dataset-id","data_1","--checkpoint-id","ckpt_1","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py")
            self.assertEqual(cp.returncode,0,cp.stderr)
            with (ws/'metrics.csv').open('w',newline='') as f:
                w=csv.writer(f); w.writerow(['run_id','claim_id','metric','value','unit','dataset','split','condition','aggregation','source_artifact','notes']); w.writerow(['r1','claim_1','accuracy','1.0','','','','','','',''])
            (ws/'reproduction_assessment.json').write_text(json.dumps({"schema_version":"1.1","assessments":[{"claim_id":"claim_1","state":"exact_reproduction","supporting_run_ids":["r1"],"material_deviations":[],"limitations":[]}]},indent=2)+"\n")
            cp=run_script("preflight.py",str(ws)); self.assertNotEqual(cp.returncode,0)
            report=json.loads((ws/'preflight.json').read_text())
            self.assertIn('exact_without_exact_rule',{f['code'] for f in report['findings']})

    def test_reconcile_claims_generates_candidate_not_final(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,sha=make_repo(root); ws=prepare_workspace(root,repo,sha,rule_kind='reported_variation')
            cp=run_script("run_with_ledger.py","--ledger",str(ws/'run_ledger.jsonl'),"--workspace",str(ws),"--run-id","r1","--claim-id","claim_1","--run-kind","target","--cwd",str(repo),"--dataset-id","data_1","--checkpoint-id","ckpt_1","--logs-dir",str(ws/'logs'),"--",sys.executable,"eval.py"); self.assertEqual(cp.returncode,0,cp.stderr)
            with (ws/'metrics.csv').open('w',newline='') as f:
                w=csv.writer(f); w.writerow(['run_id','claim_id','metric','value','unit','dataset','split','condition','aggregation','source_artifact','notes']); w.writerow(['r1','claim_1','accuracy','1.05','','','','','','',''])
            cp=run_script("reconcile_claims.py",str(ws)); self.assertEqual(cp.returncode,0,cp.stderr)
            cand=json.loads((ws/'reproduction_assessment.candidate.json').read_text())
            self.assertEqual(cand['assessments'][0]['state'],'within_reported_variation')
            final=json.loads((ws/'reproduction_assessment.json').read_text())
            self.assertEqual(final['assessments'],[])


if __name__ == '__main__':
    unittest.main()
