import sys
from pathlib import Path
import pandas as pd

# Allow imports from backend
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import utils, ratios as ratios_mod, baseline, llm  # type: ignore


def main():
    sample = ROOT / "data" / "sample_financials.csv"
    df = pd.read_csv(sample)
    df = utils.normalize_columns(df)
    row = df.iloc[-1]
    norm = utils.normalize_row(row)
    r = ratios_mod.compute_ratios(norm)
    flags = ratios_mod.derive_red_flags(r)

    base = baseline.predict(r)
    analysis = llm.analyze_financials(r)

    print("Ratios:", r)
    print("Red flags:", flags)
    print("Baseline:", base)
    print("LLM (heuristic):", analysis)


if __name__ == "__main__":
    main()
