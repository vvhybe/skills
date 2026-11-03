// Regression tests for skills/site-upgrade/scripts/slop-scan.mjs. Run: node --test tests/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const scanner = join(here, '..', 'skills', 'site-upgrade', 'scripts', 'slop-scan.mjs');
const scan = (fixture, ...flags) => {
  const run = spawnSync(process.execPath, [scanner, join(here, 'fixtures', fixture), '--json', ...flags], { encoding: 'utf8' });
  return { status: run.status, report: JSON.parse(run.stdout) };
};
const rules = (report) => new Set(report.findings.map((f) => f.rule));

test('the generated-looking page fails with errors', () => {
  const { status, report } = scan('sloppy-site');
  assert.equal(status, 1);
  assert.ok(report.errors >= 3, `expected errors, got ${report.errors}`);
});

test('invented proof, placeholders and fake people are errors', () => {
  const { report } = scan('sloppy-site');
  for (const rule of ['invented-proof', 'placeholder', 'fake-people']) {
    const finding = report.findings.find((f) => f.rule === rule);
    assert.ok(finding, `missing ${rule}`);
    assert.equal(finding.severity, 'error');
  }
});

test('visual, copy and motion tells are found', () => {
  const found = rules(scan('sloppy-site').report);
  for (const rule of [
    'gradient-text', 'violet-gradient', 'glow', 'glass', 'eyebrow', 'emoji-icon', 'genre-copy', 'vague-cta',
    'not-just', 'middot-meta', 'dead-link', 'img-no-alt', 'bounce-ease', 'layout-tween', 'unsourced-uptime',
    'reduced-motion',
  ]) assert.ok(found.has(rule), `missing ${rule}`);
});

test('earned exceptions pass and are reported, not hidden', () => {
  const { status, report } = scan('earned-site');
  assert.equal(status, 0);
  assert.equal(report.findings.length, 0, JSON.stringify(report.findings, null, 2));
  const glass = report.allowed.find((a) => a.rule === 'glass');
  assert.ok(glass, 'the repo-level exception is listed');
  assert.match(glass.reason, /signature/);
});

test('--allow silences a rule for one run and lists it', () => {
  const { report } = scan('sloppy-site', '--allow', 'genre-copy');
  assert.ok(!rules(report).has('genre-copy'));
  assert.ok(report.allowed.some((a) => a.rule === 'genre-copy'));
});

test('--strict fails on warnings alone', () => {
  const { status } = scan('earned-site', '--strict');
  assert.equal(status, 0); // nothing left to warn about
  const run = spawnSync(process.execPath, [scanner, join(here, 'fixtures', 'sloppy-site'), '--strict'], { encoding: 'utf8' });
  assert.equal(run.status, 1);
});

test('--list-rules prints every rule', () => {
  const out = execFileSync(process.execPath, [scanner, '--list-rules'], { encoding: 'utf8' });
  assert.match(out, /invented-proof/);
  assert.match(out, /env-committed/);
});
