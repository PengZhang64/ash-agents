from __future__ import annotations

import json
import os
import re
from typing import Any


class LLMClientError(Exception):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise LLMClientError("no JSON object in model response")
    return json.loads(match.group(0))


class OpenAICompatibleClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip(
            "/"
        )
        self.model = model or os.environ.get("ASH_LLM_MODEL", "gpt-4o-mini")
        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY is required")

    async def chat_json(self, system: str, user: str) -> dict[str, Any]:
        import httpx

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            if response.status_code >= 400:
                raise LLMClientError(f"LLM API error {response.status_code}: {response.text[:200]}")
            data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMClientError("unexpected LLM response shape") from exc
        return _extract_json(content)
