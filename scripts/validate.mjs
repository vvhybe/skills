#!/usr/bin/env node
// Validates every skill in skills/: frontmatter, size, relative links, and that bundled scripts parse.
// Zero dependencies. Run: node scripts/validate.mjs
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join, dirname, extname, relative } from 'node:path';
import { spawnSync } from 'node:child_process';
import { Script } from 'node:vm';
import { fileURLToPath } from 'node:url';

const repo = join(dirname(fileURLToPath(import.meta.url)), '..');
const skillsDir = join(repo, 'skills');
let failures = 0;
const fail = (msg) => {
  failures++;
  console.error(`✗ ${msg}`);
};
const ok = (msg) => console.log(`✓ ${msg}`);

const walk = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(dir, e.name)) : [join(dir, e.name)]));

const frontmatter = (text) => {
  const m = text.match(/^---\n([\s\S]*?)\n---\n/);
  if (!m) return null;
  const fields = {};
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([a-z][\w-]*):\s?(.*)$/);
    if (kv) fields[kv[1]] = kv[2].trim();
  }
  return fields;
};

for (const name of readdirSync(skillsDir)) {
  const dir = join(skillsDir, name);
  if (!statSync(dir).isDirectory()) continue;
  const skillFile = join(dir, 'SKILL.md');
  if (!existsSync(skillFile)) {
    fail(`${name}: no SKILL.md`);
    continue;
  }
  const text = readFileSync(skillFile, 'utf8');
  const fm = frontmatter(text);
  if (!fm) {
    fail(`${name}: SKILL.md has no frontmatter`);
    continue;
  }
  if (fm.name !== name) fail(`${name}: frontmatter name "${fm.name}" must match the folder`);
  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(fm.name ?? '') || fm.name.length > 64) fail(`${name}: name must be kebab-case, at most 64 characters`);
  if (!fm.description) fail(`${name}: description is missing`);
  else {
    if (fm.description.length > 1024) fail(`${name}: description is ${fm.description.length} characters (max 1024)`);
    if (/[<>]/.test(fm.description)) fail(`${name}: description must not contain angle brackets`);
    if (!/\bUse (it )?when\b/i.test(fm.description)) fail(`${name}: description should say when to use the skill ("Use when …")`);
  }
  const lines = text.split('\n').length;
  if (lines > 500) fail(`${name}: SKILL.md is ${lines} lines (keep it under 500; move detail into references/)`);
  else ok(`${name}: frontmatter ok, SKILL.md ${lines} lines`);

  // Relative links in every Markdown file resolve
  let links = 0;
  // templates hold placeholder links like (01-<slug>.md); they are filled in per project
  for (const file of walk(dir).filter((f) => extname(f) === '.md' && !f.includes('/assets/templates/'))) {
    const md = readFileSync(file, 'utf8').replace(/```[\s\S]*?```/g, '').replace(/`[^`\n]*`/g, '');
    for (const [, target] of md.matchAll(/\]\(([^)\s]+)\)/g)) {
      if (/^(https?:|mailto:|#)/.test(target)) continue;
      const path = target.split('#')[0];
      if (!path) continue;
      links++;
      if (!existsSync(join(dirname(file), path))) fail(`${relative(repo, file)}: broken link → ${target}`);
    }
  }
  ok(`${name}: ${links} relative links checked`);

  // Bundled scripts parse
  for (const file of walk(dir)) {
    const rel = relative(repo, file);
    const ext = extname(file);
    let run = null;
    if (ext === '.mjs' || ext === '.cjs' || (ext === '.js' && !file.includes('/playwright/'))) run = spawnSync(process.execPath, ['--check', file], { encoding: 'utf8' });
    else if (ext === '.py') run = spawnSync('python3', ['-c', 'import ast, sys; ast.parse(open(sys.argv[1]).read(), sys.argv[1])', file], { encoding: 'utf8' });
    else if (ext === '.js') {
      // Playwright MCP wraps the file as `await (<file>)(page)`: it must be one function expression.
      // vm.Script only compiles the source; nothing runs.
      const source = readFileSync(file, 'utf8');
      try {
        new Script(`(${source})`, { filename: rel });
        if (/;\s*$/.test(source.trim())) fail(`${rel}: Playwright scripts must not end with ";"`);
      } catch (e) {
        fail(`${rel}: does not parse as one function expression (${e.message})`);
      }
      continue;
    } else if (ext === '.sh') run = spawnSync('bash', ['-n', file], { encoding: 'utf8' });
    if (run && run.status !== 0) fail(`${rel}: ${run.stderr.trim().split('\n')[0]}`);
  }
  ok(`${name}: scripts parse`);
}

// The marketplace manifest points at real skills
const manifest = join(repo, '.claude-plugin', 'marketplace.json');
if (existsSync(manifest)) {
  const data = JSON.parse(readFileSync(manifest, 'utf8'));
  for (const plugin of data.plugins ?? []) for (const s of plugin.skills ?? []) if (!existsSync(join(repo, s, 'SKILL.md'))) fail(`marketplace: ${plugin.name} → ${s} has no SKILL.md`);
  ok('marketplace.json points at existing skills');
}

if (failures) {
  console.error(`\n${failures} problem(s)`);
  process.exit(1);
}
console.log('\nall checks pass');
