// Build the Word edition of the guide from model.json (written by build_book.py).
// Usage: node build_docx.js <work-dir>   (MONO_FONT = path to a monospace TTF to embed, optional)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, ImageRun, Header, Footer, PageNumber, LevelFormat,
  TableOfContents, ExternalHyperlink, InternalHyperlink, Bookmark, VerticalAlign, TableLayoutType,
  HeightRule, SectionType, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo,
  PositionalTabLeader, PageBreak,
  HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom,
} = require("docx");

const BUILD = path.resolve(process.argv[2] || ".");
const model = JSON.parse(fs.readFileSync(path.join(BUILD, "model.json"), "utf8"));
const FONTS = model.fonts_dir;
const META = model.meta;
const SUBTITLE = META.subtitle || "Developer Guide";
const FOOTER = META.footer || `${META.title} · ${SUBTITLE}`;

// ---- design tokens -------------------------------------------------------------------
const PART = {
  0: { main: "EB6834", dark: "C24E1F", tint: "FDF2EC", soft: "F9D5C4" },
  1: { main: "2A78D6", dark: "1B5AA6", tint: "EEF5FD", soft: "CFE0F7" },
  2: { main: "139A6B", dark: "0D7A54", tint: "ECF8F2", soft: "C8EBDB" },
  3: { main: "EB6834", dark: "C24E1F", tint: "FDF2EC", soft: "F9D5C4" },
  4: { main: "4A3AA7", dark: "372A85", tint: "F2F0FB", soft: "DCD8F3" },
};
const CALLOUT = {
  note: { k: "2A78D6", t: "EEF5FD" }, tip: { k: "1F8A3B", t: "EBF6ED" }, why: { k: "4A3AA7", t: "F2F0FB" },
  warn: { k: "B87700", t: "FFF6DF" }, never: { k: "CF3736", t: "FDEEEE" },
};
const INK = "1A1A19", INK2 = "52514E", MUTED = "8A8983", RULE = "E4E3DF";
const F = { body: "Inter", bold: "Inter SemiBold", head: "Montserrat SemiBold", num: "Anton", mono: "DejaVu Sans Mono" };
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134, TEXT_W = PAGE_W - 2 * MARGIN;
const mmToPx = (mm) => Math.round((mm / 25.4) * 96);
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NONE, bottom: NONE, left: NONE, right: NONE };

// ---- runs ----------------------------------------------------------------------------
const bookmarkId = (href) => href.replace(/^#/, "").replace(/[^A-Za-z0-9_]/g, "_");

function textRun(r, base, P) {
  const o = { text: r.text, font: base.font || F.body, size: base.size || 19, color: base.color || INK };
  if (r.b) o.font = base.boldFont || F.bold;
  if (r.i) o.italics = true;
  if (base.bold) o.bold = true;
  if (r.code) {
    o.font = F.mono; o.size = Math.max(14, (base.size || 19) - 3);
    o.color = base.codeColor || P.dark;
    o.shading = { type: ShadingType.CLEAR, color: "auto", fill: base.codeFill || "F1F0EC" };
  }
  if (r.color) o.color = r.color.replace("#", "");
  if (base.allCaps) o.allCaps = true;
  if (base.characterSpacing) o.characterSpacing = base.characterSpacing;
  return new TextRun(o);
}

function runs(list, base, P) {
  const out = [];
  for (const r of list || []) {
    if (r.br) { out.push(new TextRun({ break: 1 })); continue; }
    if (r.link) {
      const link = { ...base, color: base.linkColor || P.dark };
      const tr = textRun(r, link, P);
      if (r.link.startsWith("#")) out.push(new InternalHyperlink({ anchor: bookmarkId(r.link), children: [tr] }));
      else out.push(new ExternalHyperlink({ link: r.link, children: [tr] }));
      continue;
    }
    out.push(textRun(r, base, P));
  }
  return out;
}

// ---- helpers ---------------------------------------------------------------------------
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}
function imageFor(src) {
  if (src.endsWith(".svg")) return path.join(BUILD, "raster", path.basename(src, ".svg") + ".png");
  return src;
}
function boxTable(children, { fill, left, leftSize = 20, border, dashed = false, width = TEXT_W, margins, keep = true }) {
  const side = border
    ? { style: dashed ? BorderStyle.DASHED : BorderStyle.SINGLE, size: 6, color: border }
    : NONE;
  return new Table({
    width: { size: width, type: WidthType.DXA }, columnWidths: [width], layout: TableLayoutType.FIXED,
    rows: [new TableRow({ cantSplit: keep, children: [new TableCell({
      width: { size: width, type: WidthType.DXA },
      shading: fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined,
      borders: { top: side, bottom: side, right: side,
                 left: left ? { style: BorderStyle.SINGLE, size: leftSize, color: left } : side },
      margins: margins || { top: 140, bottom: 120, left: 220, right: 220 },
      children,
    })] })],
  });
}
const spacer = (after = 120) => new Paragraph({ spacing: { before: 0, after }, children: [] });

