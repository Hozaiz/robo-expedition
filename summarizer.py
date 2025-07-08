import tiktoken

# Reuse tokenizer for efficiency; compatible with Groq LLaMA3 and OpenAI models
ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")


def summarize_text(text: str, max_tokens: int = 1000) -> str:
    """
    Summarizes large text inputs by preserving beginning and end sections based on token count.
    Ideal for condensing long files before AI processing.

    Args:
        text (str): Raw input text.
        max_tokens (int): Desired token limit for the summary.

    Returns:
        str: Concise summary or original text if already within token limits.
    """
    if not text or not isinstance(text, str):
        return ""

    try:
        tokens = ENCODER.encode(text)

        if len(tokens) <= max_tokens:
            return text  # Already within limits

        half = max_tokens // 2
        first_tokens = tokens[:half]
        last_tokens = tokens[-half:]

        first_part = ENCODER.decode(first_tokens).strip()
        last_part = ENCODER.decode(last_tokens).strip()

        return (
            f"{first_part}\n\n"
            f"... [Content Trimmed for Length] ...\n\n"
            f"{last_part}"
        )

    except Exception as e:
        return f"⚠️ Summarization error: {str(e)}"
