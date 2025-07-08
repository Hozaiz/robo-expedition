# Core conversation initialization with persistent AI context
conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]

# Temporary chat memory for sidebar user events
chat_memory = []

# Configurable Limits
MAX_HISTORY_LENGTH = 50   # Keeps AI context window reasonable
MAX_CHAT_MEMORY = 100     # Prevents sidebar memory overflow


def add_to_memory(entry: str) -> None:
    """
    Adds user events or prompts to sidebar memory with safety checks.
    """
    if isinstance(entry, str) and entry.strip():
        chat_memory.append(entry)
        if len(chat_memory) > MAX_CHAT_MEMORY:
            chat_memory.pop(0)


def get_chat_memory() -> list:
    """
    Returns a copy of current chat memory for UI display.
    """
    return chat_memory.copy()


def add_to_history(role: str, content: str) -> None:
    """
    Adds structured messages to persistent conversation history for AI.
    Ensures system prompt and recent context are retained.
    """
    if role in {"user", "assistant", "system"} and isinstance(content, str) and content.strip():
        conversation_history.append({"role": role, "content": content})

        if len(conversation_history) > MAX_HISTORY_LENGTH:
            # Retain system prompt and most recent exchanges
            conversation_history[:] = [conversation_history[0]] + conversation_history[-(MAX_HISTORY_LENGTH - 1):]


def get_conversation_history() -> list:
    """
    Provides a copy of structured conversation history for AI context.
    """
    return conversation_history.copy()