// ---- blocks ----------------------------------------------------------------------------
let olInstance = 0;

function listParas(block, P, level = 0, partKey) {
  const out = [];
  const inst = ++olInstance;
  for (const it of block.items) {
    const para = { spacing: { before: 30, after: 50 }, children: [] };
    if (it.task) {
      para.indent = { left: 360 + level * 360, hanging: 300 };
      para.children.push(new TextRun({ text: "☐  ", font: F.mono, size: 20, color: P.main }));
    } else {
      para.numbering = { reference: `${block.ordered ? "ol" : "ul"}-${partKey}`, level, instance: block.ordered ? inst : undefined };
    }
    para.children.push(...runs(it.runs, {}, P));
    out.push(new Paragraph(para));
    for (const child of it.children) {
      if (child.t === "list") out.push(...listParas(child, P, level + 1, partKey));
      else out.push(...render([child], P, partKey));
    }
  }
  return out;
}

function tableBlock(b, P) {
  const cols = b.head.length;
  const len = (rs) => rs.reduce((n, r) => n + (r.text || "").length, 0);
  const weights = Array.from({ length: cols }, (_, c) =>
    Math.min(60, Math.max(8, Math.max(len(b.head[c]), ...b.rows.map((r) => len(r[c] || []))))));
  const total = weights.reduce((a, c) => a + c, 0);
  let widths = weights.map((w) => Math.floor((w / total) * TEXT_W));
  widths[widths.length - 1] += TEXT_W - widths.reduce((a, c) => a + c, 0);
  const cellBorders = { top: NONE, left: NONE, right: NONE, bottom: { style: BorderStyle.SINGLE, size: 4, color: "E7E6E1" } };
  const head = new TableRow({ tableHeader: true, cantSplit: true, children: b.head.map((h, i) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: P.main }, borders: noBorders,
    margins: { top: 90, bottom: 90, left: 120, right: 120 }, verticalAlign: VerticalAlign.BOTTOM,
    children: [new Paragraph({ spacing: { after: 0 }, children: runs(h, { font: F.head, boldFont: F.head, size: 15, color: "FFFFFF", codeColor: "FFFFFF", codeFill: P.dark }, P) })],
  })) });
  const rows = b.rows.map((row, ri) => new TableRow({ cantSplit: true, children: row.map((cell, i) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: ri % 2 ? { type: ShadingType.CLEAR, color: "auto", fill: P.tint } : undefined,
    borders: cellBorders, margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ spacing: { after: 0, line: 264 }, children: runs(cell, { size: 17, boldFont: F.bold, color: INK }, P) })],
  })) }));
  return [new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
                      rows: [head, ...rows] }), spacer(160)];
}

function codeBlock(b, P) {
  // split coloured runs into lines
  const lines = [[]];
  for (const r of b.runs) {
    const parts = r.text.split("\n");
    parts.forEach((p, i) => {
      if (i > 0) lines.push([]);
      if (p) lines[lines.length - 1].push({ ...r, text: p });
    });
  }
  while (lines.length && lines[lines.length - 1].length === 0) lines.pop();
  const paras = [];
  if (b.lang) paras.push(new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 20 },
    children: [new TextRun({ text: b.lang.toUpperCase(), font: F.head, size: 12, color: P.main, characterSpacing: 20 })] }));
  for (const line of lines) {
    paras.push(new Paragraph({ spacing: { before: 0, after: 0, line: 250 }, children: line.length
      ? line.map((r) => new TextRun({ text: r.text, font: F.mono, size: 15, color: (r.color || "#24292F").replace("#", ""),
                                      bold: !!r.b, italics: !!r.i }))
      : [new TextRun({ text: " ", font: F.mono, size: 15 })] }));
  }
  return [boxTable(paras, { fill: "F7F7F9", left: P.main, leftSize: 18, border: "E6E6EA",
                            margins: { top: 100, bottom: 120, left: 200, right: 160 } }), spacer(160)];
}

