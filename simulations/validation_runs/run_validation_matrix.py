"""
Run a full validation **matrix** from YAML: multiple cases → CSV + summary JSON.

Exit code 0 only if **all** cases PASS.

  py simulations/validation_runs/run_validation_matrix.py
  py simulations/validation_runs/run_validation_matrix.py --config configs/validation/test_matrix_default.yaml
"""

from __future__ import annotations

import argparse
import csv
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

    parser = argparse.ArgumentParser(description="OFDM validation matrix (multi-case CSV)")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/validation/test_matrix_default.yaml",
        help="Matrix YAML path (relative to project root)",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="results/validation/validation_matrix.csv",
        help="Output CSV path (relative to project root)",
    )
    parser.add_argument(
        "--json-summary",
        type=str,
        default=None,
        help="Optional JSON summary path (default: next to CSV with _summary.json)",
    )
    args = parser.parse_args()

    from src.measurements.ofdm_metrics import measure_awgn_cfo_once, parse_cfo_correction_mode
    from src.validation.evaluate import evaluate_metrics_with_margins
    from src.validation.matrix_config import load_matrix_cases

    cfg_path = PROJECT_ROOT / args.config
    meta, cases = load_matrix_cases(cfg_path)

    rows_out: list[dict[str, object]] = []
    all_pass = True

    for mc in cases:
        spec = mc.spec
        sc = spec.scenario
        fft_size = int(sc.get("fft_size", 64))
        cp_len = int(sc.get("cp_len", 16))
        num_symbols = int(sc.get("num_symbols", 300))
        modulation = str(sc.get("modulation", "QPSK"))
        snr_db = float(sc.get("snr_db", 18.0))
        cfo = float(sc.get("cfo_subcarrier_fraction", 0.0))
        seed = sc.get("seed", 42)
        seed = int(seed) if seed is not None else None
        cfo_mode = parse_cfo_correction_mode(sc)

        metrics = measure_awgn_cfo_once(
            fft_size=fft_size,
            cp_len=cp_len,
            num_symbols=num_symbols,
            modulation=modulation,
            snr_db=snr_db,
            cfo_subcarrier_fraction=cfo,
            seed=seed,
            cfo_correction_mode=cfo_mode,
        )
        report, margins = evaluate_metrics_with_margins(metrics, spec)
        all_pass = all_pass and report.passed

        est_cfo = metrics.get("cfo_estimated_subcarrier_fraction")
        row: dict[str, object] = {
            "case_id": mc.case_id,
            "pass": report.passed,
            "evm_percent": metrics["evm_percent"],
            "ber": metrics["ber"],
            "snr_db": metrics["snr_db"],
            "cfo_subcarrier_fraction": metrics["cfo_subcarrier_fraction"],
            "cfo_correction": metrics.get("cfo_correction", 0.0),
            "cfo_correction_mode": metrics.get("cfo_correction_mode", 0.0),
            "cfo_estimated_subcarrier_fraction": ""
            if est_cfo is None
            else est_cfo,
            "tx_power_db": metrics["tx_power_db"],
            "rx_power_db": metrics["rx_power_db"],
            "evm_limit_pct": margins.get("evm_limit_pct", ""),
            "evm_margin_pct": margins.get("evm_margin_pct", ""),
            "ber_limit": margins.get("ber_limit", ""),
            "ber_margin": margins.get("ber_margin", ""),
        }
        rows_out.append(row)

        status = "PASS" if report.passed else "FAIL"
        print(f"[{status}] {mc.case_id}  EVM={metrics['evm_percent']:.3f}%  BER={metrics['ber']:.4e}")

    out_csv = PROJECT_ROOT / args.csv
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "pass",
        "evm_percent",
        "ber",
        "snr_db",
        "cfo_subcarrier_fraction",
        "cfo_correction",
        "cfo_correction_mode",
        "cfo_estimated_subcarrier_fraction",
        "tx_power_db",
        "rx_power_db",
        "evm_limit_pct",
        "evm_margin_pct",
        "ber_limit",
        "ber_margin",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    print(f"Saved CSV: {out_csv}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    summary_path = Path(args.json_summary) if args.json_summary else out_csv.with_name(
        f"validation_matrix_summary_{ts}.json"
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "matrix_config": str(cfg_path.relative_to(PROJECT_ROOT)),
        "meta": meta,
        "overall_pass": all_pass,
        "cases": rows_out,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved summary: {summary_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
