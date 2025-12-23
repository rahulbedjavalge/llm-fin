from __future__ import annotations
import os
from typing import Optional, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from . import utils, ratios as ratios_mod, baseline, llm
from .models import UploadResponse, Ratios, RedFlags, AnalyzeResponse, LLMAnalysis, BaselinePrediction

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


# Uvicorn entrypoint: `uvicorn backend.main:app --reload`
