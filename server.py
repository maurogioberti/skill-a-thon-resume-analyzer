"""Minimal FastAPI server for the resume-skills MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import run_resume_agent


app = FastAPI(title="Resume Skills MVP")
UI_INDEX = Path(__file__).parent / "ui" / "index.html"


class AnalyzeRequest(BaseModel):
    resume: str


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(UI_INDEX)


@app.post("/analyze")
def analyze_resume_endpoint(request: AnalyzeRequest) -> dict[str, Any]:
    resume_text = request.resume.strip()
    if not resume_text:
        raise HTTPException(status_code=400, detail="resume is required.")

    return run_resume_agent(resume_text)
