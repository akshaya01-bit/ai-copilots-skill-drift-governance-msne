# Governance and Evidence-Readiness Checklist (Synthetic Demo)

This checklist explains how the synthetic artifact is structured to support governance, audit,
and research on algorithmic authority and skill trajectories.

## 1. Logging structure

- [x] Row-level decision logs capture:
  - Worker/team identifiers (for clustering and random effects).
  - Protected group indicator `A` and access modality `M`.
  - Assistance arm (`None`, `Rationale`, `Calib`, `Counter`).
  - Model confidence and suggestions.
  - Human decisions, overrides, and correctness.
- [x] Session-level summaries allow monitoring at the granularity used in the study design.

## 2. Fairness and access-aware metrics

- [x] Equalized-odds style gap (EO gap) between protected groups.
- [x] Access Disparity Index (ADI) that surfaces the worst EO gap across modalities `M`.
- [x] Stratification by `A` and `M` enables more detailed subgroup analyses when needed.

## 3. Calibration and uncertainty

- [x] Approximate expected calibration error (ECE) is computed for each assistance arm.
- [x] Confidence bins and empirical accuracy are logged in a way that could be extended
      to more formal calibration analysis or visualizations.

## 4. Skill trajectories and drift vs lift

- [x] The `None` arm serves as an unaided baseline that can be tracked over sessions.
- [x] A simple SDI proxy is computed from changes in unaided accuracy over time.
- [x] The pipeline is structured so that more sophisticated longitudinal models could
      be layered on top (e.g., mixed-effects models, survival analysis).

## 5. Reproducibility

- [x] Synthetic data generation is scripted in `src/generate_synthetic_data.py`.
- [x] Metrics and plots are reproducible via `src/compute_metrics_and_plots.py`.
- [x] Additional analysis sketches are provided in `src/causal_and_power_demo.py`.
- [x] Environment details are documented in `requirements.txt` and `environment.yml`.

## 6. Privacy and ethics

- [x] All data in this repository are fully synthetic, created solely for demonstration.
- [x] No real user, worker, or organization data are included.
- [x] The structure is intended to model the *kind* of logging that would be needed
      for responsible evaluation in a real deployment, not to encode any real outcomes.

## 7. Adaptation to real deployments

In a real study, this structure would be combined with:

- Institutional review and consent procedures.
- Clear role definitions for who monitors fairness, calibration, and skill outcomes.
- Documented policies for responding to adverse findings (e.g., halting an arm,
  redesigning prompts, or introducing additional guardrails).

This synthetic artifact is therefore best read as an **evidence-ready template** that
connects measurement design, governance concerns, and empirical analysis.
