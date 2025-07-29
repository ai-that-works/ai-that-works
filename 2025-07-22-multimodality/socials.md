# Social Media Posts - AI That Works #15: PDFs, Multimodality, Vision Models

## Twitter/X

### Twitter post 1

when you send a PDF to an LLM, here's what actually happens...

it extracts all transactions, gets a summary, then validates against your expected total. if >N failures, send to human for review

the magic: runtime evals catch errors BEFORE they reach production. hybrid AI systems ftw

![extraction pipeline whiteboard](https://github.com/user-attachments/assets/6ff39e3b-4aa1-407f-b603-bdadac38c190)

link to full episode with Vaibhav on llm image/pdf processing in comments

### Twitter post 2

just spent 90 min showing how to hack PDFs with vision models… turns out LLMs dont actually read PDFs they just pretend to 😅

learned the hard way: when claude says it can "read your PDF" what it really means is "lemme convert this to janky images first then maybe hallucinate the numbers"

solution? take control of the preprocessing yourself. use pixel diffing to remove headers/footers. validate outputs with actual math

![whiteboard](https://github.com/user-attachments/assets/21c223c6-5669-4603-98d4-03f10d4641e3)

link to full episode with Vaibhav on llm image/pdf processing in comments

### Twitter post 3

TIL: vision models quietly resize your images before processing them

claude's max resolution is 1092x1092px before automatic resizing kicks in. anything larger gets scaled down to fit ~1600 tokens ($4.80/1k images on sonnet 3.7)

i can only assume these limits reflect training data resolutions. if you're processing high-detail documents, consider pre-resizing to these specs yourself rather than letting the provider handle it

![tokenization whiteboard](https://github.com/user-attachments/assets/fe425e7f-3825-4dc1-bfd6-16f03781750e)

link to full episode with Vaibhav on llm image/pdf processing in comments

### Twitter post 4

this graph haunts me every time i build an AI pipeline

20 steps at 99% accuracy each = only 81% overall success rate
20 steps at 97% accuracy each = 54% success rate

the lesson: every +1% accuracy improvement matters way more than you think. and maybe... use fewer steps

![accuracy compound graph](https://github.com/user-attachments/assets/d92ec658-6f5b-48a4-a1bd-7068f5929d37)

link to full episode with Vaibhav on llm image/pdf processing in comments

### Links

link to code from the episode: https://github.com/hellovai/ai-that-works/tree/main/2025-07-22-multimodality/

sign up for the next livestream tuesday at 10am PT - https://lu.ma/gnvx0iic