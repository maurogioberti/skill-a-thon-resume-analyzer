# How To Use

## Requirements

- Python 3.10+
- Optional: local Ollama for model-powered analysis and summaries

## Install backend dependencies

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn pydantic
```

If you already have these packages available globally, you can skip the virtual environment and use your existing setup.

## Run the CLI demo

```bash
python3 demo.py
```

Expected behavior:

- the agent prints each pipeline step in order
- a formatted report is shown with candidate details, skills, companies, and summary

## Run the API and web UI

```bash
source .venv/bin/activate
python -m uvicorn server:app --reload
```

Then open `http://127.0.0.1:8000`.

Expected behavior:

- `GET /` serves the UI
- paste or edit resume text in the textarea
- click `Analyze Resume`
- the page renders candidate, level, specialization, top skills, companies, and summary

## Optional: enable local Ollama

Without Ollama, the app uses deterministic fallback logic so the demo still works.

To enable live model output:

```bash
ollama serve
ollama pull llama3.2
```

Then rerun the demo or the API server.

## Test commands

```bash
python3 -m py_compile agent.py demo.py server.py skills/__init__.py skills/parse_resume.py skills/enrich_company.py skills/analyze_resume.py skills/summarize_candidate.py
```

```bash
python3 demo.py
```

```bash
source .venv/bin/activate
python -m uvicorn server:app --reload
```

## Swap the sample resume

Edit `resume.md`, then rerun the demo or paste the new text into the browser UI.
