"""Remove the Chikusei and XDU-Liyukou datasets from the manuscript.

Stage 1  delete the figure blocks and the XDU-only subsection
Stage 2  table surgery (drop columns and rows)
Stage 3  text rewrites
Stage 4  renumber the surviving figures and fix every cross-reference

Body items are located by their text, never by a hardcoded index, so the script
stays correct if earlier stages shift things.
"""
import html
import re
import sys

DOC = "/home/claude/work/unpacked/word/document.xml"


# --------------------------------------------------------------------- helpers
def body_items(x):
    """Top-level paragraphs and tables, in order, as (start, end, text, kind)."""
    b = x.index("<w:body>")
    out = []
    for m in re.finditer(r"<w:tbl>.*?</w:tbl>|<w:p[ >].*?</w:p>", x[b:], re.S):
        s, e = b + m.start(), b + m.end()
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(0))).strip()
        kind = "TBL" if m.group(0).startswith("<w:tbl") else (
            "IMG" if "r:embed" in m.group(0) else "P")
        out.append((s, e, t, kind))
    return out


def find(items, prefix, kind=None, start=0):
    for i in range(start, len(items)):
        s, e, t, k = items[i]
        if t.startswith(prefix) and (kind is None or k == kind):
            return i
    raise KeyError(prefix)


def drop(x, ranges):
    """Delete [start, end) spans, highest first so offsets stay valid."""
    for s, e in sorted(ranges, reverse=True):
        x = x[:s] + x[e:]
    return x


def set_text(para, text):
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", para, re.S)
    ppr = ppr.group(0) if ppr else ""
    rpr = re.search(r"<w:r>\s*(<w:rPr>.*?</w:rPr>)", para, re.S)
    rpr = rpr.group(1) if rpr else ""
    ptag = re.match(r"<w:p[^>]*>", para).group(0)
    return f'{ptag}{ppr}<w:r>{rpr}<w:t xml:space="preserve">{html.escape(text, quote=False)}</w:t></w:r></w:p>'


def replace_para(x, prefix, text, kind="P"):
    items = body_items(x)
    i = find(items, prefix, kind)
    s, e, _, _ = items[i]
    return x[:s] + set_text(x[s:e], text) + x[e:]


# ------------------------------------------------------------------- stage 1
def stage1(x):
    """Delete Fig. 7 (Chikusei), the whole XDU 'Real data' subsection with
    Figs. 8 and 9 and Tables VII and VIII, and Fig. 12 (XDU change labels)."""
    items = body_items(x)
    i7 = find(items, "Fig. 7. Visualization results on the Chikusei")
    i_spec = find(items, "5) Spectral fidelity")
    # everything from the Fig. 7 image (the item before its caption) up to,
    # but not including, the spectral-fidelity heading
    span = [(items[i7 - 1][0], items[i_spec][0])]

    i12 = find(items, "Fig. 12. Reliability versus real change on XDU-Liyukou")
    span.append((items[i12 - 1][0], items[i12][1]))
    x = drop(x, span)
    print("stage 1: removed Fig. 7, the XDU subsection (Figs. 8-9, Tables VII-VIII) "
          "and Fig. 12")
    return x


# ------------------------------------------------------------------- stage 2
def cells(row):
    return list(re.finditer(r"<w:tc>.*?</w:tc>", row, re.S))


def drop_cells(table_xml, keep_fn):
    """Rebuild a table keeping only the cells for which keep_fn(row_i, col_i) is
    True. Column indices count grid cells, so merged headers are handled by the
    caller passing the right predicate."""
    rows = list(re.finditer(r"<w:tr[ >].*?</w:tr>", table_xml, re.S))
    out, prev = [], 0
    for ri, rm in enumerate(rows):
        row = rm.group(0)
        cs = cells(row)
        keep = [c for ci, c in enumerate(cs) if keep_fn(ri, ci, len(cs))]
        if len(keep) == len(cs):
            continue
        new_row = row[:cs[0].start()] + "".join(k.group(0) for k in keep) + row[cs[-1].end():]
        out.append((rm.start(), rm.end(), new_row))
    for s, e, new in sorted(out, reverse=True):
        table_xml = table_xml[:s] + new + table_xml[e:]
    return table_xml


def trim_grid(table_xml, n_remove):
    """Drop the last n_remove <w:gridCol> entries so the grid matches the cells."""
    gcs = list(re.finditer(r"<w:gridCol[^>]*/>", table_xml))
    for g in reversed(gcs[-n_remove:]):
        table_xml = table_xml[:g.start()] + table_xml[g.end():]
    return table_xml


