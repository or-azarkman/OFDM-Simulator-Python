"""
Smoke validation run: load YAML spec → measure EVM/BER → PASS/FAIL → JSON report.

From project root:

  py simulations/validation_runs/run_validation_smoke.py
  py simulations/validation_runs/run_validation_smoke.py --config configs/validation/default_smoke.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _ensure_path() -> None:
    import os

    os.chdir(PROJECT_ROOT)
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    _ensure_path()

    parser = argparse.ArgumentParser(description="OFDM validation smoke run (EVM/BER vs thresholds)")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/validation/default_smoke.yaml",
        help="Path to validation YAML (relative to project root)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output JSON path (default: results/validation/validation_report_<timestamp>.json)",
    )
    args = parser.parse_args()

    from src.measurements.ofdm_metrics import measure_awgn_cfo_once
    from src.validation.evaluate import evaluate_metrics, load_spec_from_yaml, report_to_dict

    cfg_path = PROJECT_ROOT / args.config
    spec = load_spec_from_yaml(cfg_path)
    sc = spec.scenario

    fft_size = int(sc.get("fft_size", 64))
    cp_len = int(sc.get("cp_len", 16))
    num_symbols = int(sc.get("num_symbols", 400))
    modulation = str(sc.get("modulation", "QPSK"))
    snr_db = float(sc.get("snr_db", 18.0))
    cfo = float(sc.get("cfo_subcarrier_fraction", 0.0))
    seed = sc.get("seed", 42)
    seed = int(seed) if seed is not None else None
    cfo_correction = bool(sc.get("cfo_correction", False))

    metrics = measure_awgn_cfo_once(
        fft_size=fft_size,
        cp_len=cp_len,
        num_symbols=num_symbols,
        modulation=modulation,
        snr_db=snr_db,
        cfo_subcarrier_fraction=cfo,
        seed=seed,
        cfo_correction=cfo_correction,
    )

    report = evaluate_metrics(metrics, spec)
    for line in report.summary_lines():
        print(line)

    out_dir = PROJECT_ROOT / "results" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = Path(args.out) if args.out else out_dir / f"validation_report_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": str(cfg_path.relative_to(PROJECT_ROOT)),
        "report": report_to_dict(report),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved: {out_path}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
