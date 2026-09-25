"""Terminology, scope and consistency pass.

Two jobs:

  1. "simulated dataset" is replaced by "reduced resolution" wherever the phrase
     was doing contrastive work, i.e. wherever it implied a real-data counterpart
     that this article does not report.  Where the word merely names the protocol
     (a simulated spectral response, a simulated four-band MSI) it stays.
     A short definition of the term is added to Sect. 5.1 so a reviewer meets it
     once, in plain words, before it is used.

  2. The loose ends that the dataset removal left: Table 1's G4 row, the Salinas
     scene used by the two schematic figures, the uncited [42], the
     self-referential note about an earlier version, and the apparent
     contradiction between the number in Fig. 1's caption and the one printed
     inside the panel.

Everything is edited inside <w:t> character data only.  Rebuilding a paragraph
from its stripped text would destroy the inline equation objects it carries.
"""
import html
import re
import sys

sys.path.insert(0, "/home/claude/work")
from springer import DOC, body_items

# --------------------------------------------------------------------------
# (old, new, expected number of occurrences)
EDITS = [
    # ---- 1. the eight contrastive uses
    ("On two simulated datasets",
     "On two reduced-resolution datasets", 2),

    ("Table 2 lists the data. Both simulated sets reproduce the settings of [4] "
     "for direct comparability; CNC-Bench is new. An earlier version of this study "
     "also announced a spaceborne EnMAP/PRISMA plus Sentinel-2 set; because no "
     "quantitative result could be obtained for it, that set has been removed from "
     "the benchmark, from the abstract and from the conclusion, and spaceborne data "
     "is named only as future work in Sect. 6.4.",
     "Table 2 lists the data used for the reconstruction experiments. Both datasets "
     "reproduce the settings of [4] for direct comparability; CNC-Bench is new. A "
     "further scene, Indian Pines (AVIRIS, 145 × 145 pixels, 200 bands, sixteen "
     "labelled classes) [41], is too small to carry a target together with a larger "
     "partly disjoint reference and is therefore not used for reconstruction; it "
     "appears only in the downstream-classification experiment of Sect. 5.10, which "
     "needs its labels. No spaceborne pair is evaluated: a set combining EnMAP or "
     "PRISMA with Sentinel-2 was prepared, but no quantitative result could be "
     "obtained for it, so spaceborne data is named only as future work in Sect. 6.4.",
     1),

    ("Quantitative results on simulated datasets",
     "Quantitative results at reduced resolution", 1),

    ("Qualitative analysis of the simulated datasets",
     "Qualitative analysis at reduced resolution", 1),

    ("Reconstruction on the simulated datasets",
     "Reconstruction at reduced resolution", 2),

    ("Across both simulated datasets",
     "Across both datasets", 1),

    # ---- the definition a reviewer needs, placed where the protocol is stated
    ("All simulated LR-HSIs follow one Wald-type protocol [43]:",
     "Every experiment in this article is carried out at reduced resolution, and "
     "the term is used in its standard sense: the available hyperspectral image is "
     "taken as the ground truth, the low-resolution input is produced from it by a "
     "known degradation, and the reconstruction is scored against that ground "
     "truth. No sensor delivers a hyperspectral image at the target resolution, so "
     "this is the only regime in which per-pixel measures such as PSNR, SSIM and "
     "SAM can be computed at all; it is the protocol used throughout this "
     "literature [4], [43], and a result obtained under it is indicative of, rather "
     "than identical to, performance on a sensor’s native imagery. Every "
     "low-resolution input therefore follows one Wald-type protocol [43]:", 1),

    # ---- 6.4: say plainly what is not reported
    ("Reconstruction quality remains below the fully supervised state of the art "
     "on simulated data. Promising directions include",
     "Reconstruction quality remains below the fully supervised state of the art at "
     "reduced resolution. Every result reported here is obtained at reduced "
     "resolution; no real cross-sensor pair is scored at its native resolution, so "
     "the behaviour of the reliability map under genuine inter-sensor and "
     "inter-date differences is still to be established. Promising directions "
     "include", 1),

    # ---- 2. Table 1, gap G4: the row name now reads as a training requirement,
    #         and the closing column no longer implies a real-pair evaluation
    ("Simulated HR-HSI ground truth required",
     "HR-HSI ground truth required for training", 1),

    ("Zero-shot with respect to HR-HSI: frozen image prior [15] plus a "
     "self-supervised encoder (Sect. 3.8).",
     "Zero-shot with respect to HR-HSI: a frozen image prior [15] and a "
     "self-supervised encoder remove the training requirement (Sect. 3.8). "
     "Evaluation here is still at reduced resolution; no real cross-sensor pair is "
     "scored.", 1),

    # ---- the Salinas scene: named, cited, and its scope stated
    ("one block replaced by a Salinas field patch to emulate land-cover change.",
     "one block replaced by a patch of the Salinas scene (AVIRIS [48]) to emulate "
     "land-cover change. Salinas is used only for this schematic and for Fig. 3, "
     "and in no experiment; the scenes of Table 2 are used everywhere else.", 1),

    (" (Salinas) pasted under a mask ",
     " (Salinas [48], used only for this schematic) pasted under a mask ", 1),

    # ---- [42] was in the list but never cited; it belongs exactly here
    ("off-the-shelf change detectors [8].",
     "off-the-shelf change detectors [8], and multimodal change detection is "
     "itself an open problem [42].", 1),

    # ---- cross-references the Roman-to-Arabic pass could not reach, because the
    #      run boundary falls inside the reference
    ("No number in Tables 5–VI is copied",
     "No number in Tables 5 and 6 is copied", 1),

    ("Tables 5–VI, Table 7",
     "Tables 5 and 6, Table 7", 1),

    ("The reconstruction values of Tables 5–XVI come from the full pipeline",
     "The reconstruction values of Tables 5–14 come from the full pipeline", 1),

    ("matches Tables 5, VI and XII.",
     "matches Tables 5, 6 and 10.", 1),

    # ---- the list of regenerated figures still carried the old numbering
    ("Figs. 4, 5, 6, 10, 11, 13, 15, 17, 18 and 19 are computed end to end",
     "Figs. 4–11 and 13–15 are computed end to end", 1),

    # ---- Fig. 1: the caption and the number printed inside the panel disagree
    #      because they are measured against different references
    ("). (c) Graph encoding and unbalanced transport produce ",
     " against the observed low-resolution image; the smaller value printed inside "
     "the panel is measured against the projection of that image onto the rank-k "
     "subspace and is therefore at round-off level, as Sect. 5.6.4 explains). "
     "(c) Graph encoding and unbalanced transport produce ", 1),
]

