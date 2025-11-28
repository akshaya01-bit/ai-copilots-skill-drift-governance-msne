import numpy as np
import pandas as pd
from pathlib import Path

RNG_SEED = 42
np.random.seed(RNG_SEED)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

def generate_decision_log(
    n_workers=80,
    n_teams=16,
    n_sessions=12,
    items_per_session=60,
):

    """
    Generate synthetic decision logs aligned with the co-pilot study brief:
    - workers grouped into teams
    - sessions
    - protected group A
    - access modality M (connectivity / device / language)
    - assistance arm T
    - AI confidence and suggestion
    - human decision and override
    - label y
    """
    teams = np.arange(1, n_teams + 1)
    workers = np.arange(1, n_workers + 1)

    # assign workers to teams
    worker_team = {
        w: np.random.choice(teams)
        for w in workers
    }

    # protected group (e.g., community) A and access modality M
    # A in {0,1}, M in {feature_2G, smartphone_3G, kannada_voice, hindi_text}
    modalities = ["feature_2G", "smartphone_3G", "kannada_voice", "hindi_text"]
    records = []

    for w in workers:
        A = np.random.binomial(1, 0.4)  # 40% in protected group
        M = np.random.choice(modalities, p=[0.25, 0.25, 0.25, 0.25])
        team = worker_team[w]

        for s in range(1, n_sessions + 1):
            # randomly assign assistance arm per worker-session (simple version)
            arm = np.random.choice(["None", "Rationale", "Calib", "Counter"])

            for i in range(items_per_session):
                # base difficulty and label y
                difficulty = np.random.beta(2, 5)  # more easy than hard
                # true label: harder items slightly more likely to be positive
                y = np.random.binomial(1, 0.4 + 0.3 * difficulty)

                # group-specific base skill for unaided worker
                base_skill = 0.65 + 0.05 * (1 - A)  # group A=0 slightly higher
                # modality penalty (e.g., 2G feature phones / ASR issues)
                modality_penalty = {
                    "feature_2G": 0.08,
                    "smartphone_3G": 0.02,
                    "kannada_voice": 0.06,
                    "hindi_text": 0.03,
                }[M]

                unaided_prob_correct = np.clip(
                    base_skill - modality_penalty - 0.25 * difficulty,
                    0.05,
                    0.95,
                )

                # AI model: slightly better on average but with group gap
                model_base = 0.75 + 0.03 * (1 - A)
                model_penalty = modality_penalty * 0.6
                model_prob_correct = np.clip(
                    model_base - model_penalty - 0.20 * difficulty,
                    0.1,
                    0.98,
                )

                # AI confidence as a noisy version of model_prob_correct
                ai_conf = np.clip(
                    np.random.normal(loc=model_prob_correct, scale=0.08),
                    0.01,
                    0.99,
                )

                # AI suggestion = y_hat (1 if confidence>0.5)
                ai_suggestion = int(ai_conf >= 0.5)

                # assistance arm effect on human accuracy and overrides
                if arm == "None":
                    assisted_prob_correct = unaided_prob_correct
                    override_rate = 0.0
                elif arm == "Rationale":
                    assisted_prob_correct = np.clip(
                        unaided_prob_correct + 0.03, 0, 1
                    )
                    override_rate = 0.15
                elif arm == "Calib":
                    assisted_prob_correct = np.clip(
                        unaided_prob_correct + 0.05, 0, 1
                    )
                    override_rate = 0.20
                else:  # "Counter"
                    assisted_prob_correct = np.clip(
                        unaided_prob_correct + 0.06, 0, 1
                    )
                    override_rate = 0.30

                # probability of trusting AI vs overriding, biased by confidence
                trust_tendency = 0.6 + 0.5 * (ai_conf - 0.5)  # more trust when confident
                trust_tendency = np.clip(trust_tendency, 0.05, 0.95)

                # sample whether human follows AI suggestion or not
                if np.random.rand() < override_rate:
                    uses_ai = np.random.rand() < (1 - trust_tendency)
                else:
                    uses_ai = np.random.rand() < trust_tendency

                if uses_ai:
                    human_decision = ai_suggestion
                    override = 0
                    # if model correct, human correct; else human wrong
                    correct = int(human_decision == y)
                else:
                    override = 1
                    # override correctness: based on assisted_prob_correct
                    correct = np.random.rand() < assisted_prob_correct
                    human_decision = int(
                        correct if y == 1 else not correct
                    ) if np.random.rand() < 0.5 else int(correct)

                records.append(
                    {
                        "worker_id": w,
                        "team_id": team,
                        "session": s,
                        "item_id": f"s{s}_i{i}",
                        "A": A,
                        "M": M,
                        "assistance_arm": arm,
                        "difficulty": difficulty,
                        "y_true": y,
                        "ai_confidence": ai_conf,
                        "ai_suggestion": ai_suggestion,
                        "human_decision": human_decision,
                        "override": override,
                        "correct": int(human_decision == y),
                    }
                )

    df = pd.DataFrame.from_records(records)
    return df


