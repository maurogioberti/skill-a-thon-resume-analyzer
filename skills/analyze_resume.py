"""Skill: analyze_resume.

Use local Ollama when available, otherwise return deterministic analysis.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib import error, request


OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
DEFAULT_MODEL = "llama3:8b"
PREFERRED_MODELS = (DEFAULT_MODEL, "llama3.2", "llama3")

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


def resolve_ollama_model(preferred_model: str = DEFAULT_MODEL) -> str:
    try:
        with request.urlopen(OLLAMA_TAGS_URL, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"[resolve_ollama_model] Could not reach Ollama tags endpoint: {type(exc).__name__}: {exc}")
        return preferred_model

    model_names = [model.get("name", "").strip() for model in body.get("models", []) if model.get("name")]
    if not model_names:
        return preferred_model

    if preferred_model in model_names:
        return preferred_model

    for candidate in PREFERRED_MODELS:
        if candidate in model_names:
            return candidate

    return model_names[0]


def ollama_generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    *,
    timeout: int = 30,
    response_format: str | None = None,
) -> dict[str, Any]:
    resolved_model = resolve_ollama_model(model)
    print(f"[ollama_generate] Using model: {resolved_model}")
    payload_dict: dict[str, Any] = {
        "model": resolved_model,
        "prompt": prompt,
        "stream": False,
    }
    if response_format:
        payload_dict["format"] = response_format

    payload = json.dumps(payload_dict).encode("utf-8")
    req = request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})

    with request.urlopen(req, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))

    body["_resolved_model"] = resolved_model
    return body


def analyze_resume(parsed_resume: dict[str, Any], model: str = DEFAULT_MODEL) -> dict[str, Any]:
    prompt = (
        "You are a resume analysis assistant. "
        "Given the candidate profile below, return ONLY valid JSON with keys: "
        "seniority (string), specialization (string), top_skills (array of strings).\n\n"
        f"Candidate Profile:\n{json.dumps(parsed_resume, indent=2)}"
    )

    try:
        body = ollama_generate(prompt, model=model, timeout=30, response_format="json")
        llm_json = json.loads(body.get("response", "{}"))
        fallback = _fallback_analysis(parsed_resume)
        return {
            "seniority": llm_json.get("seniority", fallback["seniority"]),
            "specialization": llm_json.get("specialization", fallback["specialization"]),
            "top_skills": llm_json.get("top_skills", fallback["top_skills"]),
            "raw_analysis": {
                **llm_json,
                "_resolved_model": body.get("_resolved_model", model),
            },
        }
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"[analyze_resume] Ollama call failed, using fallback: {type(exc).__name__}: {exc}")
        return _fallback_analysis(parsed_resume)
