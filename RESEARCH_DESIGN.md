# Research design: pre-registration-style working notes

Status: **preliminary; no dataset results and no trained models**.

## Question
How do controlled clinical field-mapping errors influence predictions of 30-day readmission using one historical EHR-derived dataset?

## First target mapping
Swap source values assigned to `number_inpatient` and `number_emergency` for records belonging to one *simulated* client. The feature names remain unchanged. This is an ETL mapping error across two different prior-year utilization concepts, not a random distribution shift, not a FHIR/OMOP transformation, and not real-world hospital measurements.

## Comparison
- E0: consistent definition in all three patient-disjoint simulated clients.
- E1: corrupted mapping in one simulated client's training records; same labels and same records as E0.
- E2: correct the injected mapping using the *known* correspondence (oracle-assisted restoration).

Main evaluation population: a fixed, patient-disjoint, canonically represented test set; compare fitted model performance on identical test records. Secondary analysis: client-local representation. Do not treat training-side corruption and deployment-side corruption as the same phenomenon.

## Rules
- Pre-specify patient-group split and record it before outcome-based analyses.
- No feature selection or preprocessing informed by final test performance.
- IDs never enter predictors. Evaluate whether the release contains chronology/selection issues before interpreting readmission outcomes clinically.
- Report class prevalence, patient counts, model stability and uncertainty. No invented findings.
- Federated learning is outside this project's implementation scope.

## Quality gate
Dataset schema and source integrity must pass before design is frozen or models are trained. Hypothesis can be unsupported; that is not failure of the project.

## Phase 1 audit checkpoint (November 3, 2026)
Real UCI audit supplied by researcher: 101,766 encounters; 71,518 patient IDs; 11,357 positive `<30` labels; field values differ in 36,199 encounters. Results indicate mapping feasibility only, not model effects. CSV SHA-256 stored in `results/dataset_manifest.json`. See `PHASE1_REVIEW.md`. Phase 2 is patient-group splitting and mapping equivalence tests, with no model training.