def summarize_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build session-level metrics close to the paper:
    - accuracy overall and by group
    - TPR/FPR gaps -> EO gap
    - access-aware ADI across modalities M
    - simple SDI approximate (change in unaided-like proxy over sessions)
    """
    # define protected group A and positive label y_true=1
    def group_metrics(sub):
        # confusion matrix components
        tp = ((sub["y_true"] == 1) & (sub["human_decision"] == 1)).sum()
        fp = ((sub["y_true"] == 0) & (sub["human_decision"] == 1)).sum()
        tn = ((sub["y_true"] == 0) & (sub["human_decision"] == 0)).sum()
        fn = ((sub["y_true"] == 1) & (sub["human_decision"] == 0)).sum()
        tpr = tp / (tp + fn + 1e-9)
        fpr = fp / (fp + tn + 1e-9)
        acc = (tp + tn) / (tp + tn + fp + fn + 1e-9)
        return pd.Series({"ACC": acc, "TPR": tpr, "FPR": fpr})

    rows = []
    for (session, arm), sub in df.groupby(["session", "assistance_arm"]):
        # group-specific metrics
        m0 = group_metrics(sub[sub["A"] == 0])
        m1 = group_metrics(sub[sub["A"] == 1])
        eo_gap = abs(m0["TPR"] - m1["TPR"]) + abs(m0["FPR"] - m1["FPR"])

        # access-aware ADI: max EO gap across modalities M
        eo_by_M = []
        for M in sub["M"].unique():
            subM = sub[sub["M"] == M]
            g0 = group_metrics(subM[subM["A"] == 0])
            g1 = group_metrics(subM[subM["A"] == 1])
            eo_M = abs(g0["TPR"] - g1["TPR"]) + abs(g0["FPR"] - g1["FPR"])
            eo_by_M.append(eo_M)
        adi = max(eo_by_M) if eo_by_M else 0.0

        # approximate calibration error (ECE-like): bin ai_confidence vs correctness
        bins = np.linspace(0.0, 1.0, 11)
        sub = sub.copy()
        sub["conf_bin"] = pd.cut(sub["ai_confidence"], bins=bins, include_lowest=True)
        ece = 0.0
        n = len(sub)
        for _, bsub in sub.groupby("conf_bin"):
            if len(bsub) == 0:
                continue
            avg_conf = bsub["ai_confidence"].mean()
            avg_acc = bsub["correct"].mean()
            ece += abs(avg_acc - avg_conf) * len(bsub) / n

        rows.append(
            {
                "session": session,
                "assistance_arm": arm,
                "acc_A0": m0["ACC"],
                "acc_A1": m1["ACC"],
                "tpr_A0": m0["TPR"],
                "tpr_A1": m1["TPR"],
                "fpr_A0": m0["FPR"],
                "fpr_A1": m1["FPR"],
                "eo_gap": eo_gap,
                "ADI": adi,
                "ECE": ece,
            }
        )

    metrics_df = pd.DataFrame(rows).sort_values(["session", "assistance_arm"])
    return metrics_df


def main():
    df = generate_decision_log()
raw_path = RAW_DIR / "sample_decisions_v2.csv"
    df.to_csv(raw_path, index=False)

    metrics_df = summarize_sessions(df)
proc_path = PROC_DIR / "session_metrics_v2.csv"
    metrics_df.to_csv(proc_path, index=False)

    print(f"Wrote raw decisions to {raw_path}")
    print(f"Wrote session metrics to {proc_path}")


if __name__ == "__main__":
    main()
