// At phone width (390), lists controls smaller than 40×40 px and visible text under 12 px on the current page.
// Links inside running text are exempt. Restores the original viewport. Pass as the `filename` of browser_run_code_unsafe.
async (page) => {
  const original = page.viewportSize() ?? { width: 1440, height: 900 };
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  const result = await page.evaluate(() => {
    const describe = (el) => {
      const label = (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40);
      return `${el.tagName.toLowerCase()}${label ? ` "${label}"` : ''}`;
    };
    const shown = (el) => {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && Number(s.opacity) > 0 && !el.closest('[aria-hidden="true"]');
    };
    const small = [];
    for (const el of document.querySelectorAll('button, a[href], [role="button"], [aria-haspopup], [role="tab"], [role="checkbox"], [role="switch"], select')) {
      if (!shown(el)) continue;
      if (el.tagName === 'A' && el.closest('p, li') && el.parentElement.textContent.trim().length > el.textContent.trim().length + 10) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 40 || r.height < 40) small.push(`${describe(el)} ${Math.round(r.width)}×${Math.round(r.height)}`);
    }
    const tiny = new Map();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const text = node.textContent.trim();
      const el = node.parentElement;
      if (!text || !el || !shown(el) || el.closest('script, style, svg')) continue;
      const size = parseFloat(getComputedStyle(el).fontSize);
      if (size < 12) tiny.set(el, `${size}px "${text.slice(0, 30)}"`);
    }
    return {
      smallControls: small.slice(0, 30), moreSmall: Math.max(0, small.length - 30),
      tinyText: [...tiny.values()].slice(0, 30), moreTiny: Math.max(0, tiny.size - 30),
    };
  });
  await page.setViewportSize(original);
  return result;
}
