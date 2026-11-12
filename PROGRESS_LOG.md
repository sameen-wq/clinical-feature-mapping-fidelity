# Research progress log

## 2026-11-02 — Session 2: Scope freeze and dataset-audit starter

**Decision:** Remove FedAvg and personalized FL entirely from project milestones. Future federation is only a possible direction in discussion. Project is a controlled feature-mapping audit with downstream readmission prediction (planned, not yet run).

**Source verified on website:** UCI #296 lists 101,766 encounters and describes `patient_nbr`, `readmitted`, `number_inpatient`, and `number_emergency`. UCI lists CC BY 4.0.

**Files:** `scripts/01_inspect_dataset.py`, `src/data_contract.py`, `tests/test_data_contract.py`, `requirements.txt`, `README.md`, `data/README.md`, `.gitignore`, and this log.

**Execution evidence:** Data-contract and CLI integration tests run against synthetic fixtures only (9 passed). Network access to download UCI was unavailable in the authoring runtime. The real UCI file has NOT been audited; all quantitative clinical findings remain unknown.

**First gate still requires:** Run the audit against the actual UCI CSV, check source hash/schema/row count, examine field mismatch proportion, and confirm grouping strategy. Do not train before that evidence is reviewed.

## 2026-11-03 — Session 3: Real UCI dataset audit received and reviewed

**Evidence supplied by researcher:** `audit_results.zip` with `data_audit.json` and `dataset_manifest.json`, created by Phase 1 script in Google Colab on 2026-11-02 18:48 UTC. Audit records a download from the official UCI #296 ZIP, original archive SHA-256 `f82ac129da2ddd2299391ff6fbae3a6a58b3edcf59ac9d7bd480c00fe453112a`, and CSV SHA-256 `0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97`. Raw data not shared with reviewer. Archive hash was **not** independently verified by reviewer.

**Dataset observations from actual audit (not model results):** 101,766 encounters; 71,518 unique patients; 16,773 patients with multiple encounters; 47,021 encounters from repeated patients. Labels: `<30`=11,357, `>30`=35,545, `NO`=54,864. Thus positive rate for binary task is 11.16%. The eight proposed count predictors have no missing values under the audit. `number_inpatient != number_emergency` in 36,199 / 101,766 encounters (35.57%). Source size and documented feature meaning cross-checked against UCI official dataset listing.

**Research interpretation:** Swapping these two fields is an auditable *synthetic ETL semantic misassignment* with a measurable potential exposure, **not** evidence of real hospital mapping failures or downstream predictive degradation. Feature differences do not indicate model errors. Quantification was on full dataset as a descriptive source audit; no outcome-driven intervention optimization was performed.

**Phase 1 data-source/schema/mapping-feasibility gate:** **Accepted provisionally** based on generated real-data audit and external dataset metadata. Raw file contents and checksum not independently reproduced in reviewer environment. Before any modeling, Phase 2 script must verify CSV hash against preserved manifest, confirm group-disjoint splits, inspect per-client prevalence and demonstrate exact round-trip mapping restoration.

**Next implementation milestone:** `src/experimental_design.py`, `scripts/02_prepare_design.py` and associated synthetic tests. In authoring environment, 16 tests passed (including CLI synthetic integration). Real-data Phase 2 split / mapping execution **not yet completed**. Zero model training performed. Source and synthetic tests alone do not establish clinical effects.
