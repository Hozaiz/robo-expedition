import os
import requests
import io
import contextlib
import traceback
from dotenv import load_dotenv

load_dotenv()
BLACKBOX_API_KEY = os.getenv("BLACKBOX_API_KEY")

if not BLACKBOX_API_KEY:
    raise EnvironmentError("Missing BLACKBOX_API_KEY in environment variables.")


def fetch_blackbox_code(prompt: str) -> str:
    """
    Fetches code suggestion from Blackbox.ai using the DeepSeek LLaMA-8B model.
    Includes full error handling and JSON validation.
    """
    # CORRECTED API ENDPOINT
    url = "https://api.blackbox.ai/api/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BLACKBOX_API_KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    payload = {
        "model": "blackboxai/deepseek/deepseek-r1-distill-llama-8b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        # Detect HTML responses
        if response.text.strip().startswith("<!DOCTYPE html>"):
            return "❌ Received HTML response. Verify API endpoint is correct."
            
        response.raise_for_status()
        
        try:
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return "⚠️ No choices returned from Blackbox."
            return choices[0].get("message", {}).get("content", "").strip()
        except ValueError:
            return f"❌ Invalid JSON from API (status {response.status_code}):\n{response.text[:200]}"

    except requests.HTTPError as http_err:
        return f"❌ HTTP error occurred: {http_err}\nResponse: {response.text[:200]}"
    except requests.RequestException as req_err:
        return f"❌ Request failed: {str(req_err)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def safe_execute(code: str) -> str:
    """
    Executes basic Python code safely with restricted built-ins.
    Skips execution if code contains error symbols or messages.
    Returns stdout output or error message.
    """
    # Prevent executing error messages
    if not code or any(err in code for err in ["❌", "⚠️", "Blackbox API Error"]):
        return "⚠️ Cannot execute: This is not valid Python code."

    allowed_builtins = {
        "print": print,
        "len": len,
        "range": range,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "enumerate": enumerate,
        "zip": zip,
        "type": type
    }
    safe_globals = {"__builtins__": allowed_builtins}
    output = io.StringIO()

    try:
        with contextlib.redirect_stdout(output):
            exec(code, safe_globals)
    except Exception as e:
        return f"⚠️ Execution Error:\n{str(e)}"

    return output.getvalue().strip() or "✅ Code executed without output."
