// Smoke-test cast. Every model id here was confirmed visible to this
// repo's API keys by smoke/list_models.py on 2026-07-27.
// NOTE: options fields must be newline-separated; one-lining them fails
// to parse with a misleading "invalid line" error on the client itself.

retry_policy Once {
  max_retries 1
}

// ---- incumbent: the model we pretend is being retired ----

client<llm> IncumbentGPT4o {
  provider openai
  retry_policy Once
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

// ---- same-provider candidates ----

client<llm> CandGPT4oMini {
  provider openai
  retry_policy Once
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> CandGPT55 {
  provider openai
  retry_policy Once
  options {
    model "gpt-5.5"
    api_key env.OPENAI_API_KEY
  }
}

// ---- cross-provider candidates: these carry the lock-in thesis ----

client<llm> CandSonnet5 {
  provider anthropic
  retry_policy Once
  options {
    model "claude-sonnet-5"
    api_key env.ANTHROPIC_API_KEY
    max_tokens 4096
  }
}

client<llm> CandGemini36Flash {
  provider google-ai
  retry_policy Once
  options {
    model "gemini-3.6-flash"
    api_key env.GOOGLE_API_KEY
  }
}

client<llm> CandGemini35Flash {
  provider google-ai
  retry_policy Once
  options {
    model "gemini-3.5-flash"
    api_key env.GOOGLE_API_KEY
  }
}

client<llm> CandGemini35FlashLite {
  provider google-ai
  retry_policy Once
  options {
    model "gemini-3.5-flash-lite"
    api_key env.GOOGLE_API_KEY
  }
}
