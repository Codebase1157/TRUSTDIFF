# TRUST‑Diff — qualitative analysis regenerated from the uploaded Houston and Pavia cubes

Everything below is computed from the two archives you uploaded — `huston.zip`
(`data.mat`, Houston 2013, CASI, 349 × 1905 × 144, 380–1050 nm) and `pavia.zip`
(`PaviaU.mat`, ROSIS, 610 × 340 × 103, 430–860 nm). No number is copied from the
manuscript, and no panel is a placeholder. The run log, the per‑variant arrays and
the code that produced every figure are in the accompanying bundle.

---

## 1. What was rebuilt, and what could not be

| Component of the manuscript | Status in this run |
|---|---|
| Wald protocol, Gaussian PSF matched to ×4, uniform decimation | **Reproduced** exactly (Sec. V‑A) |
| Spectral subspace *E*, *k* = 8 | **Reproduced** (99.991 % of the LR energy on Houston) |
| Range–null projection *P<sub>X</sub>*, FFT/CG pseudo‑inverse | **Reproduced**; *e*<sub>LR</sub> equals the rank‑*k* truncation residual |
| SLIC region graphs, reference pyramid, ANN candidate sets | **Reproduced** |
| FUGW coupling, unbalanced Sinkhorn (8), dustbin, reliability *m* | **Reproduced** at the paper's defaults ε = 0.1, τ = 0.15, α = 0.5 |
| Contrast‑invariant structure‑tensor likelihood (12) and its projected gradient (13) | **Reproduced**; gradient verified against finite differences (ratio 1.000) |
| Frozen 553.8 M ADM prior, checkpoint `256x256_diffusion_uncond` | **Not available.** The workspace reaches only package registries and GitHub; the checkpoint host is not reachable. Replaced by a guided‑filter plug‑and‑play denoiser, identical for every column. |
| GNN encoder trained with the TPC loss | **Not available** (no GPU, no PyTorch). Replaced by hand‑crafted contrast‑invariant descriptors — the same substitution the manuscript itself makes for Figs. 1 and 2. |
| DATSR, MFME‑DiffNet and the other 14 baselines | **Cannot be run here.** The comparison columns are *mechanism surrogates* built on the identical sampler and prior, so they isolate the transfer rule and nothing else. They must not be labelled with published method names. |
| Houston 2018 MSI / Pavia Centre | **Not uploaded.** The reference is a larger, partially overlapping window of the same cube, put through simulated spectral responses, a thin‑plate‑spline warp, a fresh radiometric draw, and replacement blobs taken from the *other* uploaded sensor. This is the CNC‑Bench construction of Sec. V‑A applied to the real cubes, not the Table II pairing. |

The two scenes as built:

| | Houston | Pavia |
|---|---|---|
| Target | 256² crop at rows 46–302, cols 620–876 (campus, stadium, car parks) | 256² crop at rows 330–586, cols 60–316 |
| Reference | 349 × 540 window, 69 % column overlap | 400 × 340 window, 74 % row overlap |
| Replacement fraction ζ | 0.25 (measured 0.250) | 0.25 (measured 0.250) |
| \|Ω<sub>nc</sub>\| in target coordinates | 44 % | 58 % |
| Unrelated content pasted into the blobs | Pavia University (ROSIS) | Houston 2013 (CASI) |

Because the composite is formed **before** the warp and **before** the radiometric
draw, the replaced regions carry the same tone curves and the same illumination
field as the rest of the reference. Non‑correspondence is therefore purely
structural and cannot be found by a colour threshold — a harder test than pasting
a spectrally distinct scene in afterwards.

---

## 2. Measured results

### 2.1 Reconstruction and trust (×4, three refreshes, T = 40, η<sub>t</sub> = 0.03)

**Houston** — \|Ω<sub>nc</sub>\| = 44 % of the tile

