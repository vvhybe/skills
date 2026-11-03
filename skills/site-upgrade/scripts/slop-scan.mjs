#!/usr/bin/env node
// slop-scan: finds generated-site tells, invented proof, genre copy, dead links and known traps in a
// website's source. See references/tells.md for the reasoning behind each rule.
//
//   node slop-scan.mjs [dir=.] [--json] [--strict] [--allow rule1,rule2]
//
// Earned exceptions are named, never silent:
//   - on a block: a comment containing `site-upgrade-allow: <rule> <reason>` covers its own line and the
//     lines after it, up to the next blank line
//   - for the whole repo: a `.site-upgrade-allow` file at the root, one `<rule> <reason>` per line
//   - for one run: --allow <rule,rule>
// Exit codes: 0 clean or warnings only, 1 errors (or warnings with --strict), 2 bad usage.
// Node 18+, no dependencies. Reads files only; never runs project code.

import { execFileSync } from 'node:child_process';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, extname, basename, resolve } from 'node:path';

const args = process.argv.slice(2);
if (args.includes('-h') || args.includes('--help')) {
  console.log('usage: node slop-scan.mjs [dir=.] [--json] [--strict] [--allow rule1,rule2] [--list-rules]');
  process.exit(0);
}
const json = args.includes('--json');
const strict = args.includes('--strict');
const allowIndex = args.indexOf('--allow');
const cliAllow = allowIndex >= 0 ? (args[allowIndex + 1] ?? '').split(',').filter(Boolean) : [];
const positional = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--allow');
const root = resolve(positional[0] ?? '.');
if (!existsSync(root) || !statSync(root).isDirectory()) {
  console.error(`slop-scan: not a directory: ${root}`);
  process.exit(2);
}

// ---------- files ----------

const CODE = new Set(['.tsx', '.jsx', '.ts', '.js', '.mjs', '.cjs', '.html', '.vue', '.svelte', '.astro']);
const STYLE = new Set(['.css', '.scss', '.sass', '.less']);
const PROSE = new Set(['.md', '.mdx', '.json', '.yml', '.yaml']);
const SKIP_DIRS = new Set([
  'node_modules', '.git', '.next', 'out', 'dist', 'build', '.vercel', '.turbo', '.svelte-kit', '.astro',
  '.output', 'coverage', '.playwright-mcp', '.wrangler', 'vendor', '.cache', '.taste-skill', '.impeccable',
]);
const SKIP_FILES = /(^|\/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lockb?|CHANGELOG\.md|LICENSE.*)$|\.min\.(js|css)$|\.d\.ts$/;

const listFiles = () => {
  try {
    // core.fsmonitor=false: a scanned repo's own .git/config must never get to run a program
    const out = execFileSync('git', ['-c', 'core.fsmonitor=false', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], {
      cwd: root,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      maxBuffer: 64 * 1024 * 1024,
    });
    return { files: out.split('\0').filter(Boolean), git: true };
  } catch {
    const files = [];
    const walk = (dir) => {
      for (const entry of readdirSync(dir, { withFileTypes: true })) {
        if (entry.isDirectory()) {
          if (!SKIP_DIRS.has(entry.name)) walk(join(dir, entry.name));
        } else files.push(relative(root, join(dir, entry.name)));
      }
    };
    walk(root);
    return { files, git: false };
  }
};

const { files: allFiles, git } = listFiles();
const files = allFiles.filter((f) => {
  if (f.split('/').some((part) => SKIP_DIRS.has(part))) return false;
  if (SKIP_FILES.test(f)) return false;
  const ext = extname(f).toLowerCase();
  return CODE.has(ext) || STYLE.has(ext) || PROSE.has(ext);
});

// ---------- rules ----------
// kinds: code (markup and scripts), style, prose (md/json/yaml). `min`: report only from that many hits.

const CODE_KINDS = ['code'];
const VISUAL_KINDS = ['code', 'style'];
const COPY_KINDS = ['code', 'prose'];

