"""Last typographic corrections, all applied without rebuilding any paragraph
that could contain an inline equation."""
import html
import re
import sys

sys.path.insert(0, "/home/claude/work")
from springer import DOC, _sub_in_text_nodes


def main():
    x = open(DOC, encoding="utf8").read()

    # 1. a stray space before punctuation is left wherever an inline equation
    #    object is followed by a comma or a full stop
    def spacing(t):
        t = re.sub(r"[  ]+([,.;:)])", r"\1", t)
        t = re.sub(r"\(\s+", "(", t)
        t = re.sub(r"[ ]{2,}", " ", t)
        return t

    x, n = _sub_in_text_nodes(x, spacing)
    print(f"1: punctuation spacing cleaned in {n} text nodes")

    # 1b. the same defect across a run boundary: an inline equation object sits
    #     between two text nodes, so the stray space ends one node and the comma
    #     or full stop opens the next
    nodes = list(re.finditer(
        r"(<w:t(?![^>]*/>)(?:\s[^>]*)?>)((?:(?!</w:t>).)*)(</w:t>)", x, re.S))
    out, pos, k, prev_space, prev_end = [], 0, 0, False, -1
    for m in nodes:
        raw = html.unescape(m.group(2))
        new = re.sub(r"^[  ]+(?=[,.;:)])", "", raw)
        # only when the two nodes are truly adjacent: an equation, a tab or a
        # break between them means both spaces are wanted
        gap = x[prev_end:m.start()] if prev_end >= 0 else ""
        if prev_space and not re.search(r"<(?:m:oMath|w:tab|w:br|w:drawing)", gap):
            new = re.sub(r"^[ ]+", "", new)
        prev_space = new.endswith(" ") or (not new and prev_space)
        prev_end = m.end()
        if new != raw:
            k += 1
            out.append(x[pos:m.start()])
            out.append(m.group(1) + html.escape(new, quote=False) + m.group(3))
            pos = m.end()
    out.append(x[pos:])
    x = "".join(out)
    print(f"1b: {k} run-boundary spacing defects removed")

    # 1c. the IEEE opening word is set in small caps; Springer does not do this
    x = re.sub(r"(<w:r>(?:(?!</w:r>).)*?)<w:smallCaps[^>]*/>"
               r"((?:(?!</w:r>).)*?<w:t[^>]*>Hyperspectral</w:t>(?:(?!</w:r>).)*?</w:r>)",
               r"\1\2", x, count=1, flags=re.S)
    print("1c: opening word set roman")

    # 2. one body paragraph is set entirely in italic, which was invisible while
    #    the manuscript was highlighted
    b = x.index("<w:body>")
    for m in re.finditer(r"<w:p[ >].*?</w:p>", x[b:], re.S):
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(0))).strip()
        if t.startswith("Three capability gaps run through this literature"):
            raw = m.group(0)
            new = re.sub(r'<w:i/>|<w:i w:val="(?:1|true|on)"\s*/>', "", raw)
            new = re.sub(r'<w:iCs/>|<w:iCs w:val="(?:1|true|on)"\s*/>', "", new)
            x = x[:b + m.start()] + new + x[b + m.end():]
            print("2: capability-gaps paragraph set roman")
            break

    # 3. the fourth contribution is bold throughout; the other three bold only
    #    their lead phrase
    b = x.index("<w:body>")
    for m in re.finditer(r"<w:p[ >].*?</w:p>", x[b:], re.S):
        full = html.unescape(re.sub(r"<[^>]+>", "", m.group(0))).strip()
        if not full.startswith("4) Guarantees and an evaluation protocol"):
            continue
        raw = m.group(0)
        lead = "Guarantees and an evaluation protocol for trustworthy transfer."
        i = full.index(lead) + len(lead)
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", raw, re.S)
        rpr = re.search(r"<w:r>\s*(<w:rPr>.*?</w:rPr>)", raw, re.S)
        rp_b = rpr.group(1) if rpr else "<w:rPr><w:b/></w:rPr>"
        rp_p = re.sub(r"<w:b/>|<w:bCs/>", "", rp_b)
        ptag = re.match(r"<w:p[^>]*>", raw).group(0)
        new = (f'{ptag}{ppr.group(0) if ppr else ""}'
               f'<w:r>{rp_b}<w:t xml:space="preserve">'
               f'{html.escape(full[:i], quote=False)}</w:t></w:r>'
               f'<w:r>{rp_p}<w:t xml:space="preserve"> '
               f'{html.escape(full[i:].lstrip(), quote=False)}</w:t></w:r></w:p>')
        x = x[:b + m.start()] + new + x[b + m.end():]
        print("3: contribution 4 rebuilt with a bold lead phrase only")
        break

    open(DOC, "w", encoding="utf8").write(x)
    print("written")


if __name__ == "__main__":
    main()