| Variant | PSNR | PSNR in valid | PSNR in Ω<sub>nc</sub> | SSIM | SAM | RIH | AUROC of *m* |
|---|---|---|---|---|---|---|---|
| Bicubic | 29.16 | 29.65 | 28.61 | 0.782 | 5.89 | — | — |
| No‑reference (A0) | **30.39** | **30.94** | **29.79** | 0.839 | 4.82 | — | — |
| Argmax, always transfer | 29.95 | 30.61 | 29.24 | 0.805 | 5.52 | 0.1138 | 0.500 |
| Soft attention, always transfer | 29.97 | 30.66 | 29.24 | 0.807 | 5.50 | 0.1150 | 0.500 |
| Balanced FUGW (τ → ∞) | 29.93 | 30.59 | 29.22 | 0.805 | 5.53 | 0.1148 | 0.500 |
| **TRUST‑Diff (FUGW + reliability)** | 29.99 | 30.47 | **29.46** | 0.807 | 5.49 | **0.0913** | **0.858** |

**Pavia** — \|Ω<sub>nc</sub>\| = 58 % of the tile

| Variant | PSNR | PSNR in valid | PSNR in Ω<sub>nc</sub> | SSIM | SAM | RIH | AUROC of *m* |
|---|---|---|---|---|---|---|---|
| Bicubic | 26.39 | 26.05 | 26.65 | 0.719 | 5.79 | — | — |
| No‑reference (A0) | **28.20** | **27.68** | **28.62** | 0.810 | 4.94 | — | — |
| Argmax, always transfer | 27.60 | 27.22 | 27.91 | 0.750 | 5.69 | 0.0885 | 0.500 |
| Soft attention, always transfer | 27.60 | 27.20 | 27.93 | 0.750 | 5.67 | 0.0893 | 0.500 |
| Balanced FUGW (τ → ∞) | 27.60 | 27.23 | 27.90 | 0.750 | 5.69 | 0.0891 | 0.500 |
| **TRUST‑Diff (FUGW + reliability)** | 27.60 | 27.06 | **28.04** | 0.754 | 5.64 | **0.0786** | **0.741** |

Low‑resolution consistency: *e*<sub>LR</sub> = 1.67 × 10⁻² (Houston) and
6.9 × 10⁻³ (Pavia), identical for every variant to four digits. This is the
rank‑8 truncation residual of *X* and not a fitting error, exactly as
Proposition 1 predicts; it is unchanged by the reference, which is the empirical
content of the reference‑invariance claim.

### 2.2 What holds up

**The reliability map is real.** On Houston the transport mass separates
corresponding from non‑corresponding land cover with **AUROC 0.858** during
sampling and **0.915** when the region graph is built on the ground‑truth
target (mean *m* = 0.54 on corresponding regions against 0.24 on
non‑corresponding ones). The manuscript's Fig. 2 claims AUROC 0.91 with mean
*m* = 0.63 / 0.21 for exactly this hand‑crafted configuration with a coarse
geolocation prior. **That claim reproduces.** On Pavia the map is weaker
(AUROC 0.741) but better calibrated (ECE 0.084 against 0.196 on Houston, where
the map is systematically *under*‑confident).

**Abstention is what reduces hallucination — not the transport formulation.**
Argmax, soft attention and balanced FUGW all have AUROC 0.500 by construction
and land within 0.0012 of each other on RIH. Only the unbalanced coupling, which
can leave mass in the dustbin, moves the number: −19.8 % on Houston
(0.1138 → 0.0913) and −11.2 % on Pavia (0.0885 → 0.0786), together with
+0.22 dB and +0.13 dB inside Ω<sub>nc</sub>. This is Fig. 5/6's central claim and
it survives without any training.

**The range–null projection does its job.** Fig. 10 shows TRUST‑Diff tracking
the ground‑truth spectra on vegetation, a bright roof and asphalt while bicubic
and the argmax variant drift; SAM falls from 5.89° (bicubic) to 5.49°.

### 2.3 What does not hold up in this reduced setting

**Reference gain is negative for every reference‑based variant** — about
−0.4 dB on Houston and −0.6 dB on Pavia. This would falsify H1 and H5 if it were
a result about TRUST‑Diff; it is not. It is a result about the two substituted
components, and the diagnostics say so precisely.

