# TRUST-Diff

Reference implementation for *TRUST-Diff: structure-aware partial-correspondence
posterior diffusion for unpaired reference-based hyperspectral image
super-resolution*.

TRUST-Diff sharpens a low-resolution hyperspectral image with a high-resolution
multispectral image that is **not** registered to it, may cover a different
extent, and may show land cover that has changed. The correspondence between the
two images is a latent variable estimated inside the sampler as an unbalanced
optimal-transport plan, so a region is allowed to have **no** counterpart; the
mass left unassigned is read directly as a per-region reliability map, with no
separate change detector. The reference is confined to the null space of the
degradation operator, so the measured spectra are preserved by construction.

---

## What this repository does and does not reproduce

Please read this section before comparing anything to the article.

**Reproduced by this code, end to end, from the public cubes:**

| Article figure | Command |
| --- | --- |
| Figs. 1–3, the three schematics | `python -m trustdiff capture && python -m trustdiff figures --which schematics` |
| Fig. 4, CNC-Bench construction | `python -m trustdiff figures --which fig04` |
| Figs. 5–6, visual comparisons | `python -m trustdiff run && python -m trustdiff figures --which fig05 fig06` |
| Fig. 7, spectral fidelity | `python -m trustdiff figures --which fig07` |
| Fig. 8, CNC-Bench sweep | `python -m trustdiff sweep-zeta && python -m trustdiff figures --which fig08` |
| Fig. 9, reliability as a detector | `python -m trustdiff figures --which fig09` |
| Figs. 10–11, ablation and correspondences | `python -m trustdiff figures --which fig10 fig11` |
| Fig. 13, parameter sensitivity | `python -m trustdiff sweep-params && python -m trustdiff figures --which fig13` |
| Fig. 14, cost against reference size | `python -m trustdiff runtime && python -m trustdiff figures --which fig14` |
| Fig. 15, downstream classification | `python -m trustdiff classify && python -m trustdiff figures --which fig15` |

Figure 12 is the authors' own convergence schematic and is not generated here.
Every file is written as a 600 dpi `.png` and a vector `.pdf`, named for the
figure number it carries in the article.

**Not reproduced by this code.** Tables 5–14 of the article are the authors'
own measurements under their full configuration and are *not* produced here.
Two components of that configuration are unavailable in a public checkout and
are substituted, which the article calls the *reduced setting* (Sect. 5.5.3):

1. the frozen 553.8 M-parameter ADM image prior is replaced by a guided-filter
   plug-and-play denoiser (`ops.pnp_denoise`);
2. the trained GNN encoder is replaced by hand-crafted contrast-invariant
   descriptors (`matching.canonical_descriptors`).

Everything else — the spectral subspace, the exact range–null projection, the
region graphs and reference pyramid, the fused unbalanced Gromov–Wasserstein
coupling, the reliability map, the contrast-invariant structure-tensor
likelihood and its projected gradient step — is the method as specified.

Because the prior is weaker, **reference gain is negative in this setting** for
every reference-based variant, by about 0.4 dB on Houston and 0.6 dB on Pavia.
The figures produced here say so on their faces. What does reproduce without
any training is the behaviour the article is actually about: the reliability map
separates corresponding from non-corresponding regions, and only the unbalanced
coupling lowers the hallucination score. Do not read the absolute PSNR values
from this repository as the article's results.

---

## Install

```bash
git clone https://github.com/<owner>/trust-diff.git
cd trust-diff
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Python 3.9 or newer. The dependencies are NumPy, SciPy, scikit-image,
scikit-learn and Matplotlib; the exact versions used for the article are pinned
in `requirements-lock.txt`.

## Data

Three public scenes are used. None is redistributed here; `data/README.md` gives
the source of each one and the layout the loaders expect:

```
data/
  houston/data.mat              Houston 2013, CASI, 349 x 1905 x 144
  pavia/PaviaU.mat              Pavia University, ROSIS, 610 x 340 x 103
  indian/indianpinearray.npy    Indian Pines, AVIRIS, 145 x 145 x 200
  indian/IPgt.npy               its 16-class ground truth
```

Set `TRUSTDIFF_DATA` if the cubes live elsewhere.

## Quick start

```bash
python -m trustdiff run --scene houston     # ~4 min on one core
python -m trustdiff figures --which fig05
```

Results are cached under `results/` and figures written to `figures/` at
600 dpi. Both locations are configurable; see `src/trustdiff/paths.py`.

## Using the method on your own pair

```python
import numpy as np
from trustdiff import pcm, solver

case = dict(
    hr=None,                 # only needed if you want full-reference metrics
    lr=lr,                   # (C, h, w) low-resolution hyperspectral
    y=y,                     # (c, H_y, W_y) high-resolution multispectral
    ratio=4,
    wl=wavelengths,          # (C,)
    R_true=R,                # (c, C) nominal spectral response
    tgt_rect=(ty, tx, H, W), # target window in scene coordinates
    ref_rect=(ry, rx, Hy, Wy),
)
ref = pcm.ReferenceGraph(case["y"], origin=case["ref_rect"][:2], n_segments=2600)
out = solver.sample(case, mode="trust", refg=ref, T=100, k=8)
z, reliability = out["Z"], out["m"]
```

`mode` selects the transfer rule and is the axis every comparison in the article
varies: `noref`, `argmax`, `softattn`, `balanced`, `trust`.

## Repository layout

```
src/trustdiff/
  ops.py          degradation operator, spectral subspace, range-null projection,
                  plug-and-play prior
  prep.py         cube loading, Wald protocol, spectral responses, warps,
                  radiometric perturbation, CNC-Bench construction
  matching.py     normalised gradients, structure tensors, region graphs,
                  canonical descriptors, the FUGW solver and reliability
  pcm.py          the reference pyramid and one matching refresh
  solver.py       Algorithm 1: the sampler, with an observation hook
  cases.py        the three evaluation cases
  metrics.py      PSNR, SSIM, SAM, ERGAS, CC, RMSE, RIH, ECE
  run.py          every variant on a scene
  render.py       the result figures
  schematics.py   Figs. 1-3
  capture.py      the real intermediates the schematics show
tests/            the properties the implementation must satisfy
docs/             reproduction notes and the figure map
```

## Tests

```bash
pip install pytest
pytest -q
```

The tests check the properties the method rests on rather than fixed outputs:
that the degradation adjoint is a true adjoint, that the range–null projection
reproduces the observation exactly, that the transport plan abstains as the
mass-abstention parameter falls and becomes balanced as it grows, that the edge
features are invariant to translation, rotation and scale, and that the analytic
gradient of the reference energy agrees with a finite-difference estimate. The
last one is a regression test: an extra negation there once made the guidance
*ascend* the energy.

## Citation

See `CITATION.cff`.

## Licence

MIT, see `LICENSE`. The datasets are governed by their own terms, linked in
`data/README.md`.
