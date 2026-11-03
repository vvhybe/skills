// Lists controls whose centre is covered by another element, so a tap or click lands on something else
// (the dead "⋮" menu). Scrolls each control into view first. Pass as the `filename` of browser_run_code_unsafe.
async (page) => {
  return await page.evaluate(async () => {
    const selector = [
      'button', 'a[href]', '[role="button"]', '[aria-haspopup]', '[role="menuitem"]', '[role="tab"]',
      'input:not([type="hidden"])', 'select', 'textarea',
    ].join(',');
    const describe = (el) => {
      const label = (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
      const cls = typeof el.className === 'string' ? el.className.trim().split(/\s+/).slice(0, 3).join('.') : '';
      return `${el.tagName.toLowerCase()}${cls ? '.' + cls : ''}${label ? ` "${label}"` : ''}`;
    };
    const frame = () => new Promise((resolve) => requestAnimationFrame(() => resolve()));
    const startY = scrollY;
    const covered = [];
    let checked = 0;
    for (const el of document.querySelectorAll(selector)) {
      const style = getComputedStyle(el);
      let r = el.getBoundingClientRect();
      // skip hidden and visually-hidden controls (sr-only inputs behind styled checkboxes)
      if (r.width < 4 || r.height < 4 || style.visibility === 'hidden' || style.pointerEvents === 'none' || Number(style.opacity) === 0) continue;
      if (el.closest('[aria-hidden="true"], [inert]')) continue;
      if (r.top < 0 || r.bottom > innerHeight) {
        el.scrollIntoView({ block: 'center' });
        await frame();
        r = el.getBoundingClientRect();
      }
      const x = r.left + r.width / 2;
      const y = r.top + r.height / 2;
      if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
      checked++;
      const hit = document.elementFromPoint(x, y);
      if (!hit || hit === el || el.contains(hit)) continue;
      if (hit.closest('label') && hit.closest('label').control === el) continue;
      // The Next.js dev overlay (its issues badge) floats over the page in dev only.
      if (hit.closest('nextjs-portal')) continue;
      covered.push({ control: describe(el), coveredBy: describe(hit) });
    }
    scrollTo(0, startY);
    return { width: innerWidth, checked, covered: covered.slice(0, 25), more: Math.max(0, covered.length - 25) };
  });
}
