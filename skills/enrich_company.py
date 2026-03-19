"""Skill: enrich_company.

Map company names to small demo-friendly metadata.
"""

from __future__ import annotations


COMPANY_LOOKUP: dict[str, dict[str, str]] = {
    "openai": {
        "industry": "Artificial Intelligence",
        "description": "Builds and deploys advanced AI models and products.",
    },
    "acme analytics": {
        "industry": "Data & Analytics",
        "description": "Provides analytics platforms and decision-support services.",
    },
    "cloudnine": {
        "industry": "Cloud Infrastructure",
        "description": "Delivers cloud-native platforms, DevOps support, and platform reliability services.",
    },
    "brightpath health": {
        "industry": "Digital Health",
        "description": "Creates patient-facing healthcare products with data and workflow automation.",
    },
    "northstar commerce": {
        "industry": "E-commerce",
        "description": "Builds digital commerce experiences and growth tooling for online retailers.",
    },
}


def enrich_company(company_name: str) -> dict[str, str]:
    normalized = company_name.strip()
    details = COMPANY_LOOKUP.get(
        normalized.casefold(),
        {
            "industry": "Unknown",
            "description": "No company description is available in the local lookup yet.",
        },
    )
    return {"company": normalized or "Unknown Company", **details}
