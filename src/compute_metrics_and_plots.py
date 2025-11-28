import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR = Path("data")
PROC_DIR = DATA_DIR / "processed"
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True, parents=True)


def make_summary_table(metrics_path: Path):
    df = pd.read_csv(metrics_path)
    summary = (
        df.groupby("assistance_arm")[["eo_gap", "ADI", "ECE"]]
        .mean()
        .reset_index()
        .sort_values("assistance_arm")
    )
    out_path = PROC_DIR / "summary_metrics_by_arm.csv"
    summary.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    return summary


def plot_eo_gap_over_sessions(metrics_path: Path):
    df = pd.read_csv(metrics_path)
    plt.figure()
    for arm, sub in df.groupby("assistance_arm"):
        plt.plot(sub["session"], sub["eo_gap"], marker="o", label=arm)
    plt.xlabel("Session")
    plt.ylabel("EO gap (TPR+FPR)")
    plt.title("Equalized-odds style EO gap over sessions")
    plt.legend()
    out = FIG_DIR / "eo_gap_over_sessions.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def plot_adi_over_sessions(metrics_path: Path):
    df = pd.read_csv(metrics_path)
    plt.figure()
    for arm, sub in df.groupby("assistance_arm"):
        plt.plot(sub["session"], sub["ADI"], marker="o", label=arm)
    plt.xlabel("Session")
    plt.ylabel("Access Disparity Index (ADI)")
    plt.title("ADI over sessions by assistance arm")
    plt.legend()
    out = FIG_DIR / "adi_over_sessions.png"
    plt.savefig(out, bbox_inches="tight")
    plt.close()
    print(f"Saved {out}")


def sketch_sdi_from_metrics(metrics_path: Path):
    """
    Very rough SDI proxy: we interpret accuracy under 'None' as unaided skill
    and compute change over sessions.
    """
    df = pd.read_csv(metrics_path)
    none_df = df[df["assistance_arm"] == "None"].copy()
    none_df = none_df.sort_values("session")

    # treat acc_A0+acc_A1 average as proxy for unaided skill Us
    none_df["U"] = 0.5 * (none_df["acc_A0"] + none_df["acc_A1"])
    none_df["U_shift"] = none_df["U"].shift(1)
    none_df["delta_U"] = none_df["U"] - none_df["U_shift"]

    # SDI = average delta_U over sessions (excluding NaN)
    sdi = none_df["delta_U"].iloc[1:].mean()
    out_path = PROC_DIR / "sdi_proxy.txt"
    with open(out_path, "w") as f:
        f.write(f"Approximate SDI proxy (mean delta U across sessions): {sdi:.4f}\n")
    print(f"Saved {out_path}")


def main():
    metrics_path = PROC_DIR / "session_metrics_v1.csv"
    if not metrics_path.exists():
        raise FileNotFoundError(f"{metrics_path} not found. Run generate_synthetic_data.py first.")
    make_summary_table(metrics_path)
    plot_eo_gap_over_sessions(metrics_path)
    plot_adi_over_sessions(metrics_path)
    sketch_sdi_from_metrics(metrics_path)


if __name__ == "__main__":
    main()
