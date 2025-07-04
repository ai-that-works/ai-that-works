# 🦄 Boosting AI Output Quality

> This week's ai that works session was a bit meta! We explored "Boosting AI Output Quality" by building the very AI pipeline that generated this email from our Zoom recording.

[Video](https://www.youtube.com/watch?v=HsElHU44xJ0)

[![Boosting AI Output Quality](https://img.youtube.com/vi/HsElHU44xJ0/0.jpg)](https://www.youtube.com/watch?v=HsElHU44xJ0)

## Key Takeaways

1. **It's an Architecture Problem, Not a Prompt Problem** - Before you write a single prompt, you have to whiteboard the data flow. Getting the data plumbing right—making sure all the correct links, dates, and topics are available—is 90% of the battle.

2. **Use a Two-Step "Extract, then Polish" Pipeline** - The real breakthrough was separating the task into two steps. First, a dedicated LLM call extracts the raw facts and key points from the transcript into a structured format. Then, a second LLM call polishes those facts into a well-toned message. This avoids that robotic, "Mad Libs" feel and gives you much higher quality output.

> If you remember one thing from this session: High-quality AI generation isn't about one magic prompt. It's an engineered system that first extracts facts reliably and then polishes them for tone and flow. Separate your data pipeline from your creative pipeline.

## Whiteboards (not AI generated)

Our architecture diagram (which we used to parallelize work + define the problem)
![image](https://github.com/user-attachments/assets/112ea93e-0f59-4370-9243-fd6d8e6c2320)

General idea when thinking about prompting:
![image](https://github.com/user-attachments/assets/f8d92f97-44cc-418c-85fb-c9e7fba6899d)



## Running the Code

```bash
# Backend setup
cd backend
uv sync
cp env.template .env
# Configure your environment variables

# Frontend setup
cd frontend
npm install
npm run dev

# Run the full pipeline
uv run python main.py
```

## Resources

- [Session Recording](https://www.youtube.com/watch?v=HsElHU44xJ0)
- [Full Recording and Code on GitHub](https://github.com/hellovai/ai-that-works)
- [Discord Community](https://www.boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

---

PS this README was generated with our content pipeline. How did we do?
