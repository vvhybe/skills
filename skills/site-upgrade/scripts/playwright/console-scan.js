// Visits every page in the sitemap of the current origin, scrolls each one, and collects console errors,
// uncaught page errors, failed requests and CSP violations. Run it on `next start` (production CSP).
// Navigate to any page of the site first, then pass this as the `filename` of browser_run_code_unsafe.
async (page) => {
  const origin = new URL(page.url()).origin;
  const xml = await (await page.request.get(`${origin}/sitemap.xml`)).text();
  const urls = [...new Set([...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => {
    const u = new URL(m[1]);
    return `${origin}${u.pathname}${u.search}`;
  }))].filter((u) => !/\/opengraph-image|\.(png|jpe?g|webp|svg)$/.test(u));
  if (!urls.length) urls.push(`${origin}/`);

  const found = [];
  let current = '';
  const onConsole = (msg) => {
    if (msg.type() === 'error' || /Content Security Policy|hydrat/i.test(msg.text())) {
      found.push({ page: current, kind: 'console', text: msg.text().slice(0, 300) });
    }
  };
  const onPageError = (err) => found.push({ page: current, kind: 'pageerror', text: String(err).slice(0, 300) });
  const onFailed = (req) => {
    const reason = req.failure()?.errorText ?? '';
    // aborted media and prefetches are normal when navigating away
    if (!/ERR_ABORTED|NS_BINDING_ABORTED/.test(reason)) found.push({ page: current, kind: 'requestfailed', text: `${req.url()} ${reason}` });
  };
  const onResponse = (res) => {
    if (res.status() >= 400 && res.url().startsWith(origin)) found.push({ page: current, kind: `http ${res.status()}`, text: res.url() });
  };
  page.on('console', onConsole);
  page.on('pageerror', onPageError);
  page.on('requestfailed', onFailed);
  page.on('response', onResponse);

  try {
    for (const url of urls) {
      current = new URL(url).pathname;
      await page.goto(url, { waitUntil: 'load' });
      await page.evaluate(() => {
        window.__csp = [];
        document.addEventListener('securitypolicyviolation', (e) =>
          window.__csp.push(`${e.violatedDirective} blocked ${e.blockedURI || 'inline'}`));
      });
      const height = await page.evaluate(() => document.documentElement.scrollHeight);
      for (let y = 0; y < height; y += 700) {
        await page.mouse.wheel(0, 700);
        await page.waitForTimeout(80);
      }
      await page.waitForTimeout(500);
      for (const v of await page.evaluate(() => window.__csp ?? [])) found.push({ page: current, kind: 'csp', text: v });
    }
  } finally {
    page.off('console', onConsole);
    page.off('pageerror', onPageError);
    page.off('requestfailed', onFailed);
    page.off('response', onResponse);
  }
  return { pages: urls.length, problems: found.length, found: found.slice(0, 40) };
}
