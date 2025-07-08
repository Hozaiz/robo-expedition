# ai_core/agent_router.py

from agents.blackbox_agent import fetch_blackbox_code, safe_execute
from ai_core.llama_agent import ask_ai_stream
from agents.research_agent import deep_research_answer


def route_message(agent: str, prompt: str):
    """
    Routes the user input to the correct AI service:
    - 'groq' streams LLaMA3 response (Groq API)
    - 'blackbox' gets code suggestion (Blackbox.ai)
    - 'blackbox_exec' executes provided code
    - 'deepresearch' performs web search, article fetch, summarization
    """
    if agent == "groq":
        return ask_ai_stream(prompt)

    if agent == "blackbox":
        result = fetch_blackbox_code(prompt)
        return result or "⚠️ No suggestion returned from Blackbox."

    if agent == "blackbox_exec":
        return safe_execute(prompt)

    if agent == "deepresearch":
        return deep_research_answer(prompt)

    return "❌ Unknown agent specified."
