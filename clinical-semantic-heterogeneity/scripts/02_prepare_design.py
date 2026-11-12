"""Prepare and audit reproducible simulated-client splits and one mapping intervention.

No model training. Requires official CSV from Phase 1.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_contract import sha256_file   # noqa: E402
from src.experimental_design import prepare_design_audit  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=ROOT / "data" / "raw" / "diabetic_data.csv")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "design_audit.json")
    args = ap.parse_args()
    if not args.csv.exists():
        ap.error("CSV not found. First run: python scripts/01_inspect_dataset.py --download")
    df = pd.read_csv(args.csv, na_values=["?"], low_memory=False)
    audit = prepare_design_audit(df, seed=args.seed)
    audit["csv_sha256"] = sha256_file(args.csv)
    existing = ROOT / "results" / "dataset_manifest.json"
    if existing.exists() and args.csv.resolve() == (ROOT / "data" / "raw" / "diabetic_data.csv").resolve():
        previous = json.loads(existing.read_text(encoding="utf-8"))
        if previous.get("csv_sha256") != audit["csv_sha256"]:
            raise RuntimeError("Dataset checksum differs from original audit; stop and investigate")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print("DESIGN AUDIT COMPLETE — no models trained")
    print("Patient overlap across clients:", audit["cross_client_patient_overlap_count"])
    print("Patient overlap across train/validation/test:", audit["group_overlap_count"])
    print("Changed training rows in simulated client 0:", audit["mapping_intervention"]["rows_with_different_field_values"])
    print("Oracle restoration exact:", audit["mapping_intervention"]["oracle_restore_exact"])
    print("Saved:", args.out)

if __name__ == "__main__":
    main()