Define the alignment score of a transported tensor field as
*mean<sub>p</sub> w(p) ψ<sup>T</sup>S(p)ψ*, weighted by target edge strength;
0.5 is chance and 1.0 is perfect. On Houston:

| Tensor field *S* | Valid region | Ω<sub>nc</sub> |
|---|---|---|
| The target's own MSI (oracle upper bound) | 0.940 | 0.936 |
| Reference sampled at the true per‑pixel location | 0.767 | 0.472 |
| …with one constant shift per region (integer) | **0.811** | 0.472 |
| …ignoring the 3 px thin‑plate‑spline warp | 0.536 | 0.471 |
| Pipeline with an **oracle region match** + shift refinement | 0.624 | 0.500 |
| Pipeline with hand‑crafted descriptors + FUGW | ≈ 0.59 | 0.50 |

Two things follow. First, **the region‑wise approximation of (11) is not the
problem** — one constant integer shift per superpixel loses nothing (0.811 vs
0.767; quantisation even helps by avoiding interpolation blur). Second, **a
three‑pixel localisation error destroys essentially all of the structural
information the reference carries** (0.767 → 0.536), and the hand‑crafted
descriptors cannot localise better than that.

And even a perfect reference would not buy much here: driving the sampler with
*S* built from the target's own perfectly registered MSI (alignment 0.940) gains
only **+0.10 dB** over the no‑reference baseline (30.39 → 30.49 at η = 0.02).
The contrast‑invariant energy only *orients* gradients; it cannot create
high‑frequency content. With the real ADM prior there is plausible detail to
orient, and the gain is worth having. With a guided filter there is almost
nothing to orient, so the guidance can only perturb. **The reference gain in
Figs. 5–6 cannot be regenerated without the real checkpoint.**

---

## 3. Three findings you should act on before submission

### 3.1 Equation (11) is under‑specified, and the gap is large

The similarity transform *T<sub>ij</sub>(p) = p<sub>j</sub> + (s<sub>j</sub>/s<sub>i</sub>) Q(Δθ<sub>ij</sub>)(p − p<sub>i</sub>)*
anchors the transported patch on the two superpixel centroids. Measured on
Houston, **the nearest reference superpixel centroid to a target region's true
counterpart is a median 4.99 px away** — and from the table above, 3 px is
already fatal. Unless the trained encoder produces region graphs whose
centroids coincide (which the manuscript does not claim and Fig. 2 does not
show), some sub‑region localisation step is doing real work in your
implementation and is missing from the paper. A reviewer who tries to
reimplement (11) as written will not reproduce Figs. 5–6.

In this run the gap is closed by one integer shift per accepted match, found by
FFT cross‑correlation of the target tensor field against the reference tensor
field over a window of radius 2 s<sub>i</sub>, normalised by the reference edge
energy. It refines the geometry of an already‑decided correspondence and touches
neither the coupling nor *m*. Median residual localisation error afterwards:
**0.80 px**. Recommend stating whatever the equivalent step is in your code, in
Sec. III‑G, with the 5 px measurement as its justification.

### 3.2 Δθ<sub>ij</sub> inherits the π‑ambiguity of θ

θ<sub>i</sub> is the structure‑tensor orientation, defined **modulo π** (Sec. III‑D‑1).
Sec. III‑D‑3 removes that ambiguity in the *descriptor*, by averaging the stem
features over the two canonical rotations — but Δθ<sub>ij</sub> = θ<sub>j</sub> − θ<sub>i</sub>
in (11) is still ambiguous by π, and *Q*(Δθ + π) = −*Q*(Δθ) rotates the sampled
patch by 180° about the centroid. The structure *tensor* is invariant to that
sign, so the rotation of *T<sup>Y</sup>* is unaffected and the bug is silent — but
the sampling grid is not, and the transported patch lands on the wrong pixels.
Wrapping Δθ into (−π/2, π/2] fixes it. Worth one sentence in Sec. III‑G.

### 3.3 The α sweep runs the wrong way, and H4 is the hypothesis at risk

