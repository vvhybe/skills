"""Post-process guide.docx: enable embedded TrueType fonts and give fallbacks a family."""
import re, shutil, sys, zipfile
src = sys.argv[1]; dst = sys.argv[2]
zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == "word/settings.xml":
        s = data.decode()
        if "<w:embedTrueTypeFonts" not in s:
            ins = '<w:embedTrueTypeFonts/>'
            if "<w:displayBackgroundShape/>" in s:
                s = s.replace("<w:displayBackgroundShape/>", "<w:displayBackgroundShape/>" + ins, 1)
            else:
                s = re.sub(r"(<w:settings[^>]*>)", lambda m: m.group(1) + ins, s, count=1)
        data = s.encode()
    elif item.filename == "word/fontTable.xml":
        s = data.decode()
        def fam(m):
            name, body = m.group(1), m.group(2)
            val, pitch = ("modern", "fixed") if "Mono" in name else ("swiss", "variable")
            body = re.sub(r'<w:family w:val="[^"]*"/>', f'<w:family w:val="{val}"/>', body)
            body = re.sub(r'<w:pitch w:val="[^"]*"/>', f'<w:pitch w:val="{pitch}"/>', body)
            return f'<w:font w:name="{name}">{body}</w:font>'
        s = re.sub(r'<w:font w:name="([^"]+)">(.*?)</w:font>', fam, s, flags=re.S)
        data = s.encode()
    zout.writestr(item, data)
zout.close()
print("patched", dst)


def inject_toc(docx_in, docx_out, toc_json):
    """Fill the TOC field's cached result, so the contents page reads well before any field update."""
    import json
    from xml.sax.saxutils import escape
    entries = json.load(open(toc_json))
    zin = zipfile.ZipFile(docx_in)
    zout = zipfile.ZipFile(docx_out, "w", zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            d = data.decode()
            marker = '<w:fldChar w:fldCharType="separate"/></w:r></w:p>'
            i = d.find('TOC \\h')
            j = d.find(marker, i) + len(marker)
            paras = []
            for e in entries:
                style = "TOC1" if e["level"] == 1 else "TOC2"
                parts = e["text"].split("\t")
                num_runs = ""
                if len(parts) == 2:
                    num_runs = (f'<w:r><w:rPr><w:rFonts w:ascii="Anton" w:hAnsi="Anton"/><w:color w:val="{e.get("colour", "8A8983")}"/></w:rPr>'
                                f'<w:t xml:space="preserve">{escape(parts[0])}</w:t></w:r><w:r><w:tab/></w:r>')
                    title = parts[1]
                else:
                    title = parts[0]
                tabs = '<w:tabs><w:tab w:val="left" w:pos="1000"/><w:tab w:val="right" w:leader="dot" w:pos="9638"/></w:tabs>'
                paras.append(
                    f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{tabs}</w:pPr>'
                    f'<w:hyperlink w:anchor="{e["anchor"]}" w:history="1">{num_runs}'
                    f'<w:r><w:t xml:space="preserve">{escape(title)}</w:t></w:r><w:r><w:tab/></w:r>'
                    f'<w:r><w:t>{e["page"]}</w:t></w:r></w:hyperlink></w:p>')
            d = d[:j] + "".join(paras) + d[j:]
            data = d.encode()
        zout.writestr(item, data)
    zout.close()


if len(sys.argv) > 3:
    inject_toc(dst, dst.replace(".docx", "-toc.docx"), sys.argv[3])
    print("toc injected")