const rules = [
  // Palette and surface
  { id: 'gradient-text', severity: 'warn', kinds: VISUAL_KINDS, title: 'Gradient-filled text',
    re: /bg-clip-text[^"'`]*text-transparent|text-transparent[^"'`]*bg-clip-text|(-webkit-)?background-clip:\s*text/,
    hint: 'Solid ink; emphasis from size or weight.' },
  { id: 'violet-gradient', severity: 'warn', kinds: VISUAL_KINDS, title: 'Indigo/violet gradient (the first-wave generated look)',
    re: /bg-(gradient|linear)-to-\w+[^"'`]*(from|via|to)-(indigo|violet|purple|fuchsia)-\d|linear-gradient\([^)]*(#6366f1|#8b5cf6|#7c3aed|#a855f7|#4f46e5|#9333ea)/i,
    hint: 'The brand\'s sampled palette, mostly flat. If indigo IS the brand, allow it with a reason.' },
  { id: 'glow', severity: 'warn', kinds: VISUAL_KINDS, title: 'Zero-offset colored glow',
    re: /shadow-\[0_0_\d+px|box-shadow:\s*0(px)?\s+0(px)?\s+\d+px/,
    hint: 'Depth from a tone step, or a shadow with an offset on what truly floats.' },
  { id: 'glass', severity: 'warn', kinds: VISUAL_KINDS, min: 3, title: 'Glass and backdrop blur used repeatedly',
    re: /backdrop-blur(-(sm|md|lg|xl|2xl|3xl))?\b|backdrop-filter:\s*blur/,
    hint: 'Opaque surfaces one tone step from the ground; blur only for one specific effect.' },
  { id: 'eyebrow', severity: 'warn', kinds: CODE_KINDS, title: 'Tiny tracked uppercase label (an eyebrow?)',
    test: (l) => !/<(th|dt)\b/.test(l) && /\buppercase\b/.test(l) && /\btracking-(wide|wider|widest|\[0?\.\d+em\])/.test(l) && /\btext-(xs|\[(9|10|11|12)px\]|\[0?\.(6|7)\d*rem\])/.test(l),
    hint: 'Fold it into the heading or delete it. Keep only where it carries real structure.' },
  { id: 'numbered-sections', severity: 'warn', kinds: CODE_KINDS, min: 3, title: '01 / 02 / 03 numbering',
    re: />\s*\(?0[1-9]\)?\s*[./]?\s*</,
    hint: 'Order by position, scale or the words; a real <ol> when it is a list. Allow when the sequence is the content.' },
  { id: 'emoji-icon', severity: 'warn', kinds: CODE_KINDS, min: 3, title: 'Emoji used as icons or bullets',
    re: /[\u{1F300}-\u{1FAFF}\u{2728}\u{26A1}\u{2705}\u{274C}]/u, commentsCount: false,
    hint: 'One drawn icon library, one stroke and weight; the product\'s own set when it has one.' },
  { id: 'decorative-pulse', severity: 'warn', kinds: CODE_KINDS, title: 'Pulsing or bouncing decoration',
    re: /\banimate-(ping|bounce)\b/,
    hint: 'Motion that answers the visitor; no "live" dots that mean nothing.' },
  { id: 'transition-all', severity: 'warn', kinds: VISUAL_KINDS, title: 'transition: all',
    re: /\btransition-all\b|transition:\s*all\b/,
    hint: 'Transition the properties that change (transform, opacity, colors).' },
  { id: 'layout-tween', severity: 'warn', kinds: CODE_KINDS, title: 'Animating layout properties',
    re: /gsap\.(to|from|fromTo)\([^)]*\b(top|left|width|height)\s*:/,
    hint: 'Animate transform and opacity; layout properties jank.' },
  { id: 'bounce-ease', severity: 'warn', kinds: [...CODE_KINDS, 'style'], title: 'Bounce or elastic easing',
    re: /\b(bounce|elastic)\.(out|in|inOut)\b|ease:\s*['"](bounce|elastic)/,
    hint: 'Exponential ease-out for entrances, power4.in for impacts.' },

  // Copy and proof
  { id: 'invented-proof', severity: 'error', kinds: COPY_KINDS, title: 'Social proof that needs a source',
    re: /\b(join|trusted by|loved by|used by|chosen by)\s+(over\s+|more than\s+)?(thousands|millions|hundreds|\d[\d,.]*\s*k?\+?)\b|\b\d{1,3}(,\d{3})+\+?\s+(happy\s+)?(users|customers|teams|companies|businesses)\b|\b\d+k\+\s+(users|customers|teams)\b|(^|[\s"'>])#1(\s|$)|★★★★★|⭐{3,}|\b(4\.\d|5\.0)\s*(\/\s*5|out of 5|stars?)\b/i,
    hint: 'Real proof with a source in the claims ledger, or none.' },
  { id: 'fake-people', severity: 'error', kinds: COPY_KINDS, title: 'Placeholder people or companies',
    re: /\b(John|Jane)\s+Doe\b|\bAcme\s+(Inc|Corp|Co)\b|\bLorem Corp\b/,
    hint: 'No testimonials until real ones exist.' },
  { id: 'unsourced-uptime', severity: 'warn', kinds: COPY_KINDS, title: 'Uptime or SLA figure',
    re: /\b99\.9+\s*%|\b100\s*%\s*uptime\b/i,
    hint: 'Only with a signed-off source; otherwise remove and make the figure optional.' },
  { id: 'placeholder', severity: 'error', kinds: COPY_KINDS, title: 'Placeholder content',
    re: /lorem ipsum|dolor sit amet|\bimage here\b|via\.placeholder\.com|placehold\.co\/|picsum\.photos|\bTODO:?\s*(copy|text|image)\b/i,
    hint: 'Real content, or the section waits.' },
  { id: 'genre-copy', severity: 'warn', kinds: COPY_KINDS, title: 'Genre copy',
    re: /\b(unlock(s|ing)? (your|the power|new levels|growth|potential)|supercharg(e|es|ed|ing)|seamless(ly)?|elevate(s|d)?|effortless(ly)?|cutting[- ]edge|all-in-one|all in one (app|platform|solution|tool|place|workspace)|revolutioni[sz](e|es|ing)|game[- ]chang(er|ing)|next[- ]level|world[- ]class|best[- ]in[- ]class|empower(s|ing)?|harness the power|look no further|in today'?s fast[- ]paced)\b/i,
    hint: 'Plain verbs about what actually happens.' },
  { id: 'vague-cta', severity: 'warn', kinds: COPY_KINDS, title: 'Vague call to action',
    re: />\s*(Get started|Learn more|Click here|Read more)\s*</i,
    alt: /["'`](Get started|Learn more|Click here)["'`]/i,
    hint: 'Name what happens: "Download on the App Store", "Book a 30-minute call".' },
  { id: 'not-just', severity: 'warn', kinds: COPY_KINDS, title: '"Not just X, it\'s Y"',
    re: /\bnot just (a|an|another|your)\b[^.]{0,60}\b(it'?s|we'?re|but)\b/i,
    hint: 'One concrete claim.' },
  { id: 'middot-meta', severity: 'warn', kinds: COPY_KINDS, title: 'Middle-dot meta string',
    re: /[A-Za-z]{3,}\s+·\s+[A-Za-z]{3,}\s+·\s+[A-Za-z]{3,}/,
    hint: 'Write a sentence.' },

  // Links, markup and traps
  { id: 'dead-link', severity: 'warn', kinds: CODE_KINDS, title: 'Dead or template link',
    re: /href=\{?["']#["']\}?|href=\{?["']\/?[a-z]+-0\d["'/]/,
    hint: 'Link to the real destination or remove the element.' },
  { id: 'img-no-alt', severity: 'warn', kinds: CODE_KINDS, title: 'Image without alt',
    re: /<(img|Image)\b(?![^>]*\balt\s*=)[^>]*\/?>/,
    hint: 'Describe the image, or alt="" when it is decorative.' },
  { id: 'clarity-id', severity: 'error', kinds: CODE_KINDS, title: 'id="clarity" breaks Microsoft Clarity',
    re: /\bid=\{?["']clarity["']/,
    hint: 'Element ids become window properties; Clarity never installs. Use another id.' },
  { id: 'search-params-layout', severity: 'warn', kinds: CODE_KINDS, title: 'useSearchParams in a layout',
    re: /\buseSearchParams\s*\(/, fileTest: (f) => /(^|\/)layout\.(t|j)sx?$/.test(f),
    hint: 'It can force every page to render on the client. Move it into a leaf component.' },
  { id: 'boolean-env', severity: 'warn', kinds: CODE_KINDS, title: 'Boolean env switch',
    re: /\b(process\.env|import\.meta\.env)\.\w*_(LIVE|ENABLED|ON|TOGGLE)\b/,
    hint: 'Configuration holds values (a URL, an ID); empty means off.' },
  { id: 'secret', severity: 'error', kinds: [...CODE_KINDS, 'prose', 'style'], title: 'Possible secret in source',
    re: /\b(sk_live_[A-Za-z0-9]{10,}|rk_live_[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|xox[baprs]-[A-Za-z0-9-]{10,})|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----/,
    hint: 'Remove it, rotate it, and keep it in the host\'s secret store.' },
];

if (args.includes('--list-rules')) {
  for (const r of rules) console.log(`${r.severity.padEnd(5)} ${r.id.padEnd(22)} ${r.title}`);
  console.log('error env-committed          Env file tracked by git');
  console.log('warn  reduced-motion         Motion without any prefers-reduced-motion handling');
  process.exit(0);
}

const kindOf = (file) => {
  const ext = extname(file).toLowerCase();
  if (CODE.has(ext)) return 'code';
  if (STYLE.has(ext)) return 'style';
  return 'prose';
};

// ---------- allow list ----------

const allowed = new Map(); // rule -> reason
for (const id of cliAllow) allowed.set(id, 'allowed with --allow');
const allowFile = join(root, '.site-upgrade-allow');
if (existsSync(allowFile)) {
  for (const raw of readFileSync(allowFile, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const [id, ...reason] = line.split(/\s+/);
    allowed.set(id, reason.join(' ') || '(no reason given: add one)');
  }
}
const allowsIn = (line) => {
  const m = line.match(/site-upgrade-allow:\s*([\w,-]+)/);
  return m ? m[1].split(',') : [];
};

// ---------- scan ----------

const isComment = (trimmed) => /^(\/\/|\/\*|\*|\{\s*\/\*|<!--)/.test(trimmed);
const excerpt = (line, index) => {
  const text = line.replace(/\s+/g, ' ').trim();
  if (text.length <= 110) return text;
  const at = Math.max(0, Math.min(text.length - 110, (index ?? 0) - 40));
  return (at > 0 ? '…' : '') + text.slice(at, at + 110) + (at + 110 < text.length ? '…' : '');
};

const hits = new Map(rules.map((r) => [r.id, []]));
let motionUsed = null;
let reducedMotionHandled = false;
const envFiles = [];

for (const file of files) {
  let text;
  try {
    if (statSync(join(root, file)).size > 768 * 1024) continue;
    text = readFileSync(join(root, file), 'utf8');
  } catch {
    continue;
  }
  const kind = kindOf(file);
  if (!motionUsed && /\b(from ['"](gsap|framer-motion|motion\/react|lenis)['"]|@keyframes|animation-timeline)/.test(text)) motionUsed = file;
  if (/prefers-reduced-motion|useReducedMotion|motion-reduce:|reducedMotion/.test(text)) reducedMotionHandled = true;

  const lines = text.split('\n');
  let fenced = false;
  let blockAllows = new Set(); // from a site-upgrade-allow comment, until the next blank line
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (/^(```|~~~)/.test(trimmed)) fenced = !fenced;
    if (fenced && kind === 'prose') continue;
    if (!trimmed) {
      blockAllows = new Set();
      continue;
    }
    for (const id of allowsIn(line)) blockAllows.add(id);
    if (trimmed.length > 4000) continue;
    const comment = kind !== 'prose' && isComment(trimmed);
    const importLine = /^(import|export \* from|export \{[^}]*\} from)\s/.test(trimmed);
    for (const rule of rules) {
      if (!rule.kinds.includes(kind)) continue;
      if (rule.fileTest && !rule.fileTest(file)) continue;
      if ((comment && rule.id !== 'secret') || (importLine && rule.id !== 'secret')) continue;
      let match = null;
      if (rule.test) match = rule.test(line) ? { index: 0 } : null;
      else match = line.match(rule.re) ?? (rule.alt && kind === 'code' ? line.match(rule.alt) : null);
      if (!match) continue;
      if (blockAllows.has(rule.id) || blockAllows.has('all')) continue;
      hits.get(rule.id).push({ file, line: i + 1, excerpt: excerpt(line, match.index) });
    }
  }
}

if (git) {
  try {
    const tracked = execFileSync('git', ['-c', 'core.fsmonitor=false', 'ls-files', '-z'], { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })
      .split('\0')
      .filter(Boolean);
    for (const f of tracked) {
      const name = basename(f);
      if (/^\.env(\..+)?$/.test(name) && !/\.(example|sample|template)$/.test(name)) envFiles.push(f);
    }
  } catch {
    /* not a git work tree */
  }
}

// ---------- report ----------

const findings = [];
const allowedReport = [];
for (const rule of rules) {
  const list = hits.get(rule.id);
  if (!list.length) continue;
  if (rule.min && list.length < rule.min) continue;
  if (allowed.has(rule.id)) {
    allowedReport.push({ rule: rule.id, count: list.length, reason: allowed.get(rule.id) });
    continue;
  }
  findings.push({ rule: rule.id, severity: rule.severity, title: rule.title, hint: rule.hint, hits: list });
}
if (envFiles.length && !allowed.has('env-committed')) {
  findings.push({
    rule: 'env-committed', severity: 'error', title: 'Env file tracked by git', hint: 'Commit only .env.example; git-ignore .env*.',
    hits: envFiles.map((f) => ({ file: f, line: 1, excerpt: f })),
  });
}
if (motionUsed && !reducedMotionHandled && !allowed.has('reduced-motion')) {
  findings.push({
    rule: 'reduced-motion', severity: 'warn', title: 'Motion without any prefers-reduced-motion handling',
    hint: 'Show final states under reduced motion (references/motion.md § 5).',
    hits: [{ file: motionUsed, line: 1, excerpt: 'motion library or keyframes used; no reduced-motion handling found anywhere' }],
  });
}

const order = { error: 0, warn: 1 };
findings.sort((a, b) => order[a.severity] - order[b.severity] || b.hits.length - a.hits.length);
const errors = findings.filter((f) => f.severity === 'error').reduce((n, f) => n + f.hits.length, 0);
const warnings = findings.filter((f) => f.severity === 'warn').reduce((n, f) => n + f.hits.length, 0);

if (json) {
  console.log(JSON.stringify({ root, files: files.length, errors, warnings, findings, allowed: allowedReport }, null, 2));
} else {
  const MAX = 8;
  console.log(`slop-scan: ${files.length} files in ${positional[0] ?? '.'}: ${errors} error(s), ${warnings} warning(s)\n`);
  for (const f of findings) {
    console.log(`${f.severity === 'error' ? 'ERROR' : 'WARN '} ${f.rule}  ${f.title} (${f.hits.length})`);
    for (const h of f.hits.slice(0, MAX)) console.log(`  ${h.file}:${h.line}  ${h.excerpt}`);
    if (f.hits.length > MAX) console.log(`  … and ${f.hits.length - MAX} more`);
    console.log(`  → ${f.hint}\n`);
  }
  if (allowedReport.length) {
    console.log('Allowed (earned exceptions):');
    for (const a of allowedReport) console.log(`  ${a.rule} (${a.count}): ${a.reason}`);
    console.log('');
  }
  if (!findings.length) console.log('No tells found. That is the floor, not the goal: the critique decides if it is good.');
  else console.log('Fix each finding, or name it as an earned exception: `site-upgrade-allow: <rule> <reason>`.');
}

process.exit(errors > 0 || (strict && warnings > 0) ? 1 : 0);