At matched acceptance (the 190 most reliable regions in every variant, so the
subsets are comparable), on Houston:

| α | Wrong matches | Regions accepted at *m* > 0.5 | AUROC of *m* |
|---|---|---|---|
| 0.0 (unbalanced OT, no structure term) | **24.7 %** | 190 | **0.940** |
| 0.2 | 41.1 % | 265 | 0.931 |
| 0.5 (paper default) | 57.4 % | 292 | 0.897 |
| 0.8 | 65.8 % | 310 | 0.791 |

Monotone in both columns: the Gromov–Wasserstein structure term makes matching
*and* reliability worse, steadily, over the whole range. The manuscript's Fig. 15
reports the opposite direction (45.3 % → 9.1 % wrong as the structure term is
switched on), and H4 predicts a gain under non‑rigid warps.

I would not read this as falsifying H4. With hand‑crafted descriptors the feature
cost is weak (node‑level min‑cost AUROC 0.585), so the linearised GW term
dominates the fused cost and propagates the feature cost's errors through the
neighbourhood structure; a trained encoder may well invert the ordering. But the
sweep is clean enough that it is worth re‑running on your side at
α ∈ {0, 0.2, 0.5, 0.8} with the trained encoder and reporting the curve, because
it is exactly the ablation a referee will ask for, and Fig. 15 currently reports
a single point rather than a trend — and at unmatched acceptance rates, which is
not a fair comparison (argmax accepts 958 regions here, FUGW 292; comparing their
raw error rates compares different subsets).

---

## 4. Datasets removed, and what replaced the figures

Chikusei and XDU-Liyukou are gone from the manuscript: from the abstract, Table II,
Tables V–VI, IX, XI, XIII and XVI, the hypothesis table, every body paragraph and
the acknowledgment. Tables VII and VIII (the XDU-Liyukou pair) are deleted outright,
as are Figs. 7, 8, 9 and 12. The surviving figures are renumbered 1–15 with every
cross-reference updated. Reference [41] now cites Indian Pines in place of Chikusei.
Houston and Pavia keep the numbers you measured; nothing in any table was invented.

Indian Pines (145 × 145 × 200) is used only for the downstream-classification
experiment. It cannot be a third super-resolution dataset: the whole scene is
smaller than one 256² target tile, so it cannot carry a target plus a larger
disjoint reference under the protocol of Sec. V-A.

## 5. New measurements from this round

### 5.1 The ζ sweep (Fig. 8, was Fig. 11)

Six values of ζ on Houston, against a single no-reference baseline — the target and
its LR observation do not depend on ζ, so RG = PSNR(Y) − PSNR(A0) is exact.

| ζ | 0.0 | 0.1 | 0.2 | 0.4 | 0.6 | 0.8 |
|---|---|---|---|---|---|---|
| RIH, argmax | 0.114 | 0.116 | 0.114 | 0.109 | 0.104 | 0.099 |
| **RIH, TRUST-Diff** | **0.073** | **0.078** | **0.088** | **0.094** | **0.095** | **0.095** |
| RG, TRUST-Diff (dB) | −0.37 | −0.36 | −0.40 | −0.40 | −0.42 | −0.44 |

TRUST-Diff holds the lowest hallucination and the least negative reference gain at
every ζ, converging on the always-transfer rules only at ζ = 0.8, where four fifths
of the reference has no counterpart and there is little left to abstain from. The
**ordering** the method predicts reproduces; the **sign** of the gain does not,
for the reasons in Sec. 2.3 — so H1 still rests on Table IX, not on this figure.

### 5.2 H2 is confirmed, on both scenes (Fig. 13, was Fig. 17)

Proposition 2 predicts that transfer into non-corresponding regions decays at rate
1/(τ + ε). Lowering either parameter should lower RIH. It does, monotonically, on
both scenes:

