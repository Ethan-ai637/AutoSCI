#!/usr/bin/env node
/** Dependency-free installer: copies Skills without running their research scripts. */
import {
  cpSync, existsSync, lstatSync, mkdirSync, readFileSync, readdirSync,
  renameSync, rmSync,
} from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const packageRoot = fileURLToPath(new URL('..', import.meta.url));
const skillsRoot = join(packageRoot, 'skills');
const supportedAgents = ['codex', 'claude-code', 'cursor'];

function fail(message) { throw new Error(message); }

function discoverSkills() {
  if (!existsSync(skillsRoot)) fail('The package is missing its skills/ directory.');
  return readdirSync(skillsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && existsSync(join(skillsRoot, entry.name, 'SKILL.md')))
    .map((entry) => entry.name).sort();
}

function destinationFor(agent, globalScope) {
  const home = homedir();
  if (agent === 'codex') {
    return globalScope
      ? join(resolve(process.env.CODEX_HOME || join(home, '.codex')), 'skills')
      : resolve('.agents', 'skills');
  }
  if (agent === 'claude-code') {
    return globalScope ? join(home, '.claude', 'skills') : resolve('.claude', 'skills');
  }
  if (agent === 'cursor') {
    return globalScope ? join(home, '.cursor', 'skills') : resolve('.cursor', 'skills');
  }
  fail('Unsupported agent: ' + agent + '. Use ' + supportedAgents.join(', ') + ', or --dir PATH.');
}

function parseArgs(argv) {
  const [command = 'help', ...rest] = argv;
  if (!['help', 'list', 'verify', 'install'].includes(command)) {
    fail('Unknown command: ' + command + '. Run autosci help.');
  }
  const opts = {
    command, names: [], all: false, global: false, force: false,
    dryRun: false, agent: 'codex', dir: null,
  };
  for (let i = 0; i < rest.length; i += 1) {
    const token = rest[i];
    if (token === '--all') opts.all = true;
    else if (token === '-g' || token === '--global') opts.global = true;
    else if (token === '--force') opts.force = true;
    else if (token === '--dry-run') opts.dryRun = true;
    else if (token === '--agent' || token === '--dir') {
      if (!rest[i + 1] || rest[i + 1].startsWith('-')) fail('Missing value for ' + token);
      opts[token.slice(2) === 'agent' ? 'agent' : 'dir'] = rest[++i];
    } else if (token === '--help' || token === '-h') opts.command = 'help';
    else if (token.startsWith('-')) fail('Unknown option: ' + token);
    else opts.names.push(token);
  }
  if (opts.command !== 'install' && (
    opts.names.length || opts.all || opts.global || opts.force || opts.dryRun ||
    opts.dir || opts.agent !== 'codex'
  )) fail('Options/skill names are only supported with autosci install.');
  return opts;
}

function verify(skills) {
  if (!skills.length) fail('No SKILL.md files were found.');
  for (const name of skills) {
    const content = readFileSync(join(skillsRoot, name, 'SKILL.md'), 'utf8');
    const fm = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(content);
    if (!fm ||
      !new RegExp("^name:\\s*['\"]?" + name + "['\"]?\\s*$", 'm').test(fm[1]) ||
      !/^description:\s*(?:\S.*|[>|]-?\s*)$/m.test(fm[1])) {
      fail('Invalid SKILL.md frontmatter: skills/' + name + '/SKILL.md');
    }
  }
}

function isBrokenSymlink(path) {
  try { return lstatSync(path).isSymbolicLink(); }
  catch (err) { if (err.code === 'ENOENT') return false; throw err; }
}

function copySkill(name, outputDir, force, dryRun) {
  const source = join(skillsRoot, name);
  const destination = join(outputDir, name);
  if ((existsSync(destination) || isBrokenSymlink(destination)) && !force) {
    fail('Already exists: ' + destination + '. Use --force to replace it.');
  }
  if (dryRun) {
    console.log('Would install ' + name + ' -> ' + destination);
    return;
  }
  mkdirSync(outputDir, { recursive: true });
  const stage = join(outputDir, '.autosci-stage-' + randomUUID());
  const backup = join(outputDir, '.autosci-backup-' + randomUUID());
  let hadBackup = false;
  try {
    cpSync(source, stage, { recursive: true, force: false, errorOnExist: true });
    if (existsSync(destination) || isBrokenSymlink(destination)) {
      renameSync(destination, backup);
      hadBackup = true;
    }
    renameSync(stage, destination);
    if (hadBackup) rmSync(backup, { recursive: true, force: true });
  } catch (err) {
    if (existsSync(stage)) rmSync(stage, { recursive: true, force: true });
    if (hadBackup && !existsSync(destination) && !isBrokenSymlink(destination)) {
      renameSync(backup, destination);
    }
    throw err;
  }
  console.log('Installed ' + name + ' -> ' + destination);
}

function usage() {
  console.log(`AutoSCI — install the research Skills included in this package

Usage:
  autosci list
  autosci verify
  autosci install --all [--global] [--agent codex|claude-code|cursor]
  autosci install <skill> [<skill> ...] [--global] [--force]
  autosci install <skill> --dir <path> [--force] [--dry-run]

Default: local Codex project directory .agents/skills/.
--global: user directory (~/.codex/skills for Codex, respecting CODEX_HOME).
--dir: override the destination. --force: replace existing directories, including edits.
The installer only copies files. It never runs the skills' Python scripts.`);
}

export function main(argv = process.argv.slice(2)) {
  const opts = parseArgs(argv);
  if (opts.command === 'help') return usage();
  const skills = discoverSkills();
  if (opts.command === 'list') { skills.forEach((name) => console.log(name)); return; }
  verify(skills);
  if (opts.command === 'verify') { console.log('Verified ' + skills.length + ' skills.'); return; }
  if (!supportedAgents.includes(opts.agent) && opts.dir === null) {
    fail('Unsupported agent: ' + opts.agent + '. Use ' + supportedAgents.join(', ') + ', or --dir PATH.');
  }
  if (opts.all === (opts.names.length > 0)) {
    fail('Specify either --all or one or more skill names.');
  }
  const requested = opts.all ? skills : [...new Set(opts.names)];
  for (const name of requested) {
    if (!skills.includes(name)) fail('Unknown skill: ' + name + '. Run autosci list.');
  }
  const destination = opts.dir === null ? destinationFor(opts.agent, opts.global) : resolve(opts.dir);
  // Validate the entire batch before writes to prevent partial installations on collision.
  if (!opts.force) {
    for (const name of requested) {
      const dest = join(destination, name);
      if (existsSync(dest) || isBrokenSymlink(dest)) {
        fail('Already exists: ' + dest + '. Use --force to replace it.');
      }
    }
  }
  for (const name of requested) copySkill(name, destination, opts.force, opts.dryRun);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  try { main(); }
  catch (error) { console.error('AutoSCI: ' + error.message); process.exitCode = 1; }
}
