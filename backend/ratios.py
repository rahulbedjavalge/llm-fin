from __future__ import annotations
from typing import Dict, Tuple, List
import math

RequiredSchema = [
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


def _safe_div(a: float, b: float) -> float:
    try:
        if b == 0 or math.isclose(b, 0.0):
            return 0.0
        return float(a) / float(b)
    except Exception:
        return 0.0


def compute_ratios(row: Dict[str, float]) -> Dict[str, float]:
    revenue = float(row.get("revenue", 0.0) or 0.0)
    cogs = float(row.get("cogs", 0.0) or 0.0)
    op_inc = float(row.get("operating_income", 0.0) or 0.0)
    net_inc = float(row.get("net_income", 0.0) or 0.0)
    assets = float(row.get("total_assets", 0.0) or 0.0)
    liab = float(row.get("total_liabilities", 0.0) or 0.0)
    equity = float(row.get("equity", 0.0) or 0.0)
    cash = float(row.get("cash", 0.0) or 0.0)
    recv = float(row.get("receivables", 0.0) or 0.0)
    inv = float(row.get("inventory", 0.0) or 0.0)

    gross_margin = _safe_div((revenue - cogs), revenue)
    operating_margin = _safe_div(op_inc, revenue)
    net_margin = _safe_div(net_inc, revenue)

    debt_to_assets = _safe_div(liab, assets)
    debt_to_equity = _safe_div(liab, equity)

    receivables_turnover = _safe_div(revenue, recv)
    inventory_turnover = _safe_div(cogs if cogs > 0 else revenue, inv)

    cash_to_revenue = _safe_div(cash, revenue)
    current_assets = cash + recv + inv
    current_assets_to_liabilities = _safe_div(current_assets, liab)

    return {
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "net_margin": net_margin,
        "debt_to_assets": debt_to_assets,
        "debt_to_equity": debt_to_equity,
        "receivables_turnover": receivables_turnover,
        "inventory_turnover": inventory_turnover,
        "cash_to_revenue": cash_to_revenue,
        "current_assets_to_liabilities": current_assets_to_liabilities,
    }


def derive_red_flags(r: Dict[str, float]) -> List[str]:
    flags: List[str] = []
    if r["gross_margin"] < 0.2:
        flags.append("Low gross margin")
    if r["net_margin"] < 0.05:
        flags.append("Low net margin")
    if r["debt_to_assets"] > 0.7:
        flags.append("High leverage (debt/assets)")
    if r["debt_to_equity"] > 2.0:
        flags.append("High leverage (debt/equity)")
    if r["cash_to_revenue"] < 0.05:
        flags.append("Low cash relative to revenue")
    if r["inventory_turnover"] < 2.0:
        flags.append("Slow inventory turnover")
    return flags
