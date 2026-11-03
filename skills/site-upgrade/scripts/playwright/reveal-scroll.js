// Scrolls the current page top to bottom in viewport steps so every scroll-triggered reveal,
// lazy image and IntersectionObserver fires, then returns to the top (or to `selector`).
// Use it before full-page screenshots. Pass as the `filename` of browser_run_code_unsafe.
// Edit `selector` to land on a section afterwards, e.g. '#plans'.
async (page) => {
  const selector = null;
  const step = await page.evaluate(() => Math.round(window.innerHeight * 0.6));
  let y = 0;
  for (let i = 0; i < 200; i++) {
    const max = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
    if (y >= max) break;
    y = Math.min(y + step, max);
    await page.mouse.wheel(0, step); // real wheel events, so Lenis-style smooth scrollers follow
    await page.waitForTimeout(120);
  }
  await page.waitForTimeout(600);
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  if (selector) {
    await page.locator(selector).first().scrollIntoViewIfNeeded();
  } else {
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
    await page.mouse.wheel(0, -height);
  }
  await page.waitForTimeout(800);
  const hidden = await page.evaluate(() =>
    [...document.querySelectorAll('main *')]
      .filter((el) => {
        const s = getComputedStyle(el);
        return (s.visibility === 'hidden' || s.opacity === '0') && el.textContent.trim() && el.getBoundingClientRect().height > 0;
      })
      .filter((el, _, all) => !all.some((other) => other !== el && other.contains(el)))
      .slice(0, 10)
      .map((el) => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}: ${el.textContent.trim().slice(0, 50)}`),
  );
  return { scrolledTo: y, pageHeight: height, stillHiddenAfterScroll: hidden };
}
