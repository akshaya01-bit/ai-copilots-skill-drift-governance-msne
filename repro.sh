#!/usr/bin/env bash
set -e

echo "[repro] Activating virtual environment (if present)..."
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate || echo "[repro] Could not activate .venv; ensure dependencies are installed."
else
  echo "[repro] No .venv directory found; assuming dependencies are available on PATH."
fi

echo "[repro] Installing Python dependencies (if needed)..."
if command -v pip >/dev/null 2>&1; then
  pip install -r requirements.txt
else
  echo "[repro] pip not found; please ensure numpy, pandas, scikit-learn, matplotlib (and optionally scipy) are installed."
fi

echo "[repro] Generating synthetic data..."
python src/generate_synthetic_data.py

echo "[repro] Computing metrics and plots..."
python src/compute_metrics_and_plots.py

echo "[repro] Running causal / power demo (optional)..."
python src/causal_and_power_demo.py || echo "[repro] causal_and_power_demo.py completed with a warning (likely missing scipy)."

echo "[repro] Done. Outputs:"
echo "  - data/raw/sample_decisions_*.csv"
echo "  - data/processed/session_metrics_*.csv, summary_metrics_by_arm.csv"
echo "  - data/processed/itt_demo_eo_gap.csv, sdi_proxy.txt, power_sketch.txt (if available)"
echo "  - figures/*.png"