# Whole-node replacements. Springer Nature sets the title, the headings and the
# table captions in sentence case; the manuscript arrived in IEEE title case.
# Acronyms, proper nouns and the method name are left alone.
_SENTENCE_CASE = [
    ("TRUST-Diff: Structure-Aware Partial-Correspondence Posterior Diffusion for "
     "Unpaired Reference-Based Hyperspectral Image Super-Resolution",
     "TRUST-Diff: structure-aware partial-correspondence posterior diffusion for "
     "unpaired reference-based hyperspectral image super-resolution"),
    ("2 Related Work", "2 Related work"),
    ("2.1 Unregistered and Unpaired HSI–MSI Fusion",
     "2.1 Unregistered and unpaired HSI–MSI fusion"),
    ("2.2 Reference-Based Super-Resolution and Learned Matching",
     "2.2 Reference-based super-resolution and learned matching"),
    ("2.3 Diffusion Posterior Sampling for Hyperspectral Restoration",
     "2.3 Diffusion posterior sampling for hyperspectral restoration"),
    ("2.4 Optimal Transport for Correspondence",
     "2.4 Optimal transport for correspondence"),
    ("3 Proposed Method: TRUST-Diff", "3 Proposed method: TRUST-Diff"),
    ("3.1 Problem Setting and Observation Model",
     "3.1 Problem setting and observation model"),
    ("3.3 Spectral Subspace and Range–Null Consistency",
     "3.3 Spectral subspace and range–null consistency"),
    ("3.4 Region Graphs and GNN Encoder", "3.4 Region graphs and GNN encoder"),
    ("3.5 Partial Correspondence by Fused Unbalanced Gromov–Wasserstein Transport",
     "3.5 Partial correspondence by fused unbalanced Gromov–Wasserstein transport"),
    ("3.6 Spectral Response Estimation", "3.6 Spectral response estimation"),
    ("3.7 Contrast-Invariant Reference Likelihood and Guidance",
     "3.7 Contrast-invariant reference likelihood and guidance"),
    ("3.8 Transport-Aware Partial Contrastive Learning",
     "3.8 Transport-aware partial contrastive learning"),
    ("3.9 Implementation Notes and Complexity",
     "3.9 Implementation notes and complexity"),
    ("4 Theoretical Analysis", "4 Theoretical analysis"),
    ("4.1 Consistency and Reference Invariance",
     "4.1 Consistency and reference invariance"),
    ("4.2 Transport-Controlled Transfer", "4.2 Transport-controlled transfer"),
    ("4.3 Relation of the Contrastive Objective to InfoNCE",
     "4.3 Relation of the contrastive objective to InfoNCE"),
    ("4.4 Convergence and Scope of the Guarantees",
     "4.4 Convergence and scope of the guarantees"),
    ("5.2 Compared Methods and Implementation Details",
     "5.2 Compared methods and implementation details"),
    ("5.4 Hypotheses and Falsification Criteria",
     "5.4 Hypotheses and falsification criteria"),
    ("5.5 Comparison With State-of-the-Art Methods",
     "5.5 Comparison with state-of-the-art methods"),
    ("5.6 Trustworthiness of Reference Transfer",
     "5.6 Trustworthiness of reference transfer"),
    ("5.7 Ablation Studies", "5.7 Ablation studies"),
    ("5.8 Parameter Sensitivity", "5.8 Parameter sensitivity"),
    ("5.9 Computational Efficiency", "5.9 Computational efficiency"),
    ("5.10 Downstream Application", "5.10 Downstream application"),
    ("5.11 Failure Cases", "5.11 Failure cases"),
    ("6.1 Hypotheses Versus Evidence", "6.1 Hypotheses versus evidence"),
    ("6.2 Supervised Versus Zero-Shot Gap", "6.2 Supervised versus zero-shot gap"),
    ("6.3 Where the Reference Helps", "6.3 Where the reference helps"),
    ("6.4 Limitations and Outlook", "6.4 Limitations and outlook"),
    ("Table 1 Capability Gaps in Unpaired Reference-Based Hyperspectral Image "
     "Super-Resolution and How TRUST-Diff Addresses Them",
     "Table 1 Capability gaps in unpaired reference-based hyperspectral image "
     "super-resolution and how TRUST-Diff addresses them."),
    ("Table 2 Datasets and Correspondence Regimes",
     "Table 2 Datasets and correspondence regimes."),
    ("Table 4 Hypotheses and Falsification Criteria",
     "Table 4 Hypotheses and falsification criteria."),
    # a fix that could not be applied earlier because the phrase spans two runs
    ("A central observation is that the key missing capability is",
     "The capability that is missing is"),
]

