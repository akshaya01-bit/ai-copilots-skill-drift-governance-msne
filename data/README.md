# Data Dictionary

This repository uses **fully synthetic** data constructed to mirror the structure
of logging that would be needed for the co-pilot study described in `paper/study2_brief_msne.pdf`.

## Raw decision logs

**File:** `data/raw/sample_decisions_v2.csv`  
(Versioned variants such as `sample_decisions_v1.csv` may also be present.)

Each row corresponds to one decision event for a single worker, item, and session.

- `worker_id` — Integer ID for the worker.
- `team_id` — Integer ID for the team to which the worker belongs.
- `session` — Integer session index (e.g., 1..12). In the brief, sessions can map to time blocks or task batches.
- `item_id` — String ID for the decision item within a session.
- `A` — Binary protected-group indicator (0 / 1), used in fairness analyses (e.g., EO gaps).
- `M` — Access modality, e.g. `"feature_2G"`, `"smartphone_3G"`, `"kannada_voice"`, `"hindi_text"`.
  This encodes differences in connectivity, device, or language channel.
- `assistance_arm` — Assigned assistance condition for that worker-session:
  - `"None"` — unaided baseline,
  - `"Rationale"` — co-pilot with explanation,
  - `"Calib"` — co-pilot with calibration framing,
  - `"Counter"` — co-pilot with counterfactual-style prompts.
- `difficulty` — Continuous [0,1]-ish measure for item difficulty used in synthetic generation.
- `y_true` — Binary ground-truth label (0 / 1) for the decision.
- `ai_confidence` — Model confidence in its suggestion, in [0,1].
- `ai_suggestion` — Binary suggestion from the co-pilot (0 / 1).
- `human_decision` — Binary final decision recorded for the worker (0 / 1).
- `override` — 1 if the worker overrode the AI suggestion, 0 if they followed it.
- `correct` — 1 if `human_decision == y_true`, 0 otherwise.

## Session-level metrics

**File:** `data/processed/session_metrics_v2.csv`  
(Other versions such as `session_metrics_v1.csv` may exist as earlier snapshots.)

Each row summarizes performance and fairness metrics for a given `(session, assistance_arm)` pair.

- `session` — Session index (integer).
- `assistance_arm` — Assistance condition (`"None"`, `"Rationale"`, `"Calib"`, `"Counter"`).
- `acc_A0` — Accuracy for group A=0.
- `acc_A1` — Accuracy for group A=1.
- `tpr_A0` — True positive rate (TPR) for group A=0.
- `tpr_A1` — True positive rate (TPR) for group A=1.
- `fpr_A0` — False positive rate (FPR) for group A=0.
- `fpr_A1` — False positive rate (FPR) for group A=1.
- `eo_gap` — Equalized-odds style gap, defined as
  `|TPR_A0 - TPR_A1| + |FPR_A0 - FPR_A1|` for the session and arm.
- `ADI` — Access Disparity Index: maximum EO gap across access modalities `M` within the same session and arm.
- `ECE` — Approximate expected calibration error for the co-pilot’s confidence, computed in bins.

## Derived summaries

Additional files in `data/processed/` include:

- `summary_metrics_by_arm.csv` — Mean EO gap, ADI, and ECE aggregated by `assistance_arm`.
- `itt_demo_eo_gap.csv` — Toy intent-to-treat style differences in EO gap vs the `None` arm.
- `sdi_proxy.txt` — Text file reporting an SDI-style proxy based on changes in unaided performance.
- `power_sketch.txt` — Rough power calculation output produced by `src/causal_and_power_demo.py` (if `scipy` is available).

All values and relationships are synthetic and created for demonstration of an **evidence-ready** logging
and analysis workflow. No real deployment data are included.
