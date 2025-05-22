# 🦄 policy to prompt: evaluating the enron email dataset against SEC regulations

one of the most common problems in AI engineering is looking at a set of policies / rules and evaluating evidence to determine if the rules were followed. In this session we'll explore turning policies into prompts and pipelines to evaluate which emails in the massive [enron email dataset](https://www.cs.cmu.edu/~enron/) violated SEC and Sarbanes-Oxley regulations.

[Video](https://www.youtube.com/watch?v=gkekVC67iVs) • [RSVP](https://lu.ma/iw1d9l3j)



## Key Topics

1. Policy-to-Prompt Workflows
    - Mapping compliance policies (Sarbanes-Oxley, JP Morgan Code of Conduct) to automated LLM checks
    - Focusing on specific rules (gift-giving) rather than generic policy systems
    - Building targeted evaluation pipelines

1. Iterative Evaluation Loop
    - Start with vibe evals (playground testing)
    - Add deterministic pytest cases
    - Capture intermediate pipeline steps
    - Use structured outputs (e.g. Pydantic models)

3. Scaling & Tooling Patterns
    - Regex pre-filtering → async LLM calls → structured analysis
    - Parallel processing with asyncio.gather
    - Batch processing for large datasets
    - Progress tracking with tqdm

4. Human-in-the-Loop & Golden Dataset
    - Store analyzed emails as JSON files
    - Enable reviewer triage of high-risk cases
    - Build golden dataset from production traffic
    - Monitor for drift and expand test cases

Aside - 12-Factor / ShadCN-for-Agents Mindset
- Open, customizable scaffold approach vs closed systems
- Developers own and version their agent code
- Flexibility to tweak and adapt


## Whiteboards



## Running this code

### installing dependencies

```bash
# Install dependencies
uv sync
```

### Download the datasetsa

```bash
uv run datasets.py

```



### Run the code

```
# Run the code:
python pipeline.py
```