| | τ = 0.05 | 0.10 | 0.15 | 0.30 | | ε = 0.05 | 0.10 | 0.20 |
|---|---|---|---|---|---|---|---|---|
| Houston | 0.0862 | 0.0894 | 0.0913 | 0.0919 | | 0.0873 | 0.0913 | 0.0950 |
| Pavia | 0.0756 | 0.0774 | 0.0786 | 0.0797 | | 0.0785 | 0.0786 | 0.0794 |

Eight of eight steps run in the predicted direction. This is the one theoretical
claim in the paper that reproduces **cleanly** without the trained encoder or the
real prior, because it concerns the transport, not the image model.

### 5.3 Cost scaling (Fig. 14, was Fig. 18)

Reference size grows 4.1× (65,536 → 268,032 px), median of seven timings each:

| | side 256 | 384 | 512 | 640 | 768 | growth |
|---|---|---|---|---|---|---|
| candidate-set query (s) | 0.180 | 0.231 | 0.229 | 0.211 | 0.195 | **×1.08** |
| score every node (s) | 0.034 | 0.041 | 0.066 | 0.086 | 0.093 | ×2.7 |
| index build (s) | 3.3 | 7.5 | 12.5 | 15.9 | 19.3 | ×5.8, linear |

The candidate query is **flat in N_Y** and exhaustive scoring is **linear** — exactly
the scaling Sec. V-I claims. They have not crossed at these sizes, because the index
carries a fixed construction cost that dominates while the reference is small;
extrapolating the two fits, they cross near N_Y ≈ 6 × 10⁵ px. I did **not** plot a
speed-up over MFME-DiffNet, which cannot be run here — the figure establishes
scaling, not a ratio, and its caption says so.

### 5.4 Downstream classification is a negative result (Fig. 15, was Fig. 19)

This one does not work, and the reason is the scene rather than the methods.

| | OA (%) | OA inside Ω_nc (%) |
|---|---|---|
| HR ground truth | 88.3 | 87.6 |
| Bicubic | 90.4 | 89.0 |
| No-reference (A0) | **91.2** | 91.2 |
| Argmax, always transfer | 73.0 | 78.2 |
| TRUST-Diff | 73.3 | **79.8** |

Bicubic and the no-reference sampler both score **above the ground truth**. At a 20 m
ground sampling distance over large homogeneous fields there is no fine spatial
structure for a classifier to reward, and spatial smoothing is a well-known benefit
on Indian Pines — so the task measures smoothness, not resolution. Reference transfer
costs ~18 points because texture written into the null space perturbs the spectra the
classifier reads, which is a real caution about unconditional transfer but not a test
of super-resolution.

The one comparison that behaves as the method predicts is inside Ω_nc: **79.8 % for
TRUST-Diff against 78.2 % for unconditional transfer**, +1.6 points from abstention
alone.

I tried Houston first, since Fig. 19 was a Houston figure and Houston has the spatial
structure this experiment needs. Its released `mask_train.mat` carries **2,832 labelled
pixels in the whole 349 × 1905 scene and only 255 inside the 256² test crop**, across
8 classes with one class at 4 pixels — too few to train and evaluate on. Sec. V-J now
says this plainly and leaves the proper experiment to future work.

**Recommendation:** if you want a positive downstream result, the cleanest route is the
full Houston 2013 GRSS ground truth (15 classes, ~15,000 labelled pixels), not the
training mask. Send that and I will redo Fig. 15 on Houston, where sharpening genuinely
helps. Otherwise consider deleting Sec. V-J — a negative result on a scene that cannot
support the test invites a reviewer question you gain nothing by answering.

## 6. Figures

All eleven are 7.16 in wide (IEEE double column), vector PDF plus 600 dpi PNG,
Type-42 fonts. New numbering in parentheses.

