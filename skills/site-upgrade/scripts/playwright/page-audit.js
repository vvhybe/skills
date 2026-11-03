// Measures the frame of the current page at the current viewport: one <h1>, headings over two
// lines, small text, small tap targets (phone widths), unnamed controls, images without alt,
// sections without a heading, document basics and whether browser surfaces are themed.
// Real product fragments and documents (an invoice, an app screen built in HTML) keep their own
// conventions: mark their root with `data-ui` and the type and tap-target checks skip them.
// Run it at 1440 and again at 390. Pass as the `filename` of browser_run_code_unsafe.
async (page) => {
  return await page.evaluate(() => {
    const visible = (el) => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return false;
      for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
        const s = getComputedStyle(n);
        if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false;
      }
      return true;
    };
    const srOnly = (el) => {
      const s = getComputedStyle(el);
      return s.position === 'absolute' && (s.clip === 'rect(0px, 0px, 0px, 0px)' || s.clipPath === 'inset(50%)' || el.getBoundingClientRect().width <= 1);
    };
    const label = (el) => {
      const tag = el.tagName.toLowerCase();
      const cls = typeof el.className === 'string' ? el.className.trim().split(/\s+/).slice(0, 3).join('.') : '';
      const text = (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40);
      return `${tag}${el.id ? '#' + el.id : ''}${cls ? '.' + cls : ''}${text ? ` "${text}"` : ''}`;
    };
    const lineCount = (el) => {
      const range = document.createRange();
      range.selectNodeContents(el);
      const tops = new Set();
      for (const r of range.getClientRects()) if (r.width > 1 && r.height > 1) tops.add(Math.round(r.top / 4));
      return tops.size;
    };
    const accessibleName = (el) =>
      (el.getAttribute('aria-label') || '').trim() ||
      (el.getAttribute('aria-labelledby') || '').trim() ||
      (el.getAttribute('title') || '').trim() ||
      (el.textContent || '').trim() ||
      [...el.querySelectorAll('img[alt], svg title, [aria-label]')].map((n) => n.getAttribute('alt') || n.getAttribute('aria-label') || n.textContent).join('').trim();

    const width = window.innerWidth;
    const phone = width <= 500;
    const report = { url: location.pathname, width, problems: [], notes: [] };
    const problem = (check, detail) => report.problems.push({ check, detail });

    // Document basics
    if (!document.documentElement.lang) problem('html-lang', '<html> has no lang attribute');
    if (!document.title.trim()) problem('title', 'no <title>');
    if (!document.querySelector('meta[name="description"]')) problem('meta-description', 'no meta description');
    if (!document.querySelector('meta[name="viewport"]')) problem('viewport', 'no viewport meta');
    if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)
      problem('overflow-x', `page scrolls sideways by ${document.documentElement.scrollWidth - document.documentElement.clientWidth}px (run overflow.js)`);

    // One h1
    const h1s = [...document.querySelectorAll('h1')].filter(visible);
    if (h1s.length !== 1) problem('h1-count', `${h1s.length} visible <h1> (${h1s.map((h) => `"${h.textContent.trim().slice(0, 30)}"`).join(', ')})`);

    // Headings within two lines
    for (const h of [...document.querySelectorAll('h1, h2, h3')].filter((h) => visible(h) && !h.closest('[data-ui]'))) {
      const lines = lineCount(h);
      if (lines > 2) problem('heading-lines', `${lines} lines: ${label(h)}`);
    }

    // Small text
    const small = new Map();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const el = node.parentElement;
      if (!el || !node.textContent.trim() || small.has(el)) continue;
      if (el.closest('svg, script, style, noscript, [aria-hidden="true"], [data-ui]')) continue;
      const size = parseFloat(getComputedStyle(el).fontSize);
      if (size < 12 && visible(el) && !srOnly(el)) small.set(el, size);
    }
    if (small.size) problem('small-text', `${small.size} element(s) under 12px, e.g. ${[...small].slice(0, 5).map(([el, s]) => `${s}px ${label(el)}`).join('; ')}`);

    // Tap targets on phones
    if (phone) {
      const tiny = [];
      for (const el of document.querySelectorAll('a[href], button, [role="button"], input:not([type="hidden"]), select, textarea, summary')) {
        if (!visible(el) || srOnly(el) || el.closest('[data-ui]')) continue;
        const r = el.getBoundingClientRect();
        // inline links inside running text are exempt (WCAG 2.5.8)
        const block = el.closest('p, li, dd, td, figcaption, blockquote');
        if (el.tagName === 'A' && block && (block.textContent || '').trim().length > (el.textContent || '').trim().length + 20) continue;
        // text links need 24px (WCAG 2.5.8); buttons, icons and fields need 40px to be comfortable
        const textLink = el.tagName === 'A' && (el.textContent || '').trim().length > 3;
        const min = textLink ? 24 : 40;
        if (r.width >= min && r.height >= min) continue;
        tiny.push(`${Math.round(r.width)}×${Math.round(r.height)} ${label(el)}`);
      }
      if (tiny.length) problem('tap-targets', `${tiny.length} control(s) too small to tap (text links < 24px, others < 40px), e.g. ${tiny.slice(0, 6).join('; ')}`);
    }

    // Controls without a name, images without alt
    const unnamed = [...document.querySelectorAll('a[href], button, [role="button"]')].filter((el) => visible(el) && !accessibleName(el));
    if (unnamed.length) problem('unnamed-controls', `${unnamed.length}: ${unnamed.slice(0, 5).map(label).join('; ')}`);
    const noAlt = [...document.querySelectorAll('img:not([alt])')].filter(visible);
    if (noAlt.length) problem('img-alt', `${noAlt.length} image(s) without alt: ${noAlt.slice(0, 4).map((i) => i.currentSrc.split('/').pop()).join(', ')}`);

    // Sections without a heading
    const untitled = [...document.querySelectorAll('main section, main > article')]
      .filter((s) => visible(s) && !s.querySelector('h1, h2, h3, h4, h5, h6, [role="heading"]') && (s.textContent || '').trim().length > 80)
      .filter((s, _, all) => !all.some((o) => o !== s && o.contains(s)));
    if (untitled.length) problem('untitled-sections', `${untitled.length} section(s) with text but no heading: ${untitled.slice(0, 4).map(label).join('; ')}`);
    if (!document.querySelector('main')) problem('main', 'no <main> landmark');
    if (!document.querySelector('a[href="#main"], a[href="#content"], a[href^="#main"]')) report.notes.push('no skip link to #main found');

    // Browser surfaces (the cheapest signal of a built site)
    const surfaces = { selection: false, scrollbar: false, caret: false, accent: false, focusVisible: false, tabularNums: false };
    for (const sheet of document.styleSheets) {
      let rules;
      try { rules = sheet.cssRules; } catch { continue; }
      const scan = (list) => {
        for (const rule of list) {
          const text = rule.cssText || '';
          if (/::selection/.test(text)) surfaces.selection = true;
          if (/scrollbar-color|::-webkit-scrollbar/.test(text)) surfaces.scrollbar = true;
          if (/caret-color/.test(text)) surfaces.caret = true;
          if (/accent-color/.test(text)) surfaces.accent = true;
          if (/:focus-visible/.test(text)) surfaces.focusVisible = true;
          if (/tabular-nums/.test(text)) surfaces.tabularNums = true;
          if (rule.cssRules) scan(rule.cssRules);
        }
      };
      scan(rules);
    }
    const unthemed = Object.entries(surfaces).filter(([, ok]) => !ok).map(([k]) => k);
    if (unthemed.length) report.notes.push(`browser surfaces not themed: ${unthemed.join(', ')}`);

    report.summary = report.problems.length ? `${report.problems.length} problem(s)` : 'frame checks pass';
    return report;
  });
}
