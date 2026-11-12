"""Dataset quality checks. No machine learning is performed here."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import pandas as pd

DATASET_COLUMNS = (
    "encounter_id", "patient_nbr", "readmitted",
    "number_inpatient", "number_emergency",
    "time_in_hospital", "num_medications", "num_lab_procedures",
    "num_procedures", "number_diagnoses", "number_outpatient",
)
LABELS = {"<30", ">30", "NO"}
NUMERIC_FEATURES = (
    "number_inpatient", "number_emergency", "time_in_hospital",
    "num_medications", "num_lab_procedures", "num_procedures",
    "number_diagnoses", "number_outpatient",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_frame(df: pd.DataFrame) -> dict:
    """Validate required columns and summarize counts without patient-level outputs."""
    missing = sorted(set(DATASET_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df.empty:
        raise ValueError("Input CSV has no rows")
    ids = df["encounter_id"]
    patients = df["patient_nbr"]
    if ids.isna().any() or patients.isna().any():
        raise ValueError("encounter_id or patient_nbr contains missing values")
    if (ids.astype(str).str.strip() == "").any() or (patients.astype(str).str.strip() == "").any():
        raise ValueError("encounter_id or patient_nbr is blank")
    if ids.duplicated().any():
        raise ValueError("Duplicate encounter_id values")

    labels = df["readmitted"].astype("string").str.strip()
    unexpected = sorted(set(labels.dropna().tolist()) - LABELS)
    if labels.isna().any() or unexpected:
        raise ValueError(f"Missing or invalid readmitted labels: {unexpected}")

    numeric = {}
    numeric_summary = {}
    for col in NUMERIC_FEATURES:
        # Invalid values fail loudly; missing values are reported and require review.
        try:
            vals = pd.to_numeric(df[col], errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Non-numeric values found in {col}") from exc
        if ((vals.dropna() < 0) | (vals.dropna() % 1 != 0)).any():
            raise ValueError(f"Expected nonnegative integer counts in {col}")
        numeric[col] = vals
        numeric_summary[col] = {
            "missing": int(vals.isna().sum()),
            "zero": int((vals == 0).sum()),
            "nonzero": int((vals > 0).sum()),
            "mean": (round(float(vals.mean()), 6) if vals.notna().any() else None),
        }

    inpatient = numeric["number_inpatient"]
    emergency = numeric["number_emergency"]
    comparable = inpatient.notna() & emergency.notna()
    different = comparable & (inpatient != emergency)
    patient_counts = patients.value_counts()
    label_counts = {k: int((labels == k).sum()) for k in ("<30", ">30", "NO")}
    positive = label_counts["<30"]
    return {
        "n_encounters": int(len(df)),
        "n_unique_patients": int(patients.nunique()),
        "n_patients_with_multiple_encounters": int((patient_counts > 1).sum()),
        "n_encounters_from_repeated_patients": int(patient_counts[patient_counts > 1].sum()),
        "n_duplicate_encounter_ids": int(ids.duplicated().sum()),
        "target_distribution": label_counts,
        "binary_target_definition": "positive iff readmitted == '<30'",
        "binary_positive_prevalence": round(positive / len(df), 6),
        "numeric_features": numeric_summary,
        "candidate_swap_audit": {
            "feature_a": "number_inpatient",
            "feature_b": "number_emergency",
            "n_rows_both_observed": int(comparable.sum()),
            "n_rows_values_differ": int(different.sum()),
            "fraction_differ_among_observed": (
                round(float(different.sum() / comparable.sum()), 6)
                if comparable.any() else None
            ),
        },
        "matches_uci_published_101766_rows": bool(len(df) == 101766),
        "caution": "Descriptive full-dataset audit only; do not tune on test outcomes."
    }
