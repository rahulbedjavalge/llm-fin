import os
from typing import Dict

# Placeholder LLM adapter. Replace with provider-specific calls as needed.
# Env vars: LLM_PROVIDER, OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, etc.


def analyze_financials(ratios: Dict[str, float]) -> Dict[str, object]:
    gm = ratios.get("gross_margin", 0.0)
    nm = ratios.get("net_margin", 0.0)
    lev = ratios.get("debt_to_assets", 0.0)
    inv_turn = ratios.get("inventory_turnover", 0.0)

    # Simple rule-based "LLM-like" output to keep MVP runnable without keys
    direction = "flat"
    if gm > 0.4 and nm > 0.15 and lev < 0.6:
        direction = "up"
    elif gm < 0.2 or nm < 0.05 or lev > 0.8:
        direction = "down"

    risk = "medium"
    if lev >= 0.75:
        risk = "high"
    elif lev <= 0.4:
        risk = "low"

    explanation = (
        f"Gross margin {gm:.1%}, net margin {nm:.1%}, leverage {lev:.0%}. "
        f"Inventory turnover {inv_turn:.2f}. Projecting {direction.upper()} with {risk.upper()} risk based on margins and leverage."
    )

    return {
        "direction": direction,
        "risk": risk,
        "explanation": explanation,
    }
