# 🦄 policy to prompt: evaluating the enron email dataset against SEC regulations

one of the most common problems in AI engineering is looking at a set of policies / rules and evaluating evidence to determine if the rules were followed. In this session we'll explore turning policies into prompts and pipelines to evaluate which emails in the massive [enron email dataset](https://www.cs.cmu.edu/~enron/) violated SEC and Sarbanes-Oxley regulations.

[Video](https://www.youtube.com/watch?v=gkekVC67iVs) • [RSVP](https://lu.ma/iw1d9l3j)

<a href="https://www.youtube.com/watch?v=gkekVC67iVs"><img width="1019" alt="Screenshot 2025-05-22 at 10 29 53 PM" src="https://github.com/user-attachments/assets/68c43941-f249-4c92-9a69-54db5e4a62ee" /></a>


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

![image](https://github.com/user-attachments/assets/fcd7f73b-ee1f-485d-8771-f09176b54196)

![image](https://github.com/user-attachments/assets/d18c4c82-e3b2-4eca-922a-b5e80f37956f)

![image](https://github.com/user-attachments/assets/ddd2cddc-a596-4ef0-8543-4aacbbd76a7f)

![image](https://github.com/user-attachments/assets/c76ab794-5f21-4e07-963e-2f65c6b7cbf5)


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
