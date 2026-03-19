# API

## Endpoints

### `GET /`

Serves the single-file browser UI from `ui/index.html`.

### `POST /analyze`

Accepts a JSON body with resume text and returns the full result from `run_resume_agent(...)`.

Request:

```json
{
  "resume": "resume text"
}
```

Response shape:

```json
{
  "candidate": "John Doe",
  "parsed_resume": {
    "candidate_name": "John Doe",
    "skills": ["Python", "LLM Engineering", "Prompt Design"],
    "work_experience": ["Senior AI Engineer at OpenAI (2023-Present)"],
    "companies": ["OpenAI"]
  },
  "company_enrichment": [
    {
      "company": "OpenAI",
      "industry": "Artificial Intelligence",
      "description": "Builds and deploys advanced AI models and products."
    }
  ],
  "analysis": {
    "seniority": "Senior",
    "specialization": "LLM Engineer",
    "top_skills": ["Python", "LLM Engineering", "Prompt Design"],
    "raw_analysis": {}
  },
  "summary": "John Doe brings strengths in Python, LLM Engineering, Prompt Design."
}
```

Validation:

- empty `resume` returns HTTP 400
- valid requests run the sequential agent pipeline and return JSON
