# Research progress log

## 2026-11-02 — Session 2: Scope freeze and dataset-audit starter

**Decision:** Remove FedAvg and personalized FL entirely from project milestones. Future federation is only a possible direction in discussion. Project is a controlled feature-mapping audit with downstream readmission prediction (planned, not yet run).

**Source verified on website:** UCI #296 lists 101,766 encounters and describes `patient_nbr`, `readmitted`, `number_inpatient`, and `number_emergency`. UCI lists CC BY 4.0.

**Files:** `scripts/01_inspect_dataset.py`, `src/data_contract.py`, `tests/test_data_contract.py`, `requirements.txt`, `README.md`, `data/README.md`, `.gitignore`, and this log.

**Execution evidence:** Data-contract and CLI integration tests run against synthetic fixtures only (9 passed). Network access to download UCI was unavailable in the authoring runtime. The real UCI file has NOT been audited; all quantitative clinical findings remain unknown.

**First gate still requires:** Run the audit against the actual UCI CSV, check source hash/schema/row count, examine field mismatch proportion, and confirm grouping strategy. Do not train before that evidence is reviewed.