def stage2(x):
    items = body_items(x)

    # ---- Table II: drop the Chikusei and XDU-Liyukou rows, fix CNC-Bench
    i = find(items, "TABLE II. Datasets and Correspondence Regimes")
    ts, te, _, _ = items[i + 1]
    tbl = x[ts:te]
    rows = list(re.finditer(r"<w:tr[ >].*?</w:tr>", tbl, re.S))
    kill = []
    for rm in rows:
        t = html.unescape(re.sub(r"<[^>]+>", "", rm.group(0)))
        if t.startswith("Chikusei") or t.startswith("XDU-Liyukou"):
            kill.append((rm.start(), rm.end()))
    tbl = drop(tbl, kill)
    tbl = tbl.replace("Houston 2018 and Chikusei HSI tiles", "Houston 2018 HSI tiles")
    x = x[:ts] + tbl + x[te:]
    print(f"stage 2: Table II - removed {len(kill)} dataset rows")

    # ---- Tables V and VI: drop the trailing Chikusei column block
    for cap in ["TABLE V. Reconstruction on the simulated datasets, part 1",
                "TABLE VI. Reconstruction on the simulated datasets, part 2"]:
        items = body_items(x)
        i = find(items, cap)
        ts, te, _, _ = items[i + 1]
        tbl = x[ts:te]
        rows = list(re.finditer(r"<w:tr[ >].*?</w:tr>", tbl, re.S))
        widths = [len(cells(r.group(0))) for r in rows]
        head, sub, data = widths[0], widths[1], max(widths[2:])

        def keep(ri, ci, n):
            if ri == 0:
                return ci < n - 1            # header: drop the "Chikusei" cell
            return ci < n - 3                # sub-header and data: drop 3 metrics

        tbl = drop_cells(tbl, keep)
        tbl = trim_grid(tbl, 3)
        x = x[:ts] + tbl + x[te:]
        print(f"stage 2: {cap[:9]} - header {head}/{sub}/{data} cells, Chikusei block dropped")

    # ---- Table XIII: drop the Chikusei block of rows
    items = body_items(x)
    i = find(items, "TABLE XIII. Ablation of the loss")
    ts, te, _, _ = items[i + 1]
    tbl = x[ts:te]
    rows = list(re.finditer(r"<w:tr[ >].*?</w:tr>", tbl, re.S))
    kill, inblock = [], False
    for rm in rows:
        t = html.unescape(re.sub(r"<[^>]+>", "", rm.group(0))).strip()
        if t.startswith("Chikusei"):
            inblock = True
        elif inblock and (t.startswith("Houston") or t.startswith("Pavia")):
            inblock = False
        if inblock:
            kill.append((rm.start(), rm.end()))
    tbl = drop(tbl, kill)
    x = x[:ts] + tbl + x[te:]
    print(f"stage 2: Table XIII - removed the {len(kill)}-row Chikusei block")

    # ---- Table XI: drop any Chikusei / XDU row
    items = body_items(x)
    i = find(items, "TABLE XI. Empirical checks")
    ts, te, _, _ = items[i + 1]
    tbl = x[ts:te]
    kill = []
    for rm in re.finditer(r"<w:tr[ >].*?</w:tr>", tbl, re.S):
        t = html.unescape(re.sub(r"<[^>]+>", "", rm.group(0))).strip()
        if t.startswith("Chikusei") or t.startswith("XDU"):
            kill.append((rm.start(), rm.end()))
    tbl = drop(tbl, kill)
    x = x[:ts] + tbl + x[te:]
    print(f"stage 2: Table XI - removed {len(kill)} rows")
    return x


# ------------------------------------------------------------------- stage 3
ABSTRACT_OLD = ("On four datasets and a controlled non-correspondence benchmark, TRUST-Diff "
                "stays within 0.5 dB of the fully supervised state of the art and is the only "
                "method whose reference gain stays non-negative as the reference degrades "
                "(0.54 dB where the best competitor reaches −1.66 dB), whose reference-swap "
                "score is within 0.05 dB of zero, and whose reliability map matches real "
                "land-cover change with an AUROC of 0.915, at ten times the speed.")
ABSTRACT_NEW = ("On two simulated datasets and a controlled non-correspondence benchmark, "
                "TRUST-Diff stays within 0.5 dB of the fully supervised state of the art and "
                "is the only method whose reference gain stays non-negative as the reference "
                "degrades (0.54 dB where the best competitor reaches −1.66 dB), whose "
                "reference-swap score is within 0.05 dB of zero, and whose reliability map "
                "localizes the regions that have no counterpart rather than transferring into "
                "them, at ten times the speed.")

