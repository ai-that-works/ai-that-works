# 🎯 Cracking the Prompting Interview

> Ready to level up your prompting skills? Join us for a deep dive into advanced prompting techniques that separate good prompt engineers from great ones. We'll cover systematic prompt design, evaluation frameworks, and tackle real interview-style prompting challenges.

[Video](https://youtu.be/PU2h0V-pANQ)

## 🎯 Key Takeaways

- **Use Indexes for URLs & Citations**: Provide content with simple IDs (e.g., [SOURCE_1]) and have the LLM output these IDs. Map them back programmatically to improve accuracy and reduce token load.
- **Index-Based Diarization**: For tasks like speaker diarization, have the LLM output the index of the dialogue turn and the identified speaker (e.g., {"dialogue_idx": 0, "speaker": "Nurse"}).
- **Context & "Escape Hatches" for Classification**: Provide relevant context upfront and include an "Other" or "Unknown" category to handle ambiguity.
- **Reasoning via "Busted" JSON/Comments**: Include LLM reasoning as comments or non-standard fields in structured output for easier debugging.
- **Natural Code Generation (in JSON)**: Generate code within Markdown-style backticks as a string field in JSON for higher quality output.
- **RTFP (Read The...Prompt!)**: Carefully review prompts for potential ambiguities that might confuse the LLM.

## 📝 Whiteboards

## 🚀 Running the Code

### Prerequisites

- Basic understanding of LLMs and prompting
- API access to major LLM providers (OpenAI, Anthropic, etc.)
- Programming experience (python)

### Quick Setup

```bash
uv sync
uv run hello.py
uvx run baml-cli test
```

## 📖 Resources

- [Session Recording](https://youtu.be/PU2h0V-pANQ)
- [Discord Community](https://www.boundaryml.com/discord) - Join the discussion and share your prompting experiences
- Sign up for the next session on [Luma](https://lu.ma/baml)
