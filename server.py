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
from skills.analyze_resume import DEFAULT_MODEL, OLLAMA_URL


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
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")

    req = request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
        welcome_text = body.get("response", "").strip()
        return welcome_text or _fallback_welcome()
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError):
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