# Table 2's "HR-HSI GT (eval. only)" column read "Simulated", which invites the
# reading that the ground truth itself is synthetic. It is not: the ground truth
# is the real cube, and what is simulated is the low-resolution input.
EXACT = [("Simulated", "Wald protocol", 3)] + \
        [(a, b, 1) for a, b in _SENTENCE_CASE]

REF48 = ("48. Graña M, Veganzons MA, Ayerdi B Hyperspectral remote sensing "
         "scenes: Salinas (AVIRIS). Computational Intelligence Group, Universidad "
         "del País Vasco/Euskal Herriko Unibertsitatea. "
         "https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes. "
         "Accessed 25 Sept 2026")


def apply_edits(x):
    nodes = list(re.finditer(
        r"(<w:t(?![^>]*/>)(?:\s[^>]*)?>)((?:(?!</w:t>).)*)(</w:t>)", x, re.S))
    counts = {i: 0 for i in range(len(EDITS) + len(EXACT))}
    out, pos = [], 0
    for m in nodes:
        raw = html.unescape(m.group(2))
        new = raw
        for i, (old, rep, _) in enumerate(EDITS):
            if old in new:
                counts[i] += new.count(old)
                new = new.replace(old, rep)
        for j, (old, rep, _) in enumerate(EXACT):
            if new.strip() == old:
                counts[len(EDITS) + j] += 1
                new = new.replace(old, rep)
        if new != raw:
            out.append(x[pos:m.start()])
            out.append(m.group(1) + html.escape(new, quote=False) + m.group(3))
            pos = m.end()
    out.append(x[pos:])
    rules = EDITS + EXACT
    bad = [(rules[i][0][:60], counts[i], rules[i][2])
           for i in counts if counts[i] != rules[i][2]]
    for t, got, want in bad:
        print(f"  MISMATCH {got}/{want}: {t!r}")
    assert not bad, "edit count mismatch"
    print(f"terminology: {sum(counts.values())} replacements over {len(rules)} rules")
    return "".join(out)


def add_reference(x):
    items = body_items(x)
    i = max(k for k, (s, e, t, raw) in enumerate(items) if t.startswith("47. "))
    s, e, t, raw = items[i]
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", raw, re.S)
    rpr = re.search(r"<w:r>\s*(<w:rPr>.*?</w:rPr>)", raw, re.S)
    ptag = re.match(r"<w:p[^>]*>", raw).group(0)
    p = (f'{ptag}{ppr.group(0) if ppr else ""}<w:r>{rpr.group(1) if rpr else ""}'
         f'<w:t xml:space="preserve">{html.escape(REF48, quote=False)}</w:t></w:r></w:p>')
    print("references: entry 48 (Salinas scene) appended")
    return x[:e] + p + x[e:]


def main():
    x = open(DOC, encoding="utf8").read()
    x = apply_edits(x)
    x = add_reference(x)
    open(DOC, "w", encoding="utf8").write(x)
    print("written")


if __name__ == "__main__":
    main()
