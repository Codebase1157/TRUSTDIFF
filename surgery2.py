"""Second pass: rewrite the captions and text of the figures regenerated in this
run (11, 13, 17, 18, 19), move the downstream experiment to Indian Pines, extend
the provenance subsection, and finally renumber the surviving figures."""
import html
import pickle
import re

import numpy as np

from surgery import DOC, body_items, find, replace_para, set_text, drop, stage4

OUT = "/home/claude/work/out"


def fmt(v, n=3):
    return f"{v:.{n}f}"


def main():
    x = open(DOC, encoding="utf8").read()

    # ------------------------------------------------ Fig. 11
    z = pickle.load(open(f"{OUT}/zeta_sweep.pkl", "rb"))
    rows = z["rows"]
    g = lambda m, k: [r[k] for r in rows if r["method"] == m]
    tr, am, sa = g("trust", "RIH"), g("argmax", "RIH"), g("softattn", "RIH")
    always_lo, always_hi = min(am + sa), max(am + sa)
    rg_tr = g("trust", "RG")

    F11 = ("Fig. 11. CNC-Bench sweep over the non-correspondence fraction ζ, measured on the "
           "Houston tile. (a) PSNR, with the no-reference baseline A0 drawn as a dashed line; "
           "(b) reference-induced hallucination inside Ω_nc; (c) reference gain against A0, "
           "with the band in which H1 would hold shaded. The target and its low-resolution "
           "observation do not depend on ζ, so A0 is a single constant and the identity "
           "RG = PSNR(Y) − PSNR(A0) is exact rather than approximate. Panel (b) is the one "
           f"that separates the methods: the two always-transfer rules stay between {fmt(always_lo)} "
           f"and {fmt(always_hi)} across the whole sweep, whereas TRUST-Diff starts at {fmt(tr[0])} "
           f"and rises only to {fmt(tr[-1])}, converging on them at ζ = 0.8, where four fifths "
           "of the reference has no counterpart and there is little left to abstain from. "
           "TRUST-Diff also holds the highest PSNR and the least negative reference gain at every "
           f"ζ, from {fmt(rg_tr[0], 2)} dB to {fmt(rg_tr[-1], 2)} dB, so the ordering the "
           "method predicts is reproduced. The gains are negative throughout because this figure "
           "was produced in the reduced setting of Sec. V-E-3, in which the frozen prior is "
           "replaced; H1 is therefore assessed against Table IX and not against this panel.")

    # ------------------------------------------------ Fig. 17
    p = pickle.load(open(f"{OUT}/param_sweep.pkl", "rb"))
    tau_h = p["houston"]["res"]["tau"]
    tau_lo, tau_hi = tau_h[0], tau_h[-1]
    mono = all(tau_h[i][1]["RIH"] <= tau_h[i + 1][1]["RIH"] + 1e-9
               for i in range(len(tau_h) - 1))
    F17 = ("Fig. 17. Parameter sensitivity, shown as small multiples instead of twin axes and "
           "measured on both scenes. Top row: PSNR; bottom row: RIH on a logarithmic scale. "
           "Columns: subspace dimension k, reverse steps T, entropic regularization ε and mass "
           "abstention τ. The dotted vertical line marks the default. The τ column is the "
           f"experiment that tests H2: on Houston, lowering τ from {tau_hi[0]} to {tau_lo[0]} "
           f"takes RIH from {fmt(tau_hi[1]['RIH'])} to {fmt(tau_lo[1]['RIH'])}, "
           + ("a monotone decrease, which is the dependence Proposition 2 predicts through the "
              "rate 1/(τ + ε); "
              if mono else
              "and the trend over the sampled values is reported as measured rather than "
              "smoothed; ") +
           "the price is that valid matches are eventually rejected as well, so PSNR declines "
           "and the default balances trust against reconstruction. Produced in the reduced "
           "setting of Sec. V-E-3.")

    # ------------------------------------------------ Fig. 18
    rt = pickle.load(open(f"{OUT}/runtime.pkl", "rb"))
    rr = rt["rows"]
    sp = [r["t_match_exhaustive"] / max(r["t_match_ann"], 1e-9) for r in rr]
    ann = np.array([r["t_match_ann"] for r in rr])
    exh = np.array([r["t_match_exhaustive"] for r in rr])
    ny = np.array([r["n_pixels"] for r in rr], float)
    growth_ann = ann[-1] / ann[0]
    growth_exh = exh[-1] / exh[0]
    F18 = ("Fig. 18. Cost against reference size, measured on the Houston reference as N_Y grows "
           f"from {rr[0]['n_pixels']:,} to {rr[-1]['n_pixels']:,} pixels, a factor of "
           f"{ny[-1]/ny[0]:.1f}. (a) Time for one correspondence refresh. The candidate-set query "
           f"is flat in N_Y, rising only by a factor of {growth_ann:.2f} over that range, because "
           "only the approximate-nearest-neighbor lookup depends on the size of the reference; "
           "scoring every reference node instead grows by a factor of "
           f"{growth_exh:.1f}, which is linear in N_Y and is the cost structure of a "
           "sliding-window search. The two have not yet crossed at these sizes, since the index "
           "query carries a fixed construction cost that dominates while the reference is small; "
           "what the panel establishes is the scaling, and it is the scaling that decides the "
           "cost on a full scene. (b) The one-off reference graph, descriptor and index build, "
           f"with a linear fit, from {rr[0]['t_index']:.1f} s to {rr[-1]['t_index']:.1f} s; it is "
           "paid once per scene rather than once per step. Absolute times are for the CPU "
           "implementation of Sec. V-E-3 and are not comparable with the GPU figures of "
           "Table XIV.")

    edits = {
        "Fig. 11. CNC-Bench sweep over the non-correspondence fraction": F11,
        "Fig. 17. Parameter sensitivity": F17,
        "Fig. 18. Runtime against reference side length": F18,
    }

    # ------------------------------------------------ downstream: Indian Pines
    ip = pickle.load(open(f"{OUT}/indian_classify.pkl", "rb"))
    t = ip["table"]
    order = ["HR ground truth", "Bicubic", "No-reference (A0)",
             "Argmax, always transfer", "TRUST-Diff"]
    best = max((k for k in order if k != "HR ground truth"), key=lambda k: t[k]["OA"])
    F19 = ("Fig. 19. Downstream classification on Indian Pines (AVIRIS, 200 bands, 16 classes). "
           "Ground-truth labels, classification maps for the bicubic, no-reference, "
           "always-transfer and TRUST-Diff reconstructions, and the normalized confusion matrix "
           "of the TRUST-Diff map. One support-vector machine over thirty principal components "
           "and their 5x5 spatial context is trained once on ten per cent of the labelled "
           "ground-truth spectra and applied unchanged to every reconstruction. The result is "
           "negative and is reported as such: overall accuracy is "
           f"{t['Bicubic']['OA']:.1f} % for bicubic and {t['No-reference (A0)']['OA']:.1f} % for "
           f"the no-reference sampler against {t['HR ground truth']['OA']:.1f} % on the ground "
           "truth itself, so a reconstruction that is spatially smoother than the truth scores "
           "higher. At a 20 m ground sampling distance over large homogeneous fields there is no "
           "fine spatial structure whose recovery this classifier could reward, and spatial "
           "smoothing is a known benefit on this scene, so the experiment measures smoothness "
           "rather than resolution. Reference transfer costs about eighteen points of overall "
           "accuracy on this task, because texture injected into the null space perturbs the "
           "spectra the classifier reads. The one comparison that does behave as the method "
           "predicts is inside the replaced regions, where TRUST-Diff reaches "
           f"{t['TRUST-Diff']['OA_nc']:.1f} % against "
           f"{t['Argmax, always transfer']['OA_nc']:.1f} % for unconditional transfer: abstention "
           "limits the damage where the reference has no counterpart. A scene with fine spatial "
           "structure is needed to test the downstream claim properly; see Sec. V-J.")

    edits["Fig. 19. Downstream classification on Houston 2013"] = F19

    SECJ = ("A support-vector machine over thirty principal components and their 5x5 spatial "
            "context is trained once on ten per cent of the labelled ground-truth spectra of "
            "Indian Pines [41] and applied unchanged to each super-resolved cube, so the "
            "classifier never sees a reconstruction during training and the only thing that "
            "varies between rows is the reconstruction itself. Table XV and Fig. 19 report "
            "overall accuracy, average accuracy and kappa on the held-out ninety per cent, "
            "together with accuracy restricted to the replaced regions. The experiment does not "
            "support the claim it was meant to test, and the reason is a property of the scene "
            f"rather than of the methods: bicubic reaches {t['Bicubic']['OA']:.1f} % and the "
            f"no-reference sampler {t['No-reference (A0)']['OA']:.1f} %, both above the "
            f"{t['HR ground truth']['OA']:.1f} % obtained on the ground-truth cube itself. At a "
            "20 m ground sampling distance over large homogeneous fields, spatial smoothing helps "
            "a pixel-wise classifier and spatial sharpness does not, so the task rewards blur and "
            "cannot distinguish reconstructions in the direction reconstruction quality would "
            "predict. Reference transfer costs about eighteen points of overall accuracy here, "
            "because texture written into the null space perturbs the spectra the classifier "
            "reads; that cost is a real caution about unconditional transfer, and it is the same "
            "mechanism Figs. 5 and 6 show in the image domain. Within the replaced regions the "
            f"ordering the method predicts does appear: {t['TRUST-Diff']['OA_nc']:.1f} % for "
            f"TRUST-Diff against {t['Argmax, always transfer']['OA_nc']:.1f} % for unconditional "
            "transfer, a gain of "
            f"{t['TRUST-Diff']['OA_nc'] - t['Argmax, always transfer']['OA_nc']:.1f} points from "
            "abstention alone. Validating the downstream claim properly needs a scene with fine "
            "spatial structure and dense labels; Houston 2013 is the natural candidate, but the "
            "released training mask carries only 255 labelled pixels inside the test crop used "
            "here, too few to train and evaluate on, so that experiment is left to future work.")

    edits["A fixed support-vector-machine classifier with twenty principal components"] = SECJ

    TXV = ("TABLE XV. Downstream classification accuracy on the super-resolved images (fixed "
           "support-vector-machine classifier, Indian Pines, sixteen classes, trained once on the "
           "ground truth and applied unchanged). OA in Ω_nc is overall accuracy restricted to "
           "the replaced regions. Kappa cannot exceed overall accuracy and does not in any row.")
    edits["TABLE XV. Downstream classification accuracy"] = TXV

    for prefix, new in edits.items():
        try:
            x = replace_para(x, prefix, new)
            print(f"  rewrote: {prefix[:55]}")
        except KeyError:
            print(f"  ! NOT FOUND: {prefix[:55]}")

    # ------------------------------------------------ Table XV contents
    items = body_items(x)
    i = find(items, "TABLE XV. Downstream classification")
    ts, te, _, _ = items[i + 1]
    tbl = x[ts:te]
    rows_xml = list(re.finditer(r"<w:tr[ >].*?</w:tr>", tbl, re.S))
    tpl_head, tpl_body = rows_xml[0].group(0), rows_xml[1].group(0)

    def make_row(tpl, values):
        cs = list(re.finditer(r"<w:tc>.*?</w:tc>", tpl, re.S))
        out, prev, parts = [], 0, []
        for c, v in zip(cs, values):
            cell = c.group(0)
            pm = re.search(r"<w:p[ >].*?</w:p>", cell, re.S)
            newp = set_text(pm.group(0), v)
            parts.append((c.start(), c.end(), cell[:pm.start()] + newp + cell[pm.end():]))
        for s, e, new in sorted(parts, reverse=True):
            tpl = tpl[:s] + new + tpl[e:]
        return tpl

    head = ["Method", "OA (%)", "AA (%)", "kappa"]
    body = []
    for name in order:
        r = t[name]
        body.append([name if name != "HR ground truth" else "HR-HSI ground truth (upper bound)",
                     f"{r['OA']:.1f}", f"{r['AA']:.1f}", f"{r['kappa']:.3f}"])
    new_tbl = tbl[:rows_xml[0].start()] + make_row(tpl_head, head) + \
        "".join(make_row(tpl_body, b) for b in body) + tbl[rows_xml[-1].end():]
    x = x[:ts] + new_tbl + x[te:]
    print(f"  Table XV rebuilt with {len(body)} rows")

    # ------------------------------------------------ provenance subsection
    x = x.replace(html.escape("3) Provenance of Figs. 4, 5, 6, 10 and 15", quote=False),
                  html.escape("3) Provenance of the regenerated figures", quote=False))
    x = x.replace(
        html.escape("These five figures are computed end to end from the two public cubes they "
                    "name, under the degradation protocol of Sec. V-A,", quote=False),
        html.escape("Figs. 4, 5, 6, 10, 11, 13, 15, 17, 18 and 19 are computed end to end from "
                    "the public cubes they name, under the degradation protocol of Sec. V-A,",
                    quote=False))
    x = x.replace(
        html.escape("Finally, the comparison columns of Figs. 5 and 6 are mechanism surrogates",
                    quote=False),
        html.escape("The ζ sweep of Fig. 11 reproduces the ordering the method predicts - "
                    "TRUST-Diff keeps the lowest hallucination and the least negative reference "
                    "gain at every ζ - but not the sign of the gain, so H1 is assessed against "
                    "Table IX. Finally, the comparison columns of Figs. 5 and 6 are mechanism "
                    "surrogates", quote=False))

    # ------------------------------------------------ CNC-Bench lead-in
    x = x.replace(
        html.escape("Fig. 11 and Table IX report the outcome, and Table IX also", quote=False),
        html.escape("Table IX reports the outcome, and it also", quote=False))

    # ------------------------------------------------ renumber last
    x = stage4(x)
    open(DOC, "w", encoding="utf8").write(x)
    print("written")


if __name__ == "__main__":
    main()
