// Checks the current page for horizontal overflow at phone-to-desktop widths and names the culprits.
// Pass as the `filename` of browser_run_code_unsafe. Restores the original viewport afterwards.
async (page) => {
  const widths = [320, 360, 390, 430, 768, 1024, 1280, 1440];
  const original = page.viewportSize() ?? { width: 1440, height: 900 };
  const report = [];
  for (const width of widths) {
    await page.setViewportSize({ width, height: 900 });
    await page.waitForTimeout(400);
    const result = await page.evaluate(() => {
      const root = document.documentElement;
      const limit = root.clientWidth;
      const clipped = (el) => {
        if (getComputedStyle(el).position === 'fixed') return true;
        for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
          const s = getComputedStyle(p);
          if (/(hidden|clip|auto|scroll)/.test(s.overflowX)) return true;
          if (s.position === 'fixed') return true;
        }
        return false;
      };
      const culprits = [...document.body.querySelectorAll('*')]
        .filter((el) => {
          const r = el.getBoundingClientRect();
          return r.width > 0 && (r.right > limit + 1 || r.left < -1) && !clipped(el);
        })
        // keep the outermost offenders only
        .filter((el, _, all) => !all.some((other) => other !== el && other.contains(el)))
        .slice(0, 8)
        .map((el) => {
          const r = el.getBoundingClientRect();
          const cls = typeof el.className === 'string' ? el.className.trim().split(/\s+/).slice(0, 4).join('.') : '';
          return `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${cls ? '.' + cls : ''} [${Math.round(r.left)}..${Math.round(r.right)}]`;
        });
      return { overflow: root.scrollWidth - limit, culprits };
    });
    report.push({ width, ...result });
  }
  await page.setViewportSize(original);
  return report.map((r) => (r.overflow > 0 || r.culprits.length ? r : `${r.width}: ok`));
}
