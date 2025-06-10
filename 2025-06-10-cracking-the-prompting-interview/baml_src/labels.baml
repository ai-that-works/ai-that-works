class Content {
     url string
     content string
}

class Answer {
    answer string
    citations int[] @description(#"
        index of the content
    "#)
}

function AnswerQuestion(question:string, contents: Content[]) -> Answer {
    client "openai/gpt-4o"
    prompt #"
        {{ ctx.output_format }}

        Relevant content:
        {% for content in contents %}
        ----
        content_{{ loop.index0 }}:
        {{ content.content }}
        {% endfor %}

        {{ _.role('user') }}
        {{ question }}
    "#
}

// Test the RAG function with sample content
test ai_history_question {
    functions [AnswerQuestion]
    args {
        question "What were the key developments in artificial intelligence in 2023?"
        contents [
            {
                url "https://www.youtube.com/watch?v=NMhH5_ju3-I"
                content #"
                    2023 was a landmark year for AI. GPT-4 was released by OpenAI in March, 
                    demonstrating unprecedented capabilities in reasoning and natural language understanding. 
                    Google introduced Gemini, while Anthropic released Claude 2.
                "#
            }
            {
                url "https://www.youtube.com/watch?v=D-pcKduKdYM"
                content #"
                    The impact of AI in 2023 extended beyond just technical achievements.
                    Open-source models like Llama 2 democratized access to powerful AI,
                    while AI regulation became a major focus with the EU AI Act and AI Executive Order.
                "#
            }
            {
                url "https://www.youtube.com/watch?v=D-pcKduKdYM"
                content #"
                    Europe is pretty cool and has great pasta
                "#
            }
        ]
    }
}