function calloutBlock(b, P, partKey) {
  const c = b.kind === "goal" ? { k: P.dark, t: P.tint } : CALLOUT[b.kind] || CALLOUT.note;
  const title = new Paragraph({ spacing: { after: 60 }, keepNext: true, children: [
    new TextRun({ text: "● ", font: F.mono, size: 16, color: c.k }),
    new TextRun({ text: b.title.toUpperCase(), font: F.head, size: 15, color: c.k, characterSpacing: 16 }),
  ] });
  const body = render(b.blocks, P, partKey, { inBox: true });
  return [boxTable([title, ...body], { fill: c.t, left: c.k, leftSize: 24,
                                       border: b.kind === "goal" ? P.soft : undefined }), spacer(160)];
}

function statsBlock(b) {
  const colours = ["2A78D6", "139A6B", "EB6834", "4A3AA7", "C98500"];
  const n = b.items.length, w = Math.floor(TEXT_W / n);
  const white = { style: BorderStyle.SINGLE, size: 36, color: "FFFFFF" };
  return [new Table({ width: { size: w * n, type: WidthType.DXA }, columnWidths: Array(n).fill(w), layout: TableLayoutType.FIXED,
    rows: [new TableRow({ children: b.items.map(([num, label], i) => new TableCell({
      width: { size: w, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill: colours[i % 5] },
      borders: { top: white, bottom: white, left: white, right: white }, margins: { top: 120, bottom: 120, left: 60, right: 60 },
      children: [
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: num, font: F.num, size: 52, color: "FFFFFF" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [new TextRun({ text: label.toUpperCase(), font: F.head, size: 12, color: "FFFFFF", characterSpacing: 12 })] }),
      ],
    })) })] }), spacer(200)];
}

function figureBlock(b, P) {
  const file = imageFor(b.src);
  const { w, h, data } = pngSize(file);
  const wmm = Math.min(b.w_mm || 168, 168);
  const wpx = mmToPx(wmm), hpx = Math.round((wpx * h) / w);
  const maxH = mmToPx(160);
  const scale = hpx > maxH ? maxH / hpx : 1;
  const out = [new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 80 },
    children: [new ImageRun({ type: "png", data, transformation: { width: Math.round(wpx * scale), height: Math.round(hpx * scale) } })] })];
  if (b.num) out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [
    new TextRun({ text: b.num.toUpperCase() + "   ", font: F.head, size: 14, color: P.main, characterSpacing: 14 }),
    ...runs(b.caption, { size: 16, color: INK2 }, P),
  ] }));
  return out;
}

function quizBlock(b, P) {
  const paras = [new Paragraph({ spacing: { after: 100 }, keepNext: true, children: [
    new TextRun({ text: "✎ ", font: F.mono, size: 24, color: "946300" }),
    new TextRun({ text: "Check yourself", font: F.head, size: 24, color: "946300" }),
  ] })];
  for (const it of b.items) {
    if (it.t === "q") paras.push(new Paragraph({ keepNext: true, spacing: { before: 120, after: 40 },
      children: runs(it.runs, { font: F.bold, boldFont: F.bold }, P) }));
    else paras.push(new Paragraph({ spacing: { after: 80 }, indent: { left: 200 },
      border: { left: { style: BorderStyle.SINGLE, size: 18, color: "F0C75A", space: 8 } },
      children: [new TextRun({ text: "ANSWER  ", font: F.head, size: 12, color: "946300", characterSpacing: 16 }),
                 ...runs(it.runs, { size: 17, color: "4A4944" }, P)] }));
  }
  return [spacer(120), boxTable(paras, { fill: "FFFAEB", border: "E2B33D", dashed: true, keep: false,
                                         margins: { top: 160, bottom: 140, left: 260, right: 260 } })];
}

