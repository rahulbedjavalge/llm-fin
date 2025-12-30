from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd

from . import utils, ratios as ratios_mod, baseline, llm
from .models import UploadResponse, Ratios, RedFlags, AnalyzeResponse, LLMAnalysis, BaselinePrediction, MetricsHistory, ComparisonMetrics

app = FastAPI(title="LLM Financial Statement Copilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE: Dict[str, object] = {
    "last_row": None,
    "last_ratios": None,
    "last_flags": None,
    "history": [],  # List of MetricsHistory
    "previous_ratios": None,
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    try:
        data = await file.read()
        df = utils.read_table_to_df(data, file.filename)
        df = utils.normalize_columns(df)
        if df.empty:
            raise ValueError("No rows found in file.")
        # Take last row as latest period
        row = df.iloc[-1]
        norm = utils.normalize_row(row)
        r = ratios_mod.compute_ratios(norm)
        flags = ratios_mod.derive_red_flags(r)
        STATE["last_row"] = norm
        STATE["last_ratios"] = r
        STATE["last_flags"] = flags
        return UploadResponse(
            ticker=str(norm.get("ticker")) if norm.get("ticker") is not None else None,
            period=str(norm.get("period")) if norm.get("period") is not None else None,
            ratios=Ratios(**r),
            red_flags=RedFlags(flags=flags),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ratios", response_model=UploadResponse)
async def get_ratios():
    if STATE["last_ratios"] is None or STATE["last_row"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    norm = STATE["last_row"]
    r = STATE["last_ratios"]
    flags = STATE["last_flags"] or []
    return UploadResponse(
        ticker=str(norm.get("ticker")) if norm and norm.get("ticker") is not None else None,
        period=str(norm.get("period")) if norm and norm.get("period") is not None else None,
        ratios=Ratios(**r),
        red_flags=RedFlags(flags=flags),
    )


@app.get("/baseline", response_model=BaselinePrediction)
async def baseline_predict():
    if STATE["last_ratios"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    pred = baseline.predict(STATE["last_ratios"])  # type: ignore
    return BaselinePrediction(**pred)


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze():
    if STATE["last_ratios"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    r = STATE["last_ratios"]
    flags = STATE["last_flags"] or []

    llm_out = llm.analyze_financials(r)  # placeholder, replace with provider
    base_out = baseline.predict(r)

    agreement = (llm_out.get("direction") == base_out.get("direction"))

    return AnalyzeResponse(
        llm=LLMAnalysis(**llm_out),
        baseline=BaselinePrediction(**base_out),
        agreement=bool(agreement),
        ratios=Ratios(**r),
        red_flags=RedFlags(flags=flags),
    )


@app.get("/flags", response_model=RedFlags)
async def get_flags():
    if STATE["last_flags"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    return RedFlags(flags=STATE["last_flags"] or [])


@app.get("/export/csv")
async def export_csv():
    """Export last analysis results as CSV"""
    if STATE["last_ratios"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    
    ratios = STATE["last_ratios"]
    df = pd.DataFrame([ratios])
    csv_str = df.to_csv(index=False)
    
    return StreamingResponse(
        iter([csv_str]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=financial_ratios.csv"}
    )


@app.get("/export/json")
async def export_json():
    """Export last analysis results as JSON"""
    if STATE["last_ratios"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    
    norm = STATE["last_row"]
    r = STATE["last_ratios"]
    flags = STATE["last_flags"] or []
    
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "ticker": str(norm.get("ticker")) if norm and norm.get("ticker") else None,
        "period": str(norm.get("period")) if norm and norm.get("period") else None,
        "ratios": r,
        "red_flags": flags,
    }
    
    return StreamingResponse(
        iter([json.dumps(export_data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=financial_analysis.json"}
    )


@app.get("/history", response_model=List[MetricsHistory])
async def get_history():
    """Get analysis history"""
    return STATE.get("history", [])


@app.post("/compare")
async def compare_metrics() -> List[ComparisonMetrics]:
    """Compare current ratios with previous upload"""
    if STATE["last_ratios"] is None:
        raise HTTPException(status_code=404, detail="No data uploaded yet")
    
    current = STATE["last_ratios"]
    previous = STATE.get("previous_ratios")
    
    comparison = []
    for metric_name, current_value in current.items():
        if previous and metric_name in previous:
            prev_value = previous[metric_name]
            change = ((current_value - prev_value) / abs(prev_value)) * 100 if prev_value != 0 else 0
            comparison.append(ComparisonMetrics(
                metric_name=metric_name,
                current_value=current_value,
                previous_value=prev_value,
                change_percent=change
            ))
        else:
            comparison.append(ComparisonMetrics(
                metric_name=metric_name,
                current_value=current_value
            ))
    
    return comparison


# Uvicorn entrypoint: `uvicorn backend.main:app --reload`
