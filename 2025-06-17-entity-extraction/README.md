# Entity Resolution: Extraction, Deduping, and Enriching

> Disambiguating many ways of naming the same thing (companies, skills, etc.) - from entity extraction to resolution to deduping.

[Video](https://youtu.be/niR896pQWOQ) (1h15m)

[![Entity Resolution & De-duping](https://img.youtube.com/vi/niR896pQWOQ/0.jpg)](https://www.youtube.com/watch?v=niR896pQWOQ)

Links:

- [https://github.com/BoundaryML/baml-examples/tree/main/extract-anything](extract-anything)
- [Related Session: Large Scale Classification](../2025-03-31-large-scale-classification/)

## Key Takeaways

- **Separate Extraction from Resolution**: Extract "what string did the user type?" first, then resolve "which row in my DB?" separately
- **Two-Stage Design for Scale**: List-in-prompt fails beyond ~500 companies; use staged queues instead of bigger prompts
- **Heuristics Before LLMs**: Straight alias matching covers 80% of cases - save LLM calls for the hard 20%
- **Type-Signature Mindset**: Treat every LLM call as a pure function; swap implementations without rewriting call-sites
- **Status-Driven Async Workflow**: Use database status columns (proposed/ready/committed) to enable human-in-loop and future automation
- **Start Expensive, Then Optimize**: Ship with big models first, collect ground-truth data, then optimize when it hurts

## Whiteboards

![image](https://github.com/user-attachments/assets/f5d14eda-445e-4e04-bf4b-589ca437a409)

* * *

![image](https://github.com/user-attachments/assets/6460b1fd-2780-4985-865c-45ecd9510a1d)


## Core Architecture

### Pipeline Stages
1. **Extraction**: Extract entities from raw text with small models (gpt-4o-mini, llama3:8b)
2. **Resolution**: Match extracted entities to canonical database entries
3. **Enrichment**: Queue unknown entities for web search and human review

### Data Models
```python
class Company(BaseModel):
    name_verbatim: str          # Raw text from input
    legal_name: str|None        # Canonical name if known
    company_type: Literal["well_known", "well_known_subsidiary", "startup"]

class Experience(BaseModel):
    company: Company
    title: str
```

### Database Schema
```sql
companies(id, legal_name, aliases[], status, last_updated, updated_by)
experiences(id, resume_id, company_id, ...)

-- Statuses: proposed, ready, committed
```

## Resolution Workflow

1. **Direct Match**: Check if `legal_name` exists in company dictionary
2. **Alias Matching**: Try to match `name_verbatim` against known aliases
3. **Async Enrichment**: Queue unknown companies for:
   - LLM-powered web search
   - Human review and approval
   - Back-fill to original record

## Running the Code

```bash
uv sync
uv run hello.py
uvx baml-cli test
```

## Test Cases

The BAML configuration includes test cases for:
- **Clear entities**: "Microsoft", "Google" � direct resolution
- **Ambiguous aliases**: "GCP" � "Google Cloud Platform", "XBOX" � "Microsoft"
- **Unknown startups**: Queue for enrichment pipeline

## Scaling Patterns

- **Batch Processing**: Run cheap heuristics first, fall back to LLM for failures
- **Cost Optimization**: Capture F1 metrics to know when to train custom small models  
- **Human Gates**: Choose automation level based on risk (tax systems need approval, ATS can auto-commit)

## Design Principles

- **Complexity Budget**: Break problems into extraction � resolution � enrichment layers
- **Guardrails**: Runtime type checks and retries prevent silent hallucinations  
- **Ground Truth Collection**: Start with expensive accurate methods, then optimize with data
- **Async by Design**: Use SQS/queues for enrichment to avoid blocking main pipeline

## Resources

- [Session Recording](https://youtu.be/niR896pQWOQ)
- [BAML Documentation](https://docs.boundaryml.com/)
- [Discord Community](https://www.boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)
