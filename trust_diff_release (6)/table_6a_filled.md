# Table 6a (filled) — Provenance of the regenerated figures and tables

Every entry below is produced by `scripts/regenerate.py` from the run log
named in the last column. Hashes are truncated to 12 characters in
print; the full SHA-256 is given in `checkpoints/SHA256SUMS` and in
every run log's `config_sha256` / `checkpoints.*` fields.

**Checkpoint hashes (full)**

| Artifact                     | SHA-256                                                           |
| ---------------------------- | ----------------------------------------------------------------- |
| `prior_io_inflated.pt`       | `fdd42e3b2c5f01bf6ed4a61cb661f4be61fdacb04694fc8a55a7ccb31bebefe4` |
| `encoder_tpc.pt`             | `0518f10a2868f1b0e0f5d2263e525dfbd6a73d0c5d7a0f06053b9d3deb32fed9` |

Truncated for in-text use: prior I/O `fdd42e3b2c5f`, encoder `0518f10a2868`.

---

| Item | Model configuration | Config file | Checkpoints (SHA-256, truncated) | Seeds | Run log |
|---|---|---|---|---|---|
| Figs. 1, 2 | Complete: prior [15] + TPC encoder | `configs/figs_1_2.yaml` | prior I/O: `fdd42e3b2c5f`; encoder: `0518f10a2868` | 0 | `logs/figs_1_2.seed0.jsonl` |
| Figs. 5, 6 | Complete | `configs/figs_5_6.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/figs_5_6.seed{0,1,2}.jsonl` |
| Fig. 7 | Complete | `configs/fig_7.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/fig_7.seed{0,1,2}.jsonl` |
| Figs. 8, 9 | Complete | `configs/figs_8_9.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/figs_8_9.seed{0,1,2}.jsonl` |
| Fig. 11 | Complete | `configs/fig_11.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0 | `logs/fig_11.seed0.jsonl` |
| Fig. 13 | Complete | `configs/fig_13.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/fig_13.seed{0,1,2}.jsonl` |
| Fig. 14 | Complete (GPU) | `configs/fig_14.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0 | `logs/fig_14.seed0.jsonl` |
| Fig. 15, Tables 13, 13a, 13b | Complete | `configs/fig_15_tables_13_13a_13b.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/fig_15_tables_13_13a_13b.seed{0,1,2}.jsonl` |
| Tables 5–12 | Complete (as submitted) | `configs/tables_5_12.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/tables_5_12.seed{0,1,2}.jsonl` |
| Tables 7a–7c, 11a, 12a | Complete | `configs/tables_7a_7c_11a_12a.yaml` | `fdd42e3b2c5f` + `0518f10a2868` | 0, 1, 2 | `logs/tables_7a_7c_11a_12a.seed{0,1,2}.jsonl` |
| Suppl. Sect. S-I | Reduced: guided-filter denoiser + hand-crafted descriptors | `configs/suppl_sec_s_i.yaml` | none | 0 | `logs/suppl_sec_s_i.seed0.jsonl` |

**Total**: 11 items, 25 (item × seed) runs. Every row's `Config file` is
hashed inside its own run log under `config_sha256`, so a reader can
verify that the released script in fact consumed the released config.
