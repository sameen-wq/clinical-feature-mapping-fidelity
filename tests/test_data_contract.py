"""Synthetic fixtures ONLY: these tests do not validate the original UCI data."""

import pandas as pd
import pytest

from src.data_contract import audit_frame


def sample_frame():
    # Small artificial fixture: counts have no clinical provenance.
    return pd.DataFrame({
        "encounter_id": [101, 102, 103, 104],
        "patient_nbr": [1, 1, 2, 3],
        "readmitted": ["<30", "NO", ">30", "NO"],
        "number_inpatient": [2, 0, 1, 0],
        "number_emergency": [0, 1, 1, 0],
        "time_in_hospital": [1, 2, 3, 4],
        "num_medications": [5, 6, 2, 3],
        "num_lab_procedures": [4, 1, 2, 3],
        "num_procedures": [0, 1, 0, 1],
        "number_diagnoses": [2, 3, 1, 2],
        "number_outpatient": [1, 0, 0, 0],
    })


def test_counts_and_mapping_difference():
    summary = audit_frame(sample_frame())
    assert summary["n_encounters"] == 4
    assert summary["n_unique_patients"] == 3
    assert summary["n_patients_with_multiple_encounters"] == 1
    assert summary["n_encounters_from_repeated_patients"] == 2
    assert summary["target_distribution"]["<30"] == 1
    assert summary["candidate_swap_audit"]["n_rows_values_differ"] == 2
    assert summary["binary_positive_prevalence"] == 0.25


def test_missing_required_column_rejected():
    with pytest.raises(ValueError, match="Missing required"):
        audit_frame(sample_frame().drop(columns="patient_nbr"))


def test_duplicate_encounter_rejected():
    df = sample_frame()
    df.loc[1, "encounter_id"] = df.loc[0, "encounter_id"]
    with pytest.raises(ValueError, match="Duplicate encounter_id"):
        audit_frame(df)


def test_bad_label_rejected():
    df = sample_frame()
    df.loc[0, "readmitted"] = "maybe"
    with pytest.raises(ValueError, match="invalid readmitted labels"):
        audit_frame(df)


def test_missing_label_rejected():
    df = sample_frame()
    df.loc[0, "readmitted"] = None
    with pytest.raises(ValueError, match="Missing or invalid"):
        audit_frame(df)


def test_negative_count_rejected():
    df = sample_frame()
    df.loc[0, "number_emergency"] = -1
    with pytest.raises(ValueError, match="nonnegative integer"):
        audit_frame(df)


def test_non_numeric_count_rejected():
    df = sample_frame()
    df["number_emergency"] = df["number_emergency"].astype(object)
    df.loc[0, "number_emergency"] = "unknown"
    with pytest.raises(ValueError, match="Non-numeric"):
        audit_frame(df)


def test_blank_patient_id_rejected():
    df = sample_frame()
    df["patient_nbr"] = df["patient_nbr"].astype(object)
    df.loc[0, "patient_nbr"] = " "
    with pytest.raises(ValueError, match="blank"):
        audit_frame(df)