function render(list, P, partKey, opts = {}) {
  const out = [];
  for (const b of list) {
    switch (b.t) {
      case "h2":
        out.push(new Paragraph({ heading: HeadingLevel.HEADING_3, keepNext: true, spacing: { before: 360, after: 120 }, children: [
          new TextRun({ text: "■ ", font: F.mono, size: 22, color: P.main }),
          ...runs(b.runs, { font: F.head, boldFont: F.head, size: 28, color: "111111" }, P)] }));
        break;
      case "h3":
        out.push(new Paragraph({ heading: HeadingLevel.HEADING_4, keepNext: true, spacing: { before: 240, after: 80 },
          children: runs(b.runs, { font: F.head, boldFont: F.head, size: 22, color: INK }, P) }));
        break;
      case "p":
        out.push(new Paragraph({ spacing: { after: opts.inBox ? 60 : 120, line: 290 },
          children: runs(b.runs, b.cls === "lead" ? { size: 23, color: "3A3935" } : {}, P) }));
        break;
      case "list": out.push(...listParas(b, P, 0, partKey)); if (!opts.inBox) out.push(spacer(60)); break;
      case "code": out.push(...codeBlock(b, P)); break;
      case "table": out.push(...tableBlock(b, P)); break;
      case "callout": out.push(...calloutBlock(b, P, partKey)); break;
      case "stats": out.push(...statsBlock(b)); break;
      case "figure": out.push(...figureBlock(b, P)); break;
      case "quiz": out.push(...quizBlock(b, P)); break;
    }
  }
  return out;
}

// ---- page furniture -----------------------------------------------------------------------
function chapterHeader(kicker, title, P) {
  return new Header({ children: [new Paragraph({ spacing: { after: 0 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 4 } },
    children: [
      new TextRun({ text: kicker.toUpperCase(), font: F.head, size: 13, color: P.main, characterSpacing: 20 }),
      new TextRun({ children: [new PositionalTab({ alignment: PositionalTabAlignment.RIGHT,
        relativeTo: PositionalTabRelativeTo.MARGIN, leader: PositionalTabLeader.NONE }), title],
        font: F.head, size: 15, color: INK2 }),
    ] })] });
}
function pageFooter(P) {
  return new Footer({ children: [new Paragraph({ children: [
    new TextRun({ text: FOOTER, font: F.body, size: 14, color: "A3A29C" }),
    new TextRun({ children: [new PositionalTab({ alignment: PositionalTabAlignment.RIGHT,
      relativeTo: PositionalTabRelativeTo.MARGIN, leader: PositionalTabLeader.NONE })] }),
    new TextRun({ text: "■ ", font: F.mono, size: 16, color: P.main }),
    new TextRun({ children: [PageNumber.CURRENT], font: F.head, size: 20, color: P.main }),
  ] })] });
}
const emptyHeader = () => new Header({ children: [new Paragraph({ children: [] })] });
const emptyFooter = () => new Footer({ children: [new Paragraph({ children: [] })] });
const pageProps = (extra = {}) => ({ page: { size: { width: PAGE_W, height: PAGE_H },
  margin: { top: 1360, bottom: 1250, left: MARGIN, right: MARGIN, header: 700, footer: 640 } }, ...extra });

function opener(ch, P, label) {
  const badge = new Table({ width: { size: 1500, type: WidthType.DXA }, columnWidths: [1500], layout: TableLayoutType.FIXED,
    rows: [new TableRow({ children: [new TableCell({ width: { size: 1500, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: "auto", fill: P.main }, borders: noBorders,
      margins: { top: 60, bottom: 40, left: 80, right: 80 }, verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 },
        children: [new TextRun({ text: label, font: F.num, size: label.length > 2 ? 44 : 60, color: "FFFFFF" })] })] })] })] });
  const out = [
    new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: ch.kicker.toUpperCase(), font: F.head, size: 14, color: P.main, characterSpacing: 30 })] }),
    badge,
    new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 160 }, keepNext: true, children: [
      new Bookmark({ id: bookmarkId(ch.id), children: [new TextRun({ text: ch.title, font: F.head, size: 46, color: "111111" })] })] }),
  ];
  if (ch.lead && ch.lead.length) out.push(new Paragraph({ spacing: { after: 120, line: 300 }, children: runs(ch.lead, { size: 23, color: "3A3935" }, P) }));
  out.push(new Paragraph({ spacing: { after: 280 }, border: { bottom: { style: BorderStyle.SINGLE, size: 24, color: P.main, space: 4 } }, children: [] }));
  if (ch.objectives && ch.objectives.length) out.push(...render(ch.objectives, P, "p" + ch.part));
  return out;
}

