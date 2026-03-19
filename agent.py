"""Simple orchestration layer for the resume-skills MVP."""

from __future__ import annotations

from typing import Any

from skills.analyze_resume import analyze_resume
from skills.enrich_company import enrich_company
from skills.parse_resume import parse_resume
from skills.summarize_candidate import summarize_candidate


def run_resume_agent(resume_text: str) -> dict[str, Any]:
    print("Agent starting")

    print("Step 1: parse_resume")
    parsed_resume = parse_resume(resume_text)

    print("Step 2: enrich_company")
    company_enrichment = [enrich_company(company) for company in parsed_resume.get("companies", [])]

    print("Step 3: analyze_resume")
    analysis = analyze_resume(parsed_resume)

    print("Step 4: summarize_candidate")
    summary = summarize_candidate(parsed_resume)

    return {
        "candidate": parsed_resume.get("candidate_name"),
        "parsed_resume": parsed_resume,
        "company_enrichment": company_enrichment,
        "analysis": analysis,
        "summary": summary,
    }
