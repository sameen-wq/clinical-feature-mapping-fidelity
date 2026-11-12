# UCI dataset and provenance

**Source**: [Diabetes 130-US Hospitals for Years 1999–2008](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008) (UCI ID 296). DOI: https://doi.org/10.24432/C5230J. License: Creative Commons Attribution 4.0 (CC BY 4.0). UCI lists 101,766 encounters; this must be verified after download.

The input is `diabetic_data.csv` from UCI's official archive. It is **not committed** to this repository. The script records a SHA-256 fingerprint of the exact CSV used. Original institution IDs are not available, so simulated client partitions do not represent the original hospitals.

Relevant variables (per UCI documentation):
- `patient_nbr`: patient ID; used for grouping, never as a predictor.
- `encounter_id`: encounter ID; never as a predictor.
- `readmitted`: `<30`, `>30`, or `NO` (the planned binary label is `<30` versus all other recorded states).
- `number_inpatient`: previous-year inpatient visits.
- `number_emergency`: previous-year emergency visits.

The planned swap is a simulated error where values assigned to these two *different clinical concepts* are exchanged. It is not a genuine FHIR-to-OMOP mapping study.

Citation: Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US Hospitals for Years 1999–2008* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J.