function partDivider(part) {
  const P = PART[part.n];
  const H = 13600;
  const white = (text, font, size, extra = {}) => new TextRun({ text, font, size, color: "FFFFFF", ...extra });
  const items = [];
  for (const ch of part.chapters) {
    const label = ch.num ? String(ch.num).padStart(2, "0") : "A–Z";
    items.push(new Paragraph({ spacing: { before: 110, after: 0 }, indent: { left: 1100, hanging: 1100 }, children: [
      white(label, F.num, 36), new TextRun({ text: "\t" }), white(ch.title, F.head, 24)] ,
      tabStops: [{ type: "left", position: 1100 }] }));
    if (ch.desc) items.push(new Paragraph({ spacing: { after: 30 }, indent: { left: 1100 }, children: [white(ch.desc, F.body, 18)] }));
  }
  return new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: [TEXT_W], layout: TableLayoutType.FIXED,
    rows: [new TableRow({ height: { value: H, rule: HeightRule.EXACT }, children: [new TableCell({
      width: { size: TEXT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill: P.main },
      borders: noBorders, margins: { top: 900, bottom: 400, left: 700, right: 700 },
      children: [
        new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 0 }, children: [white(part.roman, F.num, 96, { color: P.soft })] }),
        new Paragraph({ spacing: { after: 80 }, children: [white(`PART ${part.roman}`, F.head, 20, { characterSpacing: 60 })] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 380 },
          children: [new Bookmark({ id: `part_${part.n}`, children: [white(part.title, F.head, 64)] })] }),
        ...items,
      ] })] })] });
}

// ---- document ------------------------------------------------------------------------------
function coverSection() {
  // The cover is page 1 of the printed book (raster/cover.png), placed full-bleed behind the page so
  // both editions open on the same cover. Its text lives in the document title and the alt text.
  const art = fs.readFileSync(path.join(BUILD, "raster", "cover.png"));
  return {
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: 0, bottom: 0, left: 0, right: 0, header: 0, footer: 0 } } },
    headers: { default: emptyHeader() }, footers: { default: emptyFooter() },
    children: [
      new Paragraph({ spacing: { after: 0 }, children: [new ImageRun({
        type: "png", data: art,
        transformation: { width: mmToPx(210), height: mmToPx(297) },
        floating: {
          horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: 0 },
          verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: 0 },
          behindDocument: true,
        },
        altText: { title: "Cover", description: `${META.title}: ${SUBTITLE}. ${META.tagline}`, name: "cover" },
      })] }),
    ],
  };
}

function frontSection() {
  const P = PART[0];
  const children = [
    new Paragraph({ spacing: { after: 300 }, children: [new TextRun({ text: "Contents", font: F.head, size: 60, color: "111111" })] }),
    new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }),
    new Paragraph({ children: [new PageBreak()] }),
    ...opener({ id: "about", kicker: "Before you start", title: "About this guide", lead: model.about.lead, objectives: [], part: 0 }, P, "i"),
    ...render(model.about.body, P, "p0"),
  ];
  return { properties: pageProps(), headers: { default: chapterHeader(META.title, "About this guide", P) },
           footers: { default: pageFooter(P) }, children };
}

