"""Skill: parse_resume.

Extract structured candidate data from markdown-first resume text.
"""

from __future__ import annotations

import re
from typing import Any


SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SKILL_LINE_PATTERN = re.compile(r"^[\-\*\u2022]\s*(.+)$")
EXPERIENCE_HINTS = ("engineer", "developer", "scientist", "manager", "lead", "intern", "analyst")


def _clean_lines(block: str) -> list[str]:
    return [line.strip() for line in block.splitlines() if line.strip()]


def _extract_markdown_section(resume_text: str, section_names: tuple[str, ...]) -> str:
    sections = list(SECTION_PATTERN.finditer(resume_text))
    lowered_targets = {name.lower() for name in section_names}

    for index, match in enumerate(sections):
        section_name = match.group(1).strip().lower()
        if section_name not in lowered_targets:
            continue

        start = match.end()
        end = sections[index + 1].start() if index + 1 < len(sections) else len(resume_text)
        return resume_text[start:end].strip()

    return ""


def _extract_name(resume_text: str) -> str:
    heading_match = re.search(r"^#\s+(.+)$", resume_text, flags=re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()

    for line in _clean_lines(resume_text):
        if line.startswith("##"):
            continue
        if len(line.split()) <= 5 and not re.search(r"[:@/]", line):
            return line

    return "Unknown Candidate"


def _parse_skill_lines(block: str) -> list[str]:
    skills: list[str] = []

    for raw_line in _clean_lines(block):
        bullet_match = SKILL_LINE_PATTERN.match(raw_line)
        if bullet_match:
            value = bullet_match.group(1).strip()
            if value:
                skills.append(value)
            continue

        for token in re.split(r"[,|/]", raw_line):
            value = token.strip()
            if value:
                skills.append(value)

    return _dedupe(skills)


def _extract_skills(resume_text: str) -> list[str]:
    skills_block = _extract_markdown_section(resume_text, ("skills", "technical skills", "core skills"))
    if skills_block:
        return _parse_skill_lines(skills_block)

    inline_match = re.search(r"skills?\s*:\s*(.+)", resume_text, flags=re.IGNORECASE)
    if inline_match:
        return _parse_skill_lines(inline_match.group(1))

    candidates: list[str] = []
    for line in _clean_lines(resume_text):
        if re.search(r"\b(python|llm|machine learning|fastapi|sql|api|react|aws|data)\b", line, flags=re.IGNORECASE):
            candidates.extend(_parse_skill_lines(line))

    return _dedupe(candidates)


def _extract_work_experience(resume_text: str) -> list[str]:
    work_block = _extract_markdown_section(
        resume_text,
        ("work experience", "experience", "professional experience", "employment"),
    )
    if work_block:
        entries = []
        for line in _clean_lines(work_block):
            bullet_match = SKILL_LINE_PATTERN.match(line)
            entries.append(bullet_match.group(1).strip() if bullet_match else line)
        return _dedupe(entries)

    entries: list[str] = []
    for line in _clean_lines(resume_text):
        lowered = line.lower()
        if " at " in lowered or any(hint in lowered for hint in EXPERIENCE_HINTS):
            entries.append(line.lstrip("-* ").strip())

    return _dedupe(entries)


def _extract_companies(work_experience: list[str], resume_text: str) -> list[str]:
    companies: list[str] = []

    for entry in work_experience:
        at_split = re.split(r"\bat\b", entry, maxsplit=1, flags=re.IGNORECASE)
        if len(at_split) == 2:
            company = re.split(r"[\(\|\-]", at_split[1], maxsplit=1)[0].strip(" ,.")
            if company:
                companies.append(company)

    if companies:
        return _dedupe(companies)

    company_matches = re.findall(r"\b(?:at|with)\s+([A-Z][A-Za-z0-9&.\- ]+)", resume_text)
    return _dedupe([match.strip(" ,.") for match in company_matches if match.strip()])


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        key = normalized.casefold()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def parse_resume(resume_text: str) -> dict[str, Any]:
    work_experience = _extract_work_experience(resume_text)

    return {
        "candidate_name": _extract_name(resume_text),
        "skills": _extract_skills(resume_text),
        "work_experience": work_experience,
        "companies": _extract_companies(work_experience, resume_text),
    }
