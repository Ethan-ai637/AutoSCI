import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const output = execFileSync('npm', ['pack', '--dry-run', '--json'], { cwd: root, encoding: 'utf8' });
const manifest = JSON.parse(output)[0];
const shipped = new Set(manifest.files.map((file) => file.path));
const skills = readdirSync(join(root, 'skills'), { withFileTypes: true })
  .filter((item) => item.isDirectory()).map((item) => item.name);
assert.ok(skills.length >= 10, 'Expected at least ten released AutoSCI Skills');
assert.ok(shipped.has('bin/autosci.mjs'), 'CLI binary missing from npm package');
for (const name of skills) {
  assert.ok(shipped.has('skills/' + name + '/SKILL.md'),
    'Missing ' + name + '/SKILL.md from npm package');
}
console.log('npm package OK: ' + skills.length + ' Skills, ' + shipped.size +
  ' package files, ' + manifest.size + ' bytes');