function sections() {
  const out = [coverSection(), frontSection()];
  for (const part of model.parts) {
    const P = PART[part.n];
    out.push({ properties: pageProps({ type: SectionType.NEXT_PAGE }), headers: { default: emptyHeader() },
               footers: { default: emptyFooter() }, children: [partDivider(part)] });
    for (const ch of part.chapters) {
      const label = ch.num ? String(ch.num).padStart(2, "0") : "A–Z";
      const kicker = `Part ${part.roman} · ${part.title}`;
      const furniture = { headers: { default: chapterHeader(kicker, ch.title, P), first: emptyHeader() },
                          footers: { default: pageFooter(P), first: pageFooter(P) } };
      if (ch.id === "glossary") {
        out.push({ properties: pageProps({ type: SectionType.NEXT_PAGE, titlePage: true }), ...furniture, children: opener(ch, P, label) });
        out.push({ properties: pageProps({ type: SectionType.CONTINUOUS, column: { count: 2, space: 500 } }), ...furniture,
                   children: render(ch.body, P, "p" + part.n) });
      } else {
        out.push({ properties: pageProps({ type: SectionType.NEXT_PAGE, titlePage: true }), ...furniture,
                   children: [...opener(ch, P, label), ...render(ch.body, P, "p" + part.n)] });
      }
    }
  }
  out.push({ properties: pageProps({ type: SectionType.NEXT_PAGE }), headers: { default: emptyHeader() }, footers: { default: emptyFooter() },
    children: [
      new Table({ width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: Array(4).fill(TEXT_W / 4), layout: TableLayoutType.FIXED,
        rows: [new TableRow({ height: { value: 400, rule: HeightRule.EXACT }, children: ["2A78D6", "139A6B", "EB6834", "4A3AA7"].map((c) => new TableCell({
          width: { size: TEXT_W / 4, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: "auto", fill: c }, borders: noBorders, children: [new Paragraph("")] })) })] }),
      new Paragraph({ spacing: { before: 9000, after: 200 }, children: [new TextRun({ text: `${META.title} — ${SUBTITLE}`, font: F.head, size: 32, color: "111111" })] }),
      new Paragraph({ spacing: { after: 160, line: 300 }, children: [new TextRun({ text: `This document is built from the Markdown pages in ${META.guide_dir || "docs/guide"}/ of the ${META.repo_name} repository. Read them on GitHub or in Obsidian; this Word edition and the printed PDF are generated from the same source.`, font: F.body, size: 19, color: INK2 })] }),
      new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: `Written against the repository as it stood on ${META.as_of}.`, font: F.body, size: 19, color: INK2 })] }),
      new Paragraph({ spacing: { before: 300 }, children: [new TextRun({ text: META.legal || "", font: F.body, size: 16, color: MUTED })] }),
    ] });
  return out;
}

function numbering() {
  const config = [];
  for (const k of [0, 1, 2, 3, 4]) {
    const c = PART[k].main;
    config.push({ reference: `ul-p${k}`, levels: [
      { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { run: { color: c, font: F.body }, paragraph: { indent: { left: 400, hanging: 260 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
        style: { run: { color: c, font: F.mono }, paragraph: { indent: { left: 800, hanging: 260 } } } },
    ] });
    config.push({ reference: `ol-p${k}`, levels: [
      { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { run: { color: c, font: F.head }, paragraph: { indent: { left: 420, hanging: 320 } } } },
      { level: 1, format: LevelFormat.DECIMAL, text: "%2.", alignment: AlignmentType.LEFT,
        style: { run: { color: c, font: F.head }, paragraph: { indent: { left: 860, hanging: 320 } } } },
    ] });
  }
  return { config };
}

const embed = (name, file) => ({ name, data: fs.readFileSync(file) });
const doc = new Document({
  creator: META.author || "", title: `${META.title} — ${SUBTITLE}`,
  description: META.tagline, features: { updateFields: true },
  fonts: [
    embed("Inter", `${FONTS}/Inter-Regular.ttf`),
    embed("Inter SemiBold", `${FONTS}/Inter-SemiBold.ttf`),
    embed("Montserrat SemiBold", `${FONTS}/Montserrat-SemiBold.ttf`),
    embed("Anton", `${FONTS}/Anton-Regular.ttf`),
    ...(process.env.MONO_FONT && fs.existsSync(process.env.MONO_FONT) ? [embed("DejaVu Sans Mono", process.env.MONO_FONT)] : []),
  ],
  styles: {
    default: { document: { run: { font: F.body, size: 19, color: INK }, paragraph: { spacing: { after: 120, line: 290 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: F.head, size: 60, color: "FFFFFF" }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: F.head, size: 46, color: "111111" }, paragraph: { outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: F.head, size: 28, color: "111111" }, paragraph: { outlineLevel: 2 } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: F.head, size: 22, color: INK }, paragraph: { outlineLevel: 3 } },
      { id: "TOC1", name: "toc 1", basedOn: "Normal", next: "Normal",
        run: { font: F.head, size: 22, color: "111111" }, paragraph: { spacing: { before: 200, after: 60 } } },
      { id: "TOC2", name: "toc 2", basedOn: "Normal", next: "Normal",
        run: { font: F.body, size: 20, color: INK }, paragraph: { indent: { left: 400 }, spacing: { after: 40 } } },
    ],
  },
  numbering: numbering(),
  sections: sections(),
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(BUILD, "guide.docx"), buf);
  console.log("docx bytes", buf.length);
});
