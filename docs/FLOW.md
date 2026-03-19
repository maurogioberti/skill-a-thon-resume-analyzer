# Runtime Flow

## End-to-end

```text
Browser UI or CLI input
    |
    v
run_resume_agent()
    |
    +--> parse_resume()
    +--> enrich_company()
    +--> analyze_resume()
    +--> summarize_candidate()
    |
    v
Formatted CLI output or JSON API response
```

## Notes

- The flow is synchronous and intentionally easy to demo.
- Ollama is optional.
- If Ollama is unavailable, the project still returns useful output using local fallback logic.
