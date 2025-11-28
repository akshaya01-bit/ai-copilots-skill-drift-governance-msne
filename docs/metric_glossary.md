# Metric Glossary for the Co-Pilot Study Artifact

This document explains the main metrics used in the synthetic co-pilot study artifact.
They are intended to mirror the kinds of quantities discussed in the accompanying research brief.

## Equalized-odds style gap (EO gap)

For a given session and assistance arm, we compute group-specific true positive rates (TPR) and
false positive rates (FPR) for protected group indicator `A`:

- `TPR_Ag = P(human_decision = 1 | y_true = 1, A = g)`
- `FPR_Ag = P(human_decision = 1 | y_true = 0, A = g)`

The EO gap is defined as:

`EO_gap = |TPR_A0 - TPR_A1| + |FPR_A0 - FPR_A1|`

This collapses both TPR and FPR differences into a single scalar used to summarize fairness.

## Access Disparity Index (ADI)

The Access Disparity Index is an **access-aware fairness** quantity that takes account of modality `M`
(e.g., connectivity, device, or language channel). For each modality `M`, we compute an EO gap as above,
and define ADI as:

`ADI = max_M EO_gap(M)`

Intuitively, ADI focuses on the *worst* EO gap across modalities, helping highlight cases where particular
access channels (e.g., low-bandwidth or IVR-like conditions) are disproportionately disadvantaged.

## Expected Calibration Error (ECE)

Calibration compares the co-pilot's predicted confidence to realized accuracy.

We bin events by `ai_confidence` and, for each bin, compute:

- `avg_conf` — mean predicted confidence,
- `avg_acc` — mean empirical correctness of `human_decision`.

ECE is the weighted average of `|avg_acc - avg_conf|` across bins, using bin frequencies as weights.
Lower ECE indicates that confidence scores are better aligned with realized accuracy.

## Skill Drift Index (SDI proxy)

The artifact provides a *proxy* for a skill drift index (SDI) using unaided accuracy under the `None`
assistance arm. For each session `s`, we compute an aggregate accuracy `U_s` (averaging `acc_A0` and `acc_A1`),
and examine changes over time:

`delta_s = U_s - U_{s-1}`

The SDI proxy is the mean `delta_s` across sessions (excluding the first). Negative values roughly correspond
to deteriorating unaided performance, while positive values suggest skill lift; in real deployments this would
be estimated more carefully and tied to preregistered hypotheses.

## Intent-to-treat (ITT) style differences

For demonstration, the `src/causal_and_power_demo.py` script computes simple differences in EO gap between
each assistance arm and the `None` arm. These are not full causal estimates but illustrate how the logging
structure can support multi-arm comparisons and power calculations in a preregistered analysis plan.

All of these metrics are computed on synthetic data in this repository, but the structure is chosen so that
the same code could be adapted to real deployment logs under appropriate governance and review.
