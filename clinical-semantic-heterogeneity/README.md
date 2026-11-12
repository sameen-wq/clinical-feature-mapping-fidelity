# Clinical feature-mapping fidelity: exploratory research pilot

**Status: dataset audit implementation, not a completed experiment.**

## Research question
How does a controlled mismatch in the mapping of two clinically different utilization features affect the performance and probability estimates of a readmission model, when records, outcomes, and evaluation population are held fixed?

## Scope
- **No federated learning in this project.** Federation is a possible later research direction, not a planned baseline or claimed contribution.
- Primary dataset: [UCI Diabetes 130-US Hospitals (1999–2008)](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008), DOI: [10.24432/C5230J](https://doi.org/10.24432/C5230J), CC BY 4.0.
- Candidate mapping error: swap `number_inpatient` and `number_emergency` within one **simulated** client partition, keeping displayed feature names unchanged. This is a deliberately injected *feature-mapping error*, not evidence of naturally occurring hospital differences.
- No hospital identifiers are exposed in the published data. Three simulated partitions must **never** be described as real hospitals.

## Phase 1: validate the dataset (current step)

From the extracted project root, using Python 3.11+:

```bash
python -m pip install -r requirements.txt
python -m pytest tests -q
python scripts/01_inspect_dataset.py --download
```

If automatic download fails, download the official archive manually at the [UCI page](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008) and place `diabetic_data.csv` at `data/raw/diabetic_data.csv`. Then run:

```bash
python scripts/01_inspect_dataset.py --csv data/raw/diabetic_data.csv
```

The audit writes `results/data_audit.json` and `results/dataset_manifest.json`. These are descriptive audit files, **not model results**. Verify that the actual row count agrees with UCI's published 101,766 before accepting the dataset quality gate. The script records a source-file SHA-256 hash and reports how often the candidate fields disagree. It does **not** train or evaluate any model.

## Planned experimental controls (not implemented yet)

1. Split by `patient_nbr` to prevent encounters from one patient appearing in different splits or simulated clients.
2. Use the same patients, labels, feature set and random seeds in all conditions.
3. Fit preprocessing only on training data. Hold the consistently defined test set fixed as the primary reference.
4. Compare **E0: correct mapping**, **E1: injected swap in one training client**, **E2: known mapping restored (oracle-assisted)**.
5. Evaluate AUROC, AUPRC, Brier score, log loss, and calibration, while documenting negative findings and the distinction between representation error and distribution shift.

The experiment is not yet run. No numerical results should be cited.

## Attribution and limitations
UCI dataset: Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US Hospitals for Years 1999–2008*. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J (CC BY 4.0). Original clinical source: Strack et al., 2014, *BioMed Research International*, https://doi.org/10.1155/2014/781670.

The records are historical, from multiple institutions but without institution IDs. The injected swap is an artificial, narrow mapping failure. It cannot establish FHIR/OMOP transformation fidelity or clinical generalizability. This repository is a supervised, exploratory portfolio project, not a clinical tool or peer-reviewed study. Analytical design/code has been developed with AI assistance; results and interpretations will be verified separately.

See [`PROGRESS_LOG.md`](PROGRESS_LOG.md) for current verified status and [`data/README.md`](data/README.md) for source details.
