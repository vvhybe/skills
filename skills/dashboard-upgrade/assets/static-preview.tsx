// Renders one presentational component to a static HTML page with the app's theme tokens and one CSS block,
// for a visual check when a dev server won't fit in memory. Copy it to the scratchpad, edit the three EDIT
// lines, then from the repo root:
//   NODE_PATH=$PWD/node_modules npx tsx --tsconfig tsconfig.json <copy>.tsx <out-dir>/index.html
//   (cd <out-dir> && python3 -m http.server 4747 --bind 127.0.0.1)   # Playwright MCP blocks file://
// Toggle dark mode in the page with document.documentElement.classList.add('dark').
import { readFileSync, writeFileSync } from "node:fs";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LotusPond as Preview } from "@/components/ui/lotus-pond"; // EDIT: the component to preview (this is the reference's)

const CSS_FILE = "app/globals.css"; // EDIT: the app's global stylesheet
// EDIT: the first and last lines of the CSS the component needs (keyframes, component classes).
const BLOCK = { from: "@keyframes petal-fall", to: "/* ─── Zen Utility Classes ─── */" };

// The classic JSX transform used by tsx needs React in scope.
(globalThis as Record<string, unknown>).React = React;

const css = readFileSync(CSS_FILE, "utf8");
const body = (opener: string) => {
	const start = css.indexOf(opener);
	if (start < 0) return "";
	return css.slice(css.indexOf("{", start) + 1, css.indexOf("\n}", start));
};
// Theme colours: Tailwind 4 keeps them in @theme, the dark values under .dark.
const colours = (block: string) =>
	block
		.split("\n")
		.filter((line) => line.trim().startsWith("--color-"))
		.join("\n");
const from = css.indexOf(BLOCK.from);
const to = css.indexOf(BLOCK.to, from);
if (from < 0 || to < 0) throw new Error("CSS block markers not found");
// @layer wrappers are harmless, but unwrap them so the block stays plain CSS.
const block = css.slice(from, to).replace(/@layer\s+\w+\s*{/g, "{");

// Tailwind utilities the component uses are not compiled here: add the few it needs.
const utilities = ".absolute{position:absolute}.w-full{width:100%}.overflow-visible{overflow:visible}";

const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{${colours(body("@theme {"))}}
.dark{color-scheme:dark;${colours(body("\n.dark {"))}}
html,body{margin:0;min-height:100%}
body{background:var(--color-background);color:var(--color-foreground);font-family:system-ui,sans-serif}
.stage{position:relative;min-height:100dvh;overflow:hidden}
${utilities}
${block}
</style></head><body><div class="stage">${renderToStaticMarkup(<Preview />)}</div></body></html>`;

writeFileSync(process.argv[2] ?? "preview.html", html);
console.log(`wrote ${process.argv[2] ?? "preview.html"} (${html.length} bytes)`);
