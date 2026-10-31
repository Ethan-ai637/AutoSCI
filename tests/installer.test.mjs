import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = fileURLToPath(new URL('..', import.meta.url));
const cli = join(root, 'bin', 'autosci.mjs');
const skills = [
  'academic-manuscript-writing', 'academic-research-presentation',
  'experiment-execution', 'experiment-goal-design', 'literature-research',
  'manuscript-reviewer', 'method-goal-pursuit', 'paper-reproduction',
  'scientific-data-analysis', 'scientific-figure',
];
function run(args, { cwd = root, env = {} } = {}) {
  return spawnSync(process.execPath, [cli, ...args], {
    cwd, env: { ...process.env, ...env }, encoding: 'utf8',
  });
}
function scratch(t) {
  const path = mkdtempSync(join(tmpdir(), 'autosci-install-test-'));
  t.after(() => rmSync(path, { recursive: true, force: true }));
  return path;
}

test('all ten skills are discoverable, with valid SKILL.md frontmatter', () => {
  const result = run(['list']);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(result.stdout.trim().split('\n'), skills);
  assert.equal(run(['verify']).status, 0);
});
test('project install copies the complete skill directory', (t) => {
  const project = scratch(t);
  const dest = join(project, '.agents', 'skills', 'scientific-figure');
  const result = run(['install', 'scientific-figure'], { cwd: project });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(existsSync(join(dest, 'SKILL.md')), true);
  assert.equal(existsSync(join(dest, 'scripts')), true);
});
test('install --all copies every discovered skill into --dir', (t) => {
  const dir = join(scratch(t), 'skills');
  const result = run(['install', '--all', '--dir', dir]);
  assert.equal(result.status, 0, result.stderr);
  for (const skill of skills) assert.equal(existsSync(join(dir, skill, 'SKILL.md')), true);
});
test('global Codex install respects CODEX_HOME', (t) => {
  const codexHome = join(scratch(t), 'custom-codex');
  const result = run(['install', 'literature-research', '--global'], {
    env: { CODEX_HOME: codexHome },
  });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(existsSync(join(codexHome, 'skills', 'literature-research', 'SKILL.md')), true);
});
test('claude-code and cursor target project skill folders', (t) => {
  const project = scratch(t);
  for (const agent of ['claude-code', 'cursor']) {
    const result = run(['install', 'literature-research', '--agent', agent], { cwd: project });
    assert.equal(result.status, 0, result.stderr);
    const dir = agent === 'cursor' ? '.cursor' : '.claude';
    assert.equal(existsSync(join(project, dir, 'skills', 'literature-research', 'SKILL.md')), true);
  }
});
test('existing skill is never replaced without --force', (t) => {
  const dir = scratch(t);
  const dest = join(dir, 'paper-reproduction');
  assert.equal(run(['install', 'paper-reproduction', '--dir', dir]).status, 0);
  writeFileSync(join(dest, 'LOCAL_NOTES.md'), 'keep me');
  assert.notEqual(run(['install', 'paper-reproduction', '--dir', dir]).status, 0);
  assert.equal(readFileSync(join(dest, 'LOCAL_NOTES.md'), 'utf8'), 'keep me');
  assert.equal(run(['install', 'paper-reproduction', '--dir', dir, '--force']).status, 0);
  assert.equal(existsSync(join(dest, 'LOCAL_NOTES.md')), false);
});
test('collision preflight prevents partial batch installation', (t) => {
  const dir = scratch(t);
  mkdirSync(join(dir, 'literature-research'));
  const result = run(['install', 'scientific-figure', 'literature-research', '--dir', dir]);
  assert.notEqual(result.status, 0);
  assert.equal(existsSync(join(dir, 'scientific-figure')), false);
});
test('unknown skills and invalid args fail without writing', (t) => {
  const dir = scratch(t);
  assert.notEqual(run(['install', '../../not-safe', '--dir', dir]).status, 0);
  assert.notEqual(run(['install', '--all', '--agent', 'bad-agent'], { cwd: dir }).status, 0);
  assert.notEqual(run(['install', '--all', 'scientific-figure', '--dir', dir]).status, 0);
  assert.equal(existsSync(join(dir, 'scientific-figure')), false);
});
test('dry run does not mutate any folders', (t) => {
  const dir = join(scratch(t), 'out');
  const result = run(['install', 'scientific-data-analysis', '--dir', dir, '--dry-run']);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /Would install scientific-data-analysis/);
  assert.equal(existsSync(dir), false);
});
