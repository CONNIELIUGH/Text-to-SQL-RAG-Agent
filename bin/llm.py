import json
import re
from typing import Any
from ollama import Client
from .config import settings 
from .prompts import SYSTEM_PROMPT

def get_client() -> Client:
    if settings.ollama_host:
        return Client(host=settings.ollama_host)
    return Client()


def _get_message_content(response: Any) -> str:
    try:
        return response["message"]["content"]
    except Exception: 
        return response.message.content
    


def extract_json_object(text: str) -> dict:
    text = text.strip()

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    candidate = text[start : end + 1]
    return json.loads(candidate)


def call_agent_llm(context_prompt: str) -> dict:
    client = get_client()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": context_prompt,
        }
    ]


    try: 
        response = client.chat(
            model=settings.ollama_model,
            messages=messages,
            format="json",
            stream=False,
            options={
                "temperature": 0,
            },
        )
    except TypeError:
        response = client.chat(
            model=settings.ollama_model,
            messages=messages,
            stream=False,
            options={
                "temperature": 0,
            }
        )
    
    content = _get_message_content(response)
    return extract_json_object(content)