| File | Manuscript | Content |
|---|---|---|
| `fig04_cnc_construction` | Fig. 4 | CNC-Bench construction on the real cubes; ζ sweep of references and masks. |
| `fig05_houston_qualitative` | Fig. 5 | Houston: result, valid/invalid ROI zooms, residual, residual ROI zoom, six variants. |
| `fig06_pavia_qualitative` | Fig. 6 | Pavia, same layout. |
| `fig10_spectral_fidelity` | **Fig. 7** | Spectra at three homogeneous probes plus SAM maps. |
| `fig11_cnc_sweep` | **Fig. 8** | ζ sweep: PSNR, RIH, reference gain. |
| `fig13_reliability` | **Fig. 10** | ROC, reliability diagram, RIH bars, both scenes. |
| `fig14_ablation` | **Fig. 11** | Ablation dot plot, drawn from Table XIII so figure and table agree. |
| `fig15_correspondence` | **Fig. 12** | Argmax / unbalanced OT / full FUGW at equal acceptance. |
| `fig17_parameters` | **Fig. 13** | k, T, ε, τ sweeps; the τ and ε columns test H2. |
| `fig18_runtime` | **Fig. 14** | Per-refresh matching cost and one-off index build vs N_Y. |
| `fig19_classification` | **Fig. 15** | Indian Pines classification maps and confusion matrix. |

Figs. 1, 2, 3, 9 (noise robustness) and Fig. 16's successor keep your original panels —
they were outside the agreed scope, and the encoder training curves cannot be
regenerated without a trained encoder.

Colour follows one validated palette throughout: categorical slots blue `#2a78d6`,
orange `#eb6834`, aqua `#1baf7a` — the three-slot set that clears the all-pairs CVD and
normal-vision separation floors — with single-hue sequential ramps for residual and
reliability maps and no rainbow anywhere. Every series is directly labelled.

## 7. Drop-in captions

**Fig. 5.** Visualization results on the Houston tile. Rows, top to bottom:
reconstruction; a zoom of the valid ROI (aqua); a zoom of the invalid ROI
(orange), which lies inside the replaced region; the mean absolute residual over
the whole tile; and the residual inside the invalid ROI, all residuals on a shared
scale per row. Columns: ground truth and six variants that share one sampler, one
frozen prior and one range–null projection, and differ only in how the reference
is transferred. The side column gives the unpaired reference with the target
footprint outlined, the reliability map *m*, and the true non‑correspondence mask
Ω<sub>nc</sub> (44 % of the tile). Argmax matching, soft attention and the balanced
coupling all transfer unconditionally: they inject speckled texture across the
invalid ROI, visible as a raised, structured residual in the bottom row, and they
score RIH 0.114, 0.115 and 0.115 with a reliability AUROC of 0.500 by
construction. TRUST‑Diff's transport mass collapses there, giving RIH 0.091
(−19.8 %), 29.46 dB inside Ω<sub>nc</sub> against 29.22–29.24 dB for the three
always‑transfer variants, and AUROC 0.858. Low‑resolution consistency is
1.67 × 10⁻² for every variant — the rank‑8 truncation residual of *X*, unchanged
by the reference, as Proposition 1 requires. The no‑reference column is the
highest‑PSNR column here: with the plug‑and‑play prior that stands in for the
frozen ADM (Sec. S‑F) there is little high‑frequency content for the
contrast‑invariant likelihood to orient, so every reference‑based variant loses
about 0.4 dB overall. The comparison this figure supports is therefore *between
transfer rules*, not against the published baselines.

**Fig. 6.** Visualization results on the Pavia tile, same layout. The reference is
a larger, partially overlapping window with a different radiometry and 25 % of its
area replaced, so 58 % of the target has no valid counterpart. The reliability map
is low over most of the scene and follows the superpixel boundaries of the urban
blocks; AUROC is 0.741, lower than on Houston but better calibrated
(ECE 0.084 against 0.196). RIH falls from 0.0885 / 0.0893 / 0.0891 for the three
always‑transfer variants to 0.0786 for TRUST‑Diff, and PSNR inside
Ω<sub>nc</sub> rises from 27.90–27.93 dB to 28.04 dB.

---

## 8. Reproducing

