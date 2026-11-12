# Phase 1 Audit Review (pre-model evidence)

Date reviewed: 2026-11-03.

## Evidence from researcher-provided Google Colab audit

- Source: UCI Machine Learning Repository, dataset #296, DOI 10.24432/C5230J; license CC BY 4.0.
- 101,766 encounter rows and 71,518 distinct patient identifiers.
- 16,773 patients have multiple encounters; those patients contribute 47,021 rows. Hence **group-based splitting by patient is mandatory**.
- Original `readmitted` classes: `<30` = 11,357; `>30` = 35,545; `NO` = 54,864.
- Our pre-specified binary outcome (`<30` versus other outcomes) has 11,357 positive encounters, 11.16% prevalence.
- `number_inpatient` nonzero in 34,136 encounters, mean 0.635566; `number_emergency` nonzero in 11,383 encounters, mean 0.197836.
- These two recorded visit-count fields differ in 36,199 / 101,766 encounters (35.57%). This shows an injected swap can change inputs, **not** that it will change predictions or calibration.
- CSV SHA-256 as reported by Colab: `0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97`. Verified manifest structure and matching UCI row count; raw file itself was not available for rehashing in the reviewer environment.

## Quality gate decision

The **dataset audit milestone is accepted with a verification dependency**. Before advancing to model training, execute `02_prepare_design.py` on the same CSV, verify the original hash, ensure no patient appears in multiple clients or splits, document client-wise outcome prevalence, and confirm corrupted-to-restored equality. Keep held-out test data unchanged and do not tune interventions on test labels.

## Limitations

Artificial clients do not correspond to the 130 source hospitals. The proposed field swap is a deliberately injected ETL error, not evidence of naturally occurring semantic mismatches. Outcome and data are historic. Feature distribution differences may have little, no, or unexpected impact on downstream prediction.

Source documentation: https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
