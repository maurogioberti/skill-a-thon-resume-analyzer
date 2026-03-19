"""Minimal FastAPI server for the resume-skills MVP."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import error, request

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import run_resume_agent
from skills.analyze_resume import DEFAULT_MODEL, OLLAMA_URL, ollama_generate


app = FastAPI(title="Resume Skills MVP")
UI_INDEX = Path(__file__).parent / "ui" / "index.html"


class AnalyzeRequest(BaseModel):
    resume: str


def _fallback_welcome() -> str:
    return "Welcome to the hackathon demo. Drop in a resume and let the agent turn it into a sharp candidate snapshot."


def _generate_hackathon_welcome(model: str = DEFAULT_MODEL) -> str:
    prompt = (
        "Write exactly one sentence to welcome people to a resume analysis hackathon demo. "
        "Keep it upbeat, concise, and suitable for a landing page hero."
    )

    try:
        body = ollama_generate(prompt, model=model, timeout=10)
        welcome_text = body.get("response", "").strip()
        return welcome_text or _fallback_welcome()
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"[welcome] Ollama call failed, using fallback: {type(exc).__name__}: {exc}")
        return _fallback_welcome()


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(UI_INDEX)


@app.get("/welcome")
def welcome_message() -> dict[str, str]:
    return {"message": _generate_hackathon_welcome()}


@app.post("/analyze")
def analyze_resume_endpoint(request: AnalyzeRequest) -> dict[str, Any]:
    resume_text = request.resume.strip()
    if not resume_text:
        raise HTTPException(status_code=400, detail="resume is required.")

    return run_resume_agent(resume_text)
