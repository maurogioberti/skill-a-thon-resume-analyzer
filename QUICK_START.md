# Quick Start

## Step 1. Go to the project root

```bash
cd /Users/maurogioberti/work/skill-a-thon-resume-analyzer
```

## Step 2. Create the virtual environment

```bash
python3 -m venv .venv
```

## Step 3. Activate it

```bash
source .venv/bin/activate
```

## Step 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn pydantic
```

## Step 5. Run the syntax check

```bash
python -m py_compile agent.py demo.py server.py skills/__init__.py skills/parse_resume.py skills/enrich_company.py skills/analyze_resume.py skills/summarize_candidate.py
```

## Step 6. Run the CLI demo

```bash
python demo.py
```

## Step 7. Run the web app

```bash
python -m uvicorn server:app --reload
```

## Step 8. Open the browser

Open:

```text
http://127.0.0.1:8000
```

## Step 9. Test the UI

1. Paste or keep the sample resume.
2. Click `Analyze Resume`.
3. Check that you see:
   - Candidate
   - Level
   - Specialization
   - Top Skills
   - Companies
   - Summary

## Optional: local Ollama

If you want model-generated output instead of fallback output:

```bash
ollama serve
ollama pull llama3.2
```

Then run:

```bash
python -m uvicorn server:app --reload
```
