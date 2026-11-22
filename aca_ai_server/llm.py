"""Minimal OpenAI-compatible client (llama-server, llama-swap, LiteLLM)."""

from dataclasses import dataclass, field

import httpx

from . import config


@dataclass
class Reply:
    content: str
    timings: dict = field(default_factory=dict)
    usage: dict = field(default_factory=dict)


def chat(
    messages: list,
    *,
    model: str | None = None,
    thinking: bool = False,
    temperature: float = 0.2,
    max_tokens: int = 512,
    **extra,
) -> Reply:
    body = {
        "model": model or config.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": thinking},
        **extra,
    }
    r = httpx.post(
        f"{config.LLM_BASE_URL}/chat/completions",
        json=body,
        headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
        timeout=config.LLM_TIMEOUT,
    )
    r.raise_for_status()
    d = r.json()
    return Reply(
        d["choices"][0]["message"]["content"], d.get("timings", {}), d.get("usage", {})
    )


def vision(prompt: str, image_data_url: str, system: str | None = None, **kw) -> Reply:
    msgs = [{"role": "system", "content": system}] if system else []
    msgs.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ],
        }
    )
    return chat(msgs, **kw)