```
trustdiff/prep.py      cube loading, Wald protocol, SRFs, TPS warp, blobs, masks
trustdiff/cases.py     the two scene definitions (crop rectangles)
trustdiff/ops.py       degradation operator, CG pseudo-inverse, subspace, PnP prior
trustdiff/matching.py  region graphs, contrast-invariant descriptors, FUGW Sinkhorn
trustdiff/pcm.py       PCM-Refresh, reliability, structure-tensor transport
trustdiff/solver.py    Algorithm 1 with the reference likelihood and its gradient
trustdiff/metrics.py   PSNR/SSIM/SAM/ERGAS/CC/RMSE, e_LR, RIH, ECE
trustdiff/run.py       runs all six variants on both scenes  ->  out/*.pkl
trustdiff/render.py    every figure                          ->  figures/*.{pdf,png}
```

```bash
pip install h5py scikit-image scikit-learn scipy matplotlib
python run.py both        # ~25 min on 2 CPU cores
python render.py all
```

Point `DATA` in `prep.py` at the unpacked archives. The run is deterministic; no
random seed is drawn during sampling, so `Z(Y)` and `Z(Y∅)` share the trajectory
that RIH requires.

---

## 9. Springer conversion (Pattern Analysis and Applications)

I could not read `link.springer.com/journal/10044/submission-guidelines`: the fetch
proxy refused it (HTTP 429) and instructed me not to retry. The conversion below
follows Springer Nature's standard requirements — **please check the live page for
anything journal-specific.**

**What changed**

| Item | Before | After |
|---|---|---|
| Section numbering | `I.` / `A.` / `1)` | `1` / `1.1` / `1.1.1` — 47 headings |
| Section cross-refs | `Sec. III-G` | `Sect. 3.7` — 38 references |
| Table numbers | Roman, with a gap at VII–VIII | Arabic **1–14**, consecutive |
| Table captions | `TABLE I. Text` | `Table 1 Text`, above the table |
| Figure captions | `Fig. 1. Text` | `Fig. 1 Text` |
| References | IEEE, `[1] F. Yang, …, "Title," in Proc.` | Springer numbered, `1. Yang F, … (2020) Title. In: Proc …` |
| Front matter | `[Author Names], [Affiliations]` | Title page with authors, affiliations, corresponding author, ORCID |
| Abstract | 250 words, dense | 230 words, plain language, one paragraph |
| `Index Terms` | IEEE | `Keywords`, six terms, `·` separated |
| Running head | `IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING` | article short title |
| Highlighting | 1,106 highlighted runs | none |
| Declarations | absent | **Statements and Declarations** with seven required statements |

**Added content:** an explicit *Problem statement* paragraph and a *What is new*
paragraph in the Introduction, before the contributions list.

**Equations.** No conversion was needed — the manuscript's 17 display equations and
454 inline expressions were **already real Word (OMML) objects**. The flattened look
in a text dump is an artefact of stripping XML tags. I added 37 more inline
equations where my earlier edits had left literal underscore notation
(`Ω_nc`, `e_LR`, `N_Y`, …), rendered through the same OMML format. Final counts:
17 display, 508 inline, all schema-valid.

**The PDF preview drops the mathematics.** LibreOffice, which renders the preview
here, does not import OMML. I verified this is not a defect I introduced by running
the untouched original through the same pipeline — it loses its equations
identically. **The .docx is correct; open it in Word to see the mathematics.**

**Consistency audit, final state**

- 15 figures, all captioned and all cited; 15 images embedded
- 14 tables, all captioned and all cited, numbered consecutively
- 17 numbered equations
- 47 references; **[42] (XDU-Liyukou) is now uncited** — see below
- No Roman table or section citations remain; no highlighting; no dataset leftovers

**Two things you must decide**

1. **Reference [42]** is uncited since XDU-Liyukou was removed. Delete it and
   renumber [43]–[47], or keep and cite it. I did not renumber: it touches every
   in-text citation and the risk outweighed the benefit without your say-so.
2. **AI-use disclosure.** Springer Nature requires authors to disclose use of large
   language models in manuscript preparation. This manuscript was edited and its
   figures generated with AI assistance. I have **not** written a disclosure
   statement, and I have not written that none was used — that statement is yours
   to make, and it would be false for me to assert the latter.
