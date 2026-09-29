import json
import urllib.error
import urllib.request

from config.settings import Settings


class DeepSeekError(RuntimeError):
    pass


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def configured(self) -> bool:
        return self.settings.deepseek_api_key is not None

    def complete(self, prompt: str) -> str:
        if self.settings.deepseek_api_key is None:
            raise DeepSeekError("DEEPSEEK_API_KEY is not configured")
        body = json.dumps(
            {
                "model": self.settings.deepseek_model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "max_tokens": 800,
                "temperature": 0.2,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.settings.deepseek_base_url.rstrip("/") + "/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.settings.deepseek_api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.settings.request_timeout_seconds
            ) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, KeyError, ValueError) as exc:
            raise DeepSeekError(f"DeepSeek request failed: {exc}") from exc
