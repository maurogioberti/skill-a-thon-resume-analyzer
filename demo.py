"""Hackathon demo entrypoint for the resume-skills MVP."""

from __future__ import annotations

from pathlib import Path

from agent import run_resume_agent


def _format_companies(company_enrichment: list[dict[str, str]]) -> str:
    if not company_enrichment:
        return "- None"

    lines: list[str] = []
    for company in company_enrichment:
        lines.append(f"- {company.get('company', 'Unknown Company')} ({company.get('industry', 'Unknown')})")
        lines.append(f"  {company.get('description', 'No description available.')}")
    return "\n".join(lines)


def main() -> None:
    resume_text = Path("resume.md").read_text(encoding="utf-8")
    result = run_resume_agent(resume_text)

    analysis = result.get("analysis", {})
    top_skills = analysis.get("top_skills", [])

    print("===== Resume Skills MVP =====")
    print()
    print(f"Candidate: {result.get('candidate', 'Unknown Candidate')}")
    print(f"Level: {analysis.get('seniority', 'Unknown')}")
    print(f"Specialization: {analysis.get('specialization', 'Generalist')}")
    print()

    print("Top Skills:")
    if top_skills:
        for skill in top_skills:
            print(f"- {skill}")
    else:
        print("- None identified")
    print()

    print("Companies:")
    print(_format_companies(result.get("company_enrichment", [])))
    print()

    print("Summary:")
    print(result.get("summary", "Professional summary unavailable."))


if __name__ == "__main__":
    main()
