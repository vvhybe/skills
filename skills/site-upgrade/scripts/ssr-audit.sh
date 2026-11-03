#!/usr/bin/env bash
# Checks that pages are really server-rendered and carry their SEO basics (see references/seo-standards.md):
# status, one <h1>, JSON-LD blocks, a canonical link, an og:image, no client-side bailout, a <title>.
#   ssr-audit.sh <base-url> [path ...]        e.g. ssr-audit.sh http://localhost:3100 / /faq /contact
# With no paths it reads every <loc> from <base-url>/sitemap.xml (rewritten onto <base-url>).
# Run it against `next start`, not `next dev`. Exits 1 when any page fails.
set -uo pipefail

base=${1:?usage: ssr-audit.sh <base-url> [path ...]}
base=${base%/}
shift
paths=("$@")
if [ ${#paths[@]} -eq 0 ]; then
  # a while-read loop rather than mapfile, so it also runs on macOS's bash 3.2
  while IFS= read -r p; do paths+=("$p"); done < <(curl -fsS --max-time 15 "$base/sitemap.xml" |
    grep -oE '<loc>[^<]+</loc>' | sed -E 's#</?loc>##g; s#^https?://[^/]+##; s#^$#/#' | sort -u)
  [ ${#paths[@]} -gt 0 ] || { echo "no paths given and no sitemap at $base/sitemap.xml"; exit 2; }
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fail=0

printf '%-28s %4s %3s %3s %5s %3s %8s %7s  %s\n' PATH CODE H1 LD CANON OG CSR BYTES TITLE
for p in "${paths[@]}"; do
  code=$(curl -sS --max-time 30 -o "$tmp/body" -D "$tmp/head" -w '%{http_code}' "$base$p") || code=ERR
  body=$(cat "$tmp/body" 2>/dev/null || true)
  h1=$(grep -oE '<h1[ >]' <<<"$body" | wc -l)
  ld=$(grep -oE '<script[^>]*type="application/ld\+json"' <<<"$body" | wc -l)
  csr=ok
  grep -q 'BAILOUT_TO_CLIENT_SIDE_RENDERING' <<<"$body" && csr=BAILOUT
  grep -qE '<div>Loading\.\.\.</div>' <<<"$body" && csr=LOADING
  title=$(grep -oE '<title[^>]*>[^<]*</title>' <<<"$body" | head -1 | sed -E 's#</?title[^>]*>##g')
  canon=no
  grep -qE '<link[^>]+rel="canonical"' <<<"$body" && canon=yes
  og=no
  grep -qE '<meta[^>]+property="og:image"' <<<"$body" && og=yes
  printf '%-28s %4s %3s %3s %5s %3s %8s %7s  %s\n' "$p" "$code" "$h1" "$ld" "$canon" "$og" "$csr" "${#body}" "${title:0:60}"
  if [ "$code" != 200 ] || [ "$h1" -ne 1 ] || [ "$csr" != ok ] || [ -z "$title" ] || [ "$canon" != yes ]; then fail=1; fi
done

echo
echo "== headers on $base${paths[0]}"
curl -sS --max-time 30 -o /dev/null -D "$tmp/head" "$base${paths[0]}" || true
for h in strict-transport-security content-security-policy x-content-type-options referrer-policy \
  x-frame-options cross-origin-opener-policy permissions-policy x-powered-by; do
  v=$(grep -i "^$h:" "$tmp/head" | head -1 | cut -d: -f2- | tr -d '\r' | sed 's/^ //')
  if [ "$h" = x-powered-by ]; then
    [ -n "$v" ] && echo "  WARN  $h: $v (set poweredByHeader: false)" || echo "  ok    $h absent"
  else
    [ -n "$v" ] && echo "  ok    $h: ${v:0:90}" || echo "  MISS  $h"
  fi
done

echo
echo "== crawler files"
for f in /robots.txt /sitemap.xml /manifest.webmanifest /.well-known/security.txt /llms.txt /opengraph-image; do
  printf '  %4s  %s\n' "$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' "$base$f" || echo ERR)" "$f"
done

[ $fail -eq 0 ] && echo && echo "all pages pass" || { echo; echo "FAIL: each page needs 200, exactly one <h1>, a <title>, a canonical link and no client-side bailout"; }
exit $fail