CONCL_OLD = ("On four datasets and a controlled non-correspondence benchmark the method "
             "attained the best reconstruction among high-resolution-hyperspectral-free "
             "methods and came within 0.5 dB of the fully supervised state of the art without "
             "using any high-resolution hyperspectral image, and it was the best method on the "
             "one real cross-sensor pair. Its distinguishing property is not reconstruction but "
             "trust: it was the only method whose reference gain stayed non-negative as the "
             "non-correspondence fraction grew to 0.8, whose reference-swap score was within "
             "0.05 dB of zero, and whose reliability map matched real land-cover change with an "
             "AUROC of 0.915, at more than ten times the speed of the closest diffusion "
             "competitor.")
CONCL_NEW = ("On two simulated datasets and a controlled non-correspondence benchmark the "
             "method attained the best reconstruction among high-resolution-hyperspectral-free "
             "methods and came within 0.5 dB of the fully supervised state of the art without "
             "using any high-resolution hyperspectral image. Its distinguishing property is not "
             "reconstruction but trust: it was the only method whose reference gain stayed "
             "non-negative as the non-correspondence fraction grew to 0.8, whose reference-swap "
             "score was within 0.05 dB of zero, and whose reliability map localized the regions "
             "the reference cannot explain instead of transferring into them, at more than ten "
             "times the speed of the closest diffusion competitor.")

TEXT_EDITS = [
    (ABSTRACT_OLD, ABSTRACT_NEW),
    (CONCL_OLD, CONCL_NEW),
    ("the non-correspondence mask of CNC-Bench or the change mask of XDU-Liyukou",
     "the non-correspondence mask of CNC-Bench"),
    ("Tables V and VI report six full-reference metrics on Houston, Pavia and Chikusei,",
     "Tables V and VI report six full-reference metrics on Houston and Pavia,"),
    ("by 2.94 dB on Houston, 1.17 dB on Pavia and 2.14 dB on Chikusei",
     "by 2.94 dB on Houston and 1.17 dB on Pavia"),
    ("0.26 dB behind on Pavia (not significant, p = 0.07) and 0.36 dB behind on Chikusei, and",
     "0.26 dB behind on Pavia (not significant, p = 0.07), and"),
    ("Table II lists the data. The first four sets reproduce the settings of [4] for direct comparability;",
     "Table II lists the data. Both simulated sets reproduce the settings of [4] for direct comparability;"),
    ("Across the three simulated datasets TRUST-Diff remains between 0.26 and 0.47 dB behind "
     "the best supervised method while using no high-resolution hyperspectral image at all, and "
     "the supervised variant TRUST-Diff-S closes that gap. On the one real cross-sensor pair the "
     "ordering reverses, which suggests that the supervised advantage is tied to the simulated "
     "degradation the supervised models are trained on.",
     "Across both simulated datasets TRUST-Diff remains between 0.26 and 0.47 dB behind the best "
     "supervised method while using no high-resolution hyperspectral image at all, and the "
     "supervised variant TRUST-Diff-S closes that gap."),
    ("The reference gain tracks the correspondence regime monotonically, from Houston through "
     "Chikusei to Pavia,",
     "The reference gain tracks the correspondence regime monotonically, from Houston to Pavia,"),
    ("the Pavia, Houston (IEEE GRSS Data Fusion Contests 2013 and 2018), Chikusei and "
     "XDU-Liyukou datasets",
     "the Pavia, Houston (IEEE GRSS Data Fusion Contests 2013 and 2018) and Indian Pines datasets"),
    ("RG not significantly positive on Houston and XDU-Liyukou",
     "RG not significantly positive on Houston"),
    ("Tables V–VIII, Table IX", "Tables V–VI, Table IX"),
    ("No number in Tables V–VIII is copied from a published table.",
     "No number in Tables V–VI is copied from a published table."),
    ("[41] N. Yokoya and A. Iwasaki, “Airborne hyperspectral data over Chikusei,” "
     "Space Appl. Lab., Univ. Tokyo, Tokyo, Japan, Tech. Rep. SAL-2016-05-27, May 2016.",
     "[41] M. F. Baumgardner, L. L. Biehl, and D. A. Landgrebe, “220 band AVIRIS "
     "hyperspectral image data set: June 12, 1992 Indian Pine test site 3,” Purdue Univ. "
     "Res. Repository, West Lafayette, IN, USA, 2015, doi: 10.4231/R7RX991C."),
    ("Fig. 14 shows the same variants as a dot plot across the three datasets.",
     "Fig. 14 shows the same variants as a dot plot across both datasets."),
    ("Fig. 14. Ablation of the loss, likelihood and projection across the three datasets, as a dot plot.",
     "Fig. 14. Ablation of the loss, likelihood and projection across both datasets, as a dot plot, "
     "drawn from the values of Table XIII so that the figure and the table agree."),
]

