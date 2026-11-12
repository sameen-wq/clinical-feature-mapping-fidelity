# Clinical Feature-Mapping Fidelity: An Exploratory Study

## Overview

A clinical field can keep its name and data type after a transformation, even when its values no longer represent the intended concept. This project studies a controlled example of that problem: an incorrect assignment between prior inpatient and emergency visit counts in a hospital readmission prediction task.

Using the UCI Diabetes 130-US Hospitals dataset, I compared logistic regression models trained on correctly mapped data (E0), partially misassigned training features (E1), and restored mappings (E2). I examined aggregate model performance, differences in individual predicted probabilities, and sensitivity among encounters with high emergency utilization.

This is an **exploratory research pilot**, not a clinical decision tool, a federated learning experiment, or a demonstration of actual FHIR/OMOP transformation errors.

## Research question

How does a controlled misassignment between two clinically distinct healthcare-utilization features affect 30-day readmission model performance and individual predicted probabilities?

## Data and experimental design

- Source: [UCI Diabetes 130-US Hospitals (1999 to 2008)](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008), [DOI: 10.24432/C5230J](https://doi.org/10.24432/C5230J).
- Data: 101,766 hospital encounters and 71,518 unique patient identifiers.
- Outcome: readmission within 30 days, with 11,357 positive encounters (11.16%).
- Predictors: eight numeric variables selected in the research notebook.
- Patient-level partitions: 71,197 training, 15,250 validation, and 15,319 test encounters. Each patient was assigned to only one partition.
- E0: original inpatient and emergency visit values.
- E1: the two values were exchanged in Client 0 training records, changing 8,482 encounters. Other records and all validation/test inputs were unchanged.
- E2: the known exchange was reversed to verify restoration.
- Three client groups were **simulated**. They do not represent identified hospitals.

## Main results

| Test metric | E0: correct | E1: misassigned | E2: restored |
| --- | ---: | ---: | ---: |
| AUROC | 0.62086 | 0.62024 | 0.62086 |
| AUPRC | 0.19346 | 0.19065 | 0.19346 |
| Brier score | 0.09607 | 0.09644 | 0.09607 |

The changes in overall test metrics were small. Patient-cluster bootstrap intervals for E1 minus E0 included zero for AUROC, AUPRC, and Brier score, so the aggregate performance differences were inconclusive.

Individual predictions changed more noticeably for some encounters. On the held-out test set, mean absolute probability differences were 0.64 percentage points for zero emergency visits, 2.02 points for one to three visits, and 16.93 points for four or more visits (170 encounters). These are differences between model predictions, not direct measurements of clinical harm.

Five additional simulated-client assignments showed similar patterns in validation, although those runs reused the same validation patients.

## Repository guide

| Location | Purpose |
| --- | --- |
| [`notebooks/Clinical_Data_Audit.ipynb`](notebooks/Clinical_Data_Audit.ipynb) | Colab workflow for audit, modeling, evaluation, and uncertainty analysis. Upload the **latest completed notebook** here. |
| [`research_note/`](research_note/) | Research report with Methods, Results, Discussion, limitations, and references. |
| [`figures/`](figures/) | Prediction-sensitivity and bootstrap-interval figures. |
| [`results/`](results/) | Dataset audit records and exported model performance CSV files. |
| [`src/`](src/) | Dataset contract and experimental design functions. |
| [`scripts/`](scripts/) | Original dataset audit and experiment-preparation scripts. |
| [`tests/`](tests/) | Existing checks for dataset and design logic. |
| [`data/README.md`](data/README.md) | Data source and acquisition notes. The raw CSV is not included. |

## Running the existing audit and design scripts

The repository's original audit and design scripts can be run from the project root after installing the dependencies listed in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
python -m pytest tests -q
python scripts/01_inspect_dataset.py --download
python scripts/02_prepare_design.py
```

The final modeling experiments were developed interactively in Google Colab. The current `requirements.txt` originated from the earlier audit and design stage, so the modeling dependencies and a standalone end-to-end workflow still require verification. **Independent end-to-end reproducibility testing of the complete modeling workflow remains pending.** Do not treat the audit commands above as reproducing the final model results.

## Interpretation and limitations

This pilot was motivated by an interest in clinical semantics, transformation fidelity, and data provenance. It did not directly evaluate provenance metadata, automated error detection, FHIR-to-OMOP transformations, or cross-institutional federated learning. The simulated swap was known in advance, and its correction was oracle-assisted. The high-emergency-utilization group was small, and all findings come from a single historical dataset and one modeling approach.

For the complete discussion and evidence, see the report in [`research_note/`](research_note/).

## Data and references

- Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US Hospitals for Years 1999–2008*. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J
- Strack, B., et al. (2014). *Impact of HbA1c measurement on hospital readmission rates: Analysis of 70,000 clinical database patient records*. *BioMed Research International*. https://doi.org/10.1155/2014/781670

The raw dataset is excluded from this repository. Review notebook outputs and files for sensitive or identifying information before making the repository public.
