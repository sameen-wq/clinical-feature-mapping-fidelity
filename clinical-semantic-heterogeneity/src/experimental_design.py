"""Deterministic patient-group partitions and an explicitly simulated field-mapping error.

No models are fitted and no actual hospital identity is implied.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from .data_contract import NUMERIC_FEATURES, audit_frame


def make_patient_partitions(df: pd.DataFrame, *, seed: int = 2026, n_clients: int = 3) -> pd.DataFrame:
    """Return client/split assignments for encounters, grouping all encounters of each patient.

    Assign patients at random to *simulated* clients, then perform per-client
    train/validation/test patient-group splits (70/15/15). No outcome stratification.
    """
    if n_clients != 3:
        raise ValueError("Pilot is pre-specified for exactly three simulated clients")
    if df["patient_nbr"].isna().any() or df["encounter_id"].duplicated().any():
        raise ValueError("Missing patient IDs or duplicate encounter IDs")
    patient_ids = df["patient_nbr"].unique()
    if len(patient_ids) < 12:
        raise ValueError("Need at least 12 patients for simulated-client grouping")
    # Sorting makes the result invariant to input row ordering.
    patient_ids = sorted(patient_ids.tolist())
    rng = np.random.default_rng(seed)
    patient_ids = np.asarray(patient_ids)
    rng.shuffle(patient_ids)
    ids_by_client = np.array_split(patient_ids, n_clients)
    lookup = {}
    for client, group in enumerate(ids_by_client):
        rng_for_client = np.random.default_rng(seed + client + 1)
        group = group.copy()
        rng_for_client.shuffle(group)
        n = len(group)
        n_train = int(0.70 * n)
        n_val = int(0.15 * n)
        if n_train < 1 or n_val < 1 or n - n_train - n_val < 1:
            raise ValueError("Not enough patients in one simulated client")
        for i, patient in enumerate(group):
            split = "train" if i < n_train else "validation" if i < n_train + n_val else "test"
            lookup[patient] = (client, split)

    assignments = pd.DataFrame({
        "encounter_id": df["encounter_id"].to_numpy(),
        "patient_nbr": df["patient_nbr"].to_numpy(),
    }, index=df.index)
    values = assignments["patient_nbr"].map(lookup)
    assignments["client"] = values.map(lambda pair: int(pair[0]))
    assignments["split"] = values.map(lambda pair: pair[1])
    assert assignments["split"].notna().all()
    # Essential invariants, also tested against independent fixtures.
    assert assignments.groupby("patient_nbr")["client"].nunique().max() == 1
    assert assignments.groupby("patient_nbr")["split"].nunique().max() == 1
    return assignments


def swapped_utilization_fields(frame: pd.DataFrame) -> pd.DataFrame:
    """Swap the *values*, not the names, of two distinct prior-year visit fields."""
    a, b = "number_inpatient", "number_emergency"
    if a not in frame or b not in frame:
        raise ValueError("Required utilization columns missing")
    result = frame.copy()
    result[[a, b]] = frame[[b, a]].to_numpy()
    return result


def prepare_design_audit(df: pd.DataFrame, *, seed: int = 2026) -> dict:
    """Describe the pre-model experiment without saving IDs or model findings."""
    audit_frame(df)  # Contract must pass first.
    assignments = make_patient_partitions(df, seed=seed)
    work = df.loc[:, ["encounter_id", "readmitted", *NUMERIC_FEATURES]].copy()
    work["client"] = assignments["client"]
    work["split"] = assignments["split"]
    work["positive"] = (work["readmitted"] == "<30").astype(int)

    sizes = []
    for client in range(3):
        for split in ("train", "validation", "test"):
            part = work[(work.client == client) & (work.split == split)]
            patient_mask = (assignments.client == client) & (assignments.split == split)
            sizes.append({
                "client": client,
                "split": split,
                "encounters": int(len(part)),
                "patients": int(assignments.loc[patient_mask, "patient_nbr"].nunique()),
                "positive_encounters": int(part.positive.sum()),
                "positive_fraction": round(float(part.positive.mean()), 6),
            })

    injected_client = 0
    impacted = work[(work.client == injected_client) & (work.split == "train")].copy()
    swapped = swapped_utilization_fields(impacted)
    changed = (impacted["number_inpatient"] != swapped["number_inpatient"])
    restored = swapped_utilization_fields(swapped)
    if not restored.equals(impacted):
        raise AssertionError("Oracle restoration failed to reproduce canonical values")
    for part in ("validation", "test"):
        untouched = work[work.split == part]
        if untouched.empty:
            raise AssertionError("Empty held-out split")

    # These fingerprints audit the allocation without publishing patient IDs.
    # The underlying data are already public and de-identified; we nevertheless
    # avoid writing patient-level mappings to repository outputs.
    assignment_rows = sorted((str(pid), int(v[0]), v[1]) for pid, v in
                             assignments.drop_duplicates("patient_nbr")
                             .set_index("patient_nbr")[["client", "split"]]
                             .apply(tuple, axis=1).items())
    digest = hashlib.sha256(json.dumps(assignment_rows, separators=(",", ":")).encode()).hexdigest()

    return {
        "phase": "patient_disjoint_partition_and_mapping_feasibility_only",
        "seed": seed,
        "n_simulated_clients": 3,
        "actual_hospital_id_available": False,
        "assignment_method": "shuffle sorted patient IDs; 3 random artificial clients; 70/15/15 patient-group split per client; not stratified",
        "patient_assignment_sha256": digest,
        "group_overlap_count": int((assignments.groupby("patient_nbr")["split"].nunique() > 1).sum()),
        "cross_client_patient_overlap_count": int((assignments.groupby("patient_nbr")["client"].nunique() > 1).sum()),
        "client_split_summary": sizes,
        "mapping_intervention": {
            "description": "In simulated client 0 training records, swap count values of inpatient and emergency prior-year visits but retain names",
            "changed_client": 0,
            "changed_split": "train",
            "rows_in_target_split": int(len(impacted)),
            "rows_with_different_field_values": int(changed.sum()),
            "fraction_of_target_split_affected": round(float(changed.mean()), 6),
            "oracle_restore_exact": True,
            "labels_unchanged": bool((impacted["readmitted"] == swapped["readmitted"]).all()),
            "feature_names_unchanged": list(impacted.columns) == list(swapped.columns),
            "clinical_effects_observed": False,
        },
        "note": "No models trained. These are simulated partitions, not observed hospital sites. Inspect prevalence imbalance before training."
    }
