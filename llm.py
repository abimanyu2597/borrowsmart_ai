"""
Groq LLM Wrapper — uses .env GROQ_API_KEY.
Only explains tool outputs; never recomputes numbers.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).parent / ".env")

_SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.txt"
_SYSTEM_PROMPT = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

_client: Groq | None = None
MODEL = "llama-3.3-70b-versatile"


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not found. Add it to your .env file.")
        _client = Groq(api_key=api_key)
    return _client


def get_llm_explanation(user_query: str, tool_outputs: str) -> str:
    client = _get_client()

    user_message = (
        f"User Question: {user_query}\n\n"
        f"Tool Results (use these numbers exactly, do NOT recompute):\n{tool_outputs}"
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.35,
            max_tokens=900,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ Could not generate explanation: {e}"