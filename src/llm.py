import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _connect_to_client():
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    return OpenAI(base_url=base_url, api_key=api_key), model

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
        return "LLM returned an empty response."
    return text
