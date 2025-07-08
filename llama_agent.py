# ai_core/llama_agent.py

import os
import requests
import json
from dotenv import load_dotenv
from backend.memory_manager import conversation_history, add_to_history

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY in your environment variables.")


def ask_ai_stream(prompt: str):
    """
    Streams LLaMA3 responses via Groq API. Yields content chunks in real time.
    Adds conversation to memory for context retention.
    """
    url = url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    add_to_history("user", prompt)

    payload = {
        "model": "llama3-8b-8192",
        "messages": conversation_history,
        "stream": True
    }

    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=30) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        content = (
                            data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except requests.RequestException as e:
        yield f"[Groq API Error: {str(e)}]"