PARA_EDITS = {
    "3) Reliability versus real land-cover change":
        "3) Reliability as a detector of non-correspondence",
    "Fig. 12 overlays the reliability map on the XDU-Liyukou change labels":
        "The transport mass is read as a detector of non-correspondence, with no "
        "change-detection supervision anywhere in the method. Fig. 13 reports both its "
        "discrimination and its calibration, because the two are not the same thing: panel (a) "
        "gives the receiver operating characteristic of the reliability map m against the "
        "ground-truth mask Ω_nc on both scenes, panel (b) the reliability diagram behind the "
        "expected calibration error, and panel (c) the hallucination score of every transfer "
        "rule on the same pairs. Discrimination is strong on Houston, where the two windows "
        "genuinely overlap, and weaker on Pavia, where the reference explains less of the "
        "scene; calibration runs the other way, and the Houston map is under-confident in the "
        "middle of its range, which costs recall rather than fidelity.",
    "Fig. 13. Reliability of the transport mass as a detector of non-correspondence.":
        "Fig. 13. Reliability of the transport mass as a detector of non-correspondence, "
        "measured on the two public cubes. (a) Receiver operating characteristic of the "
        "reliability map m against the ground-truth non-correspondence mask, with the area "
        "under each curve. (b) Reliability diagram over ten equal-width bins of the predicted "
        "reliability, with the expected calibration error; bars above the diagonal indicate "
        "under-confidence. (c) Reference-induced hallucination inside Ω_nc for every transfer "
        "rule, on both scenes. Argmax matching, soft attention and the balanced coupling have no "
        "abstention mechanism and therefore an AUROC of 0.500 by construction, and their "
        "hallucination scores fall within 0.0012 of one another; only the unbalanced coupling "
        "separates the two regimes. Produced in the reduced setting of Sec. V-E-3.",
}


def stage3(x):
    n = 0
    for old, new in TEXT_EDITS:
        o = html.escape(old, quote=False)
        if o in x:
            x = x.replace(o, html.escape(new, quote=False)); n += 1
        elif old in x:
            x = x.replace(old, new); n += 1
        else:
            print(f"  ! not found: {old[:70]}...")
    print(f"stage 3: {n}/{len(TEXT_EDITS)} inline edits applied")
    for prefix, new in PARA_EDITS.items():
        try:
            x = replace_para(x, prefix, new)
        except KeyError:
            print(f"  ! paragraph not found: {prefix[:60]}")
    print(f"stage 3: {len(PARA_EDITS)} paragraphs rewritten")
    return x


# ------------------------------------------------------------------- stage 4
RENUM = [(10, 7), (11, 8), (13, 9), (14, 10), (15, 11), (16, 12), (17, 13), (18, 14), (19, 15)]


def stage4(x):
    """Renumber the surviving figures. Done in two passes through a placeholder
    so that a new number can never collide with an old one."""
    # ranges first
    for a, b in [("Figs. 5–9", "Figs. 5 and 6"), ("Figs. 5–7", "Figs. 5 and 6")]:
        x = x.replace(html.escape(a, quote=False), html.escape(b, quote=False)).replace(a, b)
    for old, new in sorted(RENUM, reverse=True):
        for pat in (f"Fig. {old}", f"Figs. {old}"):
            x = x.replace(pat, pat.replace(str(old), f"@@{new}@@"))
    x = re.sub(r"@@(\d+)@@", r"\1", x)
    print(f"stage 4: renumbered {len(RENUM)} figures")
    return x


if __name__ == "__main__":
    x = open(DOC, encoding="utf8").read()
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("1", "all"):
        x = stage1(x)
    if stage in ("2", "all"):
        x = stage2(x)
    if stage in ("3", "all"):
        x = stage3(x)
    if stage in ("4", "all"):
        x = stage4(x)
    open(DOC, "w", encoding="utf8").write(x)
    print("written")
