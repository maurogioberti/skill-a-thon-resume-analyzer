"""Skill: summarize_candidate.

Generate a short professional summary from the parsed resume.
"""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from skills.analyze_resume import DEFAULT_MODEL, OLLAMA_URL


def _fallback_summary(parsed_resume: dict[str, Any]) -> str:
    name = parsed_resume.get("candidate_name", "The candidate")
    skills = [str(skill) for skill in parsed_resume.get("skills", [])[:3]]
    companies = [str(company) for company in parsed_resume.get("companies", [])[:2]]
    work_experience = [str(item) for item in parsed_resume.get("work_experience", [])]

    skills_text = ", ".join(skills) if skills else "technical problem solving"
    company_text = f" across {', '.join(companies)}" if companies else ""
    role_text = work_experience[0] if work_experience else "hands-on product and engineering work"

    return (
        f"{name} brings strengths in {skills_text}{company_text}. "
        f"Recent experience includes {role_text}."
    )


def summarize_candidate(parsed_resume: dict[str, Any], model: str = DEFAULT_MODEL) -> str:
    prompt = (
        "Write a short professional summary for this candidate in two sentences or fewer. "
        "Keep it concise, specific, and presentation-friendly.\n\n"
        f"Candidate Profile:\n{json.dumps(parsed_resume, indent=2)}"
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
        with request.urlopen(req, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))

        summary = body.get("response", "").strip()
        return summary or _fallback_summary(parsed_resume)
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError):
        return _fallback_summary(parsed_resume)
