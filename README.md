# Resume-Skills

This repo is a hackathon-friendly MVP that analyzes a resume using small reusable AI skills.

## Install

```bash
pip install git+https://github.com/maurogioberti/skill-a-thon-resume-analyzer.git
```

## What it does

The app runs a simple pipeline:

1. `parse_resume` extracts structured candidate data
2. `enrich_company` adds local company metadata
3. `analyze_resume` infers seniority, specialization, and top skills
4. `summarize_candidate` creates a short candidate summary

The project includes:

- a CLI demo in `demo.py`
- a FastAPI backend in `server.py`
- a single-file web UI in `ui/index.html`
- a sample markdown resume in `resume.md`

## Quick start

See [HOW_TO_USE.md](./HOW_TO_USE.md) for run and test instructions.

## Project structure

```text
.
├── skills/
├── docs/
├── ui/
├── references/
├── agent.py
├── demo.py
├── server.py
├── resume.md
├── README.md
└── HOW_TO_USE.md
```
