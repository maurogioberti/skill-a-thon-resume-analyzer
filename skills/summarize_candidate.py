"""Skill: summarize_candidate.

Generate a short professional summary from the parsed resume.
"""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from skills.analyze_resume import DEFAULT_MODEL, ollama_generate


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

    try:
        body = ollama_generate(prompt, model=model, timeout=30)
        summary = body.get("response", "").strip()
        return summary or _fallback_summary(parsed_resume)
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"[summarize_candidate] Ollama call failed, using fallback: {type(exc).__name__}: {exc}")
        return _fallback_summary(parsed_resume)
