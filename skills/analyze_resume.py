"""Skill: analyze_resume.

Use local Ollama when available, otherwise return deterministic analysis.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib import error, request


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

SPECIALIZATION_MAP = {
    "llm": "LLM Engineer",
    "prompt": "LLM Engineer",
    "machine learning": "Machine Learning Engineer",
    "ml": "Machine Learning Engineer",
    "data": "Data Engineer",
    "analytics": "Data Analyst",
    "api": "Backend Engineer",
    "backend": "Backend Engineer",
    "react": "Frontend Engineer",
    "ui": "Frontend Engineer",
    "design": "Product Engineer",
    "cloud": "Platform Engineer",
    "devops": "Platform Engineer",
}


def _infer_seniority(parsed_resume: dict[str, Any]) -> str:
    work_experience = parsed_resume.get("work_experience", [])
    text = " ".join(work_experience)
    years = re.findall(r"(20\d{2})", text)

    if years:
        numeric_years = sorted({int(year) for year in years})
        span = max(numeric_years) - min(numeric_years) + 1
        if span >= 8:
            return "Senior"
        if span >= 4:
            return "Mid-level"
        if span >= 2:
            return "Junior"

    lowered = text.lower()
    if any(keyword in lowered for keyword in ("lead", "staff", "principal", "manager", "senior")):
        return "Senior"
    if len(work_experience) >= 3:
        return "Mid-level"
    if work_experience:
        return "Junior"
    return "Unknown (Ollama unavailable)"


def _infer_specialization(parsed_resume: dict[str, Any]) -> str:
    skills = [str(skill) for skill in parsed_resume.get("skills", [])]
    lowered_blob = " ".join(skills + parsed_resume.get("work_experience", [])).lower()

    for token, specialization in SPECIALIZATION_MAP.items():
        if token in lowered_blob:
            return specialization

    return "Generalist"


def _fallback_analysis(parsed_resume: dict[str, Any]) -> dict[str, Any]:
    top_skills = [str(skill) for skill in parsed_resume.get("skills", [])[:3]]
    return {
        "seniority": _infer_seniority(parsed_resume),
        "specialization": _infer_specialization(parsed_resume),
        "top_skills": top_skills,
        "raw_analysis": {
            "note": "Local Ollama was unavailable, so fallback heuristics were used.",
        },
    }


def analyze_resume(parsed_resume: dict[str, Any], model: str = DEFAULT_MODEL) -> dict[str, Any]:
    prompt = (
        "You are a resume analysis assistant. "
        "Given the candidate profile below, return ONLY valid JSON with keys: "
        "seniority (string), specialization (string), top_skills (array of strings).\n\n"
        f"Candidate Profile:\n{json.dumps(parsed_resume, indent=2)}"
    )

    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
    ).encode("utf-8")

    req = request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})

    try:
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))

        llm_json = json.loads(body.get("response", "{}"))
        fallback = _fallback_analysis(parsed_resume)
        return {
            "seniority": llm_json.get("seniority", fallback["seniority"]),
            "specialization": llm_json.get("specialization", fallback["specialization"]),
            "top_skills": llm_json.get("top_skills", fallback["top_skills"]),
            "raw_analysis": llm_json,
        }
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError):
        return _fallback_analysis(parsed_resume)
