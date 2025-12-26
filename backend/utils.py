from __future__ import annotations
import pandas as pd
from typing import Dict, Tuple

REQUIRED = [
    "ticker",
    "period",
    "revenue",
    "cogs",
    "sga",
    "operating_income",
    "net_income",
    "total_assets",
    "total_liabilities",
    "equity",
    "cash",
    "receivables",
    "inventory",
]

ALIASES = {
    "sales": "revenue",
    "cost_of_goods_sold": "cogs",
    "operating_income_loss": "operating_income",
    "net_income_loss": "net_income",
    "assets_total": "total_assets",
    "liabilities_total": "total_liabilities",
}


def read_table_to_df(file_bytes: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        return pd.read_csv(pd.io.common.BytesIO(file_bytes))
    if filename.lower().endswith(".xlsx") or filename.lower().endswith(".xls"):
        return pd.read_excel(pd.io.common.BytesIO(file_bytes))
    raise ValueError("Unsupported file type. Please upload CSV or Excel.")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = [str(c).strip().lower() for c in df.columns]
    rename_map: Dict[str, str] = {}
    for c in cols:
        if c in REQUIRED:
            continue
        if c in ALIASES:
            rename_map[c] = ALIASES[c]
    df = df.rename(columns=rename_map)
    return df


def normalize_row(row: pd.Series) -> Dict[str, object]:
    norm: Dict[str, object] = {k: None for k in REQUIRED}
    for k in REQUIRED:
        if k in row:
            norm[k] = row[k]
    # Ensure numerics are floats where appropriate
    for k in REQUIRED:
        if k in ("ticker", "period"):
            continue
        try:
            norm[k] = float(norm[k]) if norm[k] is not None else 0.0
        except Exception:
            norm[k] = 0.0
    return norm
