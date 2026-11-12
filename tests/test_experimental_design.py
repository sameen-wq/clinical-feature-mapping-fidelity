"""Synthetic tests. Not evidence of actual clinical predictive effects."""
import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.data_contract import NUMERIC_FEATURES
from src.experimental_design import make_patient_partitions, swapped_utilization_fields, prepare_design_audit


def frame(n_patients=45):
    rng = np.random.default_rng(18)
    vals=[]
    for i in range(n_patients):
        for r in range(2):
            row = {"encounter_id": f"e{i}_{r}", "patient_nbr": f"p{i}",
                   "readmitted": "<30" if (i + r)%8 == 0 else "NO"}
            row.update({k: int(rng.integers(1, 5)) for k in NUMERIC_FEATURES})
            row["number_inpatient"] = i % 4
            row["number_emergency"] = (i+1) % 3
            vals.append(row)
    return pd.DataFrame(vals)


def test_assignment_no_patient_overlap():
    f=frame(); a=make_patient_partitions(f)
    assert len(a) == len(f)
    assert a.groupby("patient_nbr")["client"].nunique().max()==1
    assert a.groupby("patient_nbr")["split"].nunique().max()==1
    assert all(a.split.value_counts()[x] for x in ["train", "test", "validation"])


def test_assignment_reproducible_and_row_order_invariant():
    f=frame()
    a=make_patient_partitions(f, seed=47).set_index('encounter_id').sort_index()
    reordered=f.sample(frac=1,random_state=3).reset_index(drop=True)
    b=make_patient_partitions(reordered, seed=47).set_index('encounter_id').sort_index()
    assert_frame_equal(a,b,check_dtype=True)


def test_assignment_changed_seed_can_change_assignments():
    f=frame()
    a=make_patient_partitions(f, seed=10)
    b=make_patient_partitions(f, seed=11)
    assert (a['client']!=b['client']).any()


def test_field_swap_exact_reversal_no_label_change():
    f=frame()
    altered=swapped_utilization_fields(f)
    assert_frame_equal(swapped_utilization_fields(altered),f)
    assert altered['readmitted'].equals(f['readmitted'])
    assert altered['number_inpatient'].equals(f['number_emergency'])


def test_missing_mapping_column_rejected():
    with pytest.raises(ValueError):
        swapped_utilization_fields(frame().drop(columns=['number_emergency']))


def test_design_audit_outputs_no_patient_level_records():
    a=prepare_design_audit(frame())
    assert a['group_overlap_count']==0
    assert a['cross_client_patient_overlap_count']==0
    assert a['mapping_intervention']['oracle_restore_exact']
    assert len(a['client_split_summary'])==9
    assert 'patient_nbr' not in str(a)
    assert 'encounter_id' not in str(a)
