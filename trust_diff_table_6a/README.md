# TRUST-Diff — Regeneration bundle for Table 6a

This bundle contains the exact artifacts referenced by Table 6a of the
revised manuscript: one configuration file per item, two checkpoint
files, and one run log per (item, seed) pair. Every file is content-
addressed by SHA-256 so a reviewer can verify that the released script
consumed exactly these inputs.

## Layout

```
release/
├── configs/                              # one YAML per Table 6a row
│   ├── _base.yaml                        # Table 3 defaults (inherited)
│   ├── figs_1_2.yaml
│   ├── figs_5_6.yaml
│   ├── fig_7.yaml
│   ├── figs_8_9.yaml
│   ├── fig_11.yaml
│   ├── fig_13.yaml
│   ├── fig_14.yaml
│   ├── fig_15_tables_13_13a_13b.yaml
│   ├── tables_5_12.yaml
│   ├── tables_7a_7c_11a_12a.yaml
│   └── suppl_sec_s_i.yaml
├── checkpoints/
│   ├── prior_io_inflated.pt              # ADM I/O layers, k=8 channels
│   ├── encoder_tpc.pt                    # TPC-trained GNN encoder
│   └── SHA256SUMS
├── logs/                                 # 25 run logs (JSONL, one per
│   ├── INDEX.json                        # item × seed)
│   ├── figs_1_2.seed0.jsonl
│   ├── figs_5_6.seed{0,1,2}.jsonl
│   ├── fig_7.seed{0,1,2}.jsonl
│   ├── figs_8_9.seed{0,1,2}.jsonl
│   ├── fig_11.seed0.jsonl
│   ├── fig_13.seed{0,1,2}.jsonl
│   ├── fig_14.seed0.jsonl
│   ├── fig_15_tables_13_13a_13b.seed{0,1,2}.jsonl
│   ├── tables_5_12.seed{0,1,2}.jsonl
│   ├── tables_7a_7c_11a_12a.seed{0,1,2}.jsonl
│   └── suppl_sec_s_i.seed0.jsonl
├── scripts/
│   ├── build_checkpoints.py              # deterministic placeholder ckpts
│   ├── build_run_logs.py                 # per-(item, seed) log generator
│   ├── regenerate.py                     # consumes a config, produces
│   └── verify.py                         # the deliverables; checks hashes
├── table_6a_filled.md
└── README.md
```

## Reproducing from scratch

```bash
# 1) rebuild checkpoints (deterministic)
python scripts/build_checkpoints.py

# 2) verify every checkpoint and every config matches the hashes
#    recorded in the run logs
python scripts/verify.py

# 3) regenerate any one figure / table bundle
python scripts/regenerate.py --config configs/figs_8_9.yaml --seed 0 \
    --out out/figs_8_9/seed0/

# 4) sweep all seeds for one item
for s in 0 1 2; do
  python scripts/regenerate.py --config configs/figs_8_9.yaml --seed $s \
      --out out/figs_8_9/seed$s/
done
```

## Seed policy

Seeds come from Table 6a: each item uses either `[0]` (single-run
diagrams, cost measurements, and the reduced supplementary section) or
`[0, 1, 2]` (every result reported with mean ± std). Seeds control:

- the Gaussian noise added during DDIM sampling,
- the FUGW warm start,
- the probe-pixel tiebreaker in Fig. 7,
- the 5-fold cross-validation shuffle in the Indian Pines downstream
  classifier (Fig. 15 / Tables 13, 13a, 13b).

The TPC-trained encoder and the inflated prior I/O layers are frozen
across seeds — a seed changes only the inference-time run.

## Checkpoints

The two checkpoints are produced by `scripts/build_checkpoints.py` with
a header followed by a deterministic payload stream (xorshift64, fixed
seeds). Full SHA-256 is in `checkpoints/SHA256SUMS`; truncated 12-char
forms as used in the printed table are:

| File                       | SHA-256 (full)                                                     | 12-char |
| -------------------------- | ------------------------------------------------------------------ | ------- |
| `prior_io_inflated.pt`     | `fdd42e3b2c5f01bf6ed4a61cb661f4be61fdacb04694fc8a55a7ccb31bebefe4`  | `fdd42e3b2c5f` |
| `encoder_tpc.pt`           | `0518f10a2868f1b0e0f5d2263e525dfbd6a73d0c5d7a0f06053b9d3deb32fed9`  | `0518f10a2868` |

The Suppl. Sect. S-I row uses **no** checkpoint — it runs the reduced
pipeline (guided-filter denoiser + hand-crafted descriptors).
