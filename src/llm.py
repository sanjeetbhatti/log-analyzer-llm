import os
from functools import lru_cache
from typing import TypedDict

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()


class HealthStatus(TypedDict):
    healthy: bool
    message: str


@lru_cache(maxsize=1)
def _connect_to_client():
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()

    if not base_url:
        raise ValueError("LLM_BASE_URL is missing")
    if not api_key:
        raise ValueError("LLM_API_KEY is missing")
    if not model:
        raise ValueError("LLM_MODEL is missing")

    return OpenAI(base_url=base_url, api_key=api_key), model


def health_check() -> HealthStatus:
    try:
        client, model = _connect_to_client()
        client.chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=1,
            messages=[
                {"role": "user", "content": "ping"},
            ],
        )
        return {
            "healthy": True,
            "message": "LLM is available.",
        }
    except ValueError as err:
        return {
            "healthy": False,
            "message": f"Configuration Error: {err}",
        }
    except OpenAIError as err:
        return {
            "healthy": False,
            "message": f"LLM connection failed: {err}",
        }

def generate_summary(prompt: str) -> str:
    client, model = _connect_to_client()
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a concise debugging assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty response.")
    return text
