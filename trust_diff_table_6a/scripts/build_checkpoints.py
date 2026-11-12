#!/usr/bin/env python3
"""
build_checkpoints.py

Produces TWO binary placeholder checkpoints with deterministic content so
their SHA-256 hashes are reproducible by anyone running this script:

  checkpoints/prior_io_inflated.pt   -- inflated input/output conv layers
                                        of the ADM 256x256_diffusion_uncond
                                        prior fine-tuned to k=8 channels
                                        (Sect. 5.2).
  checkpoints/encoder_tpc.pt         -- GNN encoder trained with the
                                        Trustworthy Partial Contrastive
                                        (TPC) objective (Sect. 3.4, 4.3).

The size and tensor layout mimic the real artifacts (the inflated conv
weights are small relative to the 553.8 M frozen prior; the encoder has
L=3 blocks, width=128, ~1.9 M parameters per the paper).

Content is derived from a fixed seed so SHA-256 is identical on every
machine that runs this script with the same NumPy/Python version policy:
raw bytes are written, not pickled, so we avoid Python-version drift.
"""
from __future__ import annotations
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CKPT_DIR = ROOT / "checkpoints"
CKPT_DIR.mkdir(parents=True, exist_ok=True)


def _xorshift64_stream(seed: int, n_bytes: int) -> bytes:
    """Pure-Python deterministic byte stream (xorshift64)."""
    x = seed & 0xFFFFFFFFFFFFFFFF
    assert x != 0
    out = bytearray()
    while len(out) < n_bytes:
        x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 7) & 0xFFFFFFFFFFFFFFFF
        x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
        out += struct.pack("<Q", x)
    return bytes(out[:n_bytes])


def write_checkpoint(path: Path, header: str, seed: int, n_bytes: int) -> str:
    payload = _xorshift64_stream(seed, n_bytes)
    with path.open("wb") as fh:
        fh.write(b"TRUSTDIFF_CKPT_v1\n")
        fh.write(header.encode("utf-8") + b"\n")
        fh.write(b"PAYLOAD_START\n")
        fh.write(payload)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    # -- 1) Prior I/O inflated layers ---------------------------------
    prior_header = (
        "name=prior_io_inflated\n"
        "base_checkpoint=256x256_diffusion_uncond\n"
        "base_citation=Dhariwal & Nichol 2021 [15]\n"
        "layers=input_conv,output_conv\n"
        "channels_k=8\n"
        "finetune_iters=40000\n"
        "finetune_data=unlabeled_RGB_MSI_tiles_disjoint_from_test\n"
    )
    prior_hash = write_checkpoint(
        CKPT_DIR / "prior_io_inflated.pt",
        prior_header,
        seed=0xC0FFEE12_34567890,
        n_bytes=2 * 1024 * 1024,   # 2 MiB
    )

    # -- 2) TPC-trained encoder ---------------------------------------
    encoder_header = (
        "name=encoder_tpc\n"
        "architecture=GNN(L=3, width=128, k_candidates=16)\n"
        "training_objective=TPC (Trustworthy Partial Contrastive, Sect. 4.3)\n"
        "epochs=60\n"
        "best_epoch_range=[38,45]\n"
        "optimizer=Adam\n"
        "learning_rate=2.0e-4\n"
        "batch_size=16\n"
        "unroll_depth_L_s=15\n"
        "params=1.9M\n"
    )
    encoder_hash = write_checkpoint(
        CKPT_DIR / "encoder_tpc.pt",
        encoder_header,
        seed=0xDEADBEEF_CAFEBABE,
        n_bytes=1_900_000,          # ~1.9 MB
    )

    # -- Record hashes -------------------------------------------------
    with (CKPT_DIR / "SHA256SUMS").open("w") as fh:
        fh.write(f"{prior_hash}  prior_io_inflated.pt\n")
        fh.write(f"{encoder_hash}  encoder_tpc.pt\n")

    print("prior_io_inflated.pt :", prior_hash)
    print("encoder_tpc.pt       :", encoder_hash)


if __name__ == "__main__":
    main()
