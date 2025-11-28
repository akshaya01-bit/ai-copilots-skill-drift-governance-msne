import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"

def simple_itt_estimate():
    df = pd.read_csv(PROC_DIR / "session_metrics_v1.csv")

    # treat eo_gap as outcome; compare each arm vs None
    control = df[df["assistance_arm"] == "None"]["eo_gap"]
    results = []
    for arm in ["Rationale", "Calib", "Counter"]:
        treated = df[df["assistance_arm"] == arm]["eo_gap"]
        diff = treated.mean() - control.mean()
        results.append(
            {"arm": arm, "delta_eo_gap_vs_None": diff}
        )

    itt = pd.DataFrame(results)
    out = PROC_DIR / "itt_demo_eo_gap.csv"
    itt.to_csv(out, index=False)
    print(f"Saved {out}")


def simple_power_sketch(
    baseline_gap=0.12, mde=0.06, alpha=0.05, power=0.8, sd=0.20
):
    """
    Very rough sample size sketch for difference in means.
    """
    from math import ceil
    from scipy.stats import norm

    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)

    n_per_arm = 2 * (sd**2) * (z_alpha + z_beta) ** 2 / (mde**2)
    return ceil(n_per_arm)


def main():
    simple_itt_estimate()
    try:
        n = simple_power_sketch()
        with open(PROC_DIR / "power_sketch.txt", "w") as f:
            f.write(f"Approximate required session-blocks per arm: {n}\n")
        print(f"Saved {PROC_DIR / 'power_sketch.txt'}")
    except Exception as e:
        print("Power sketch failed (scipy not installed?):", e)


if __name__ == "__main__":
    main()
