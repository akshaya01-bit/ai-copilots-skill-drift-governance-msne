# AI Co-Pilots in Low-Resource Team Decisions: Fairness, Skill Drift, and Evidence-Ready Governance

This repository accompanies the research design brief for an AI co-pilot in low-resource team decision workflows.
All data in this repository are **fully synthetic** and constructed for demonstration only.

## Structure

- `data/raw/`: synthetic row-level decision logs.
- `data/processed/`: session- and stratum-level metrics.
- `src/`: scripts for generating synthetic data, computing metrics, and sketching causal/power analyses.
- `figures/`: calibration curves, fairness plots, and HTE-style visualizations.
- `paper/`: PDF of the research brief submitted with the Stanford MS&E PhD application.

## Synthetic data

The synthetic data mirrors the structure described in the brief:

- Workers grouped into teams, sessions, and access strata (connectivity, device, language).
- Assistance arms (`None`, `Rationale`, `Calib`, `Counter`).
- Protected group indicator `A` and access modality `M`.
- AI confidence, human decisions, and overrides.

The goal is to illustrate an **evidence-ready** logging and analysis workflow aligned to the paper, without using any real deployment data.
