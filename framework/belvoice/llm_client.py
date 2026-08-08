import os

import requests

import litellm

litellm.suppress_debug_info = True

from litellm import completion


class LiteLLMClient:
    """
    Агульны кліент для chat-completion праз LiteLLM.

    Падтрымлівае Mistral (префікс `mistral/`), OpenRouter (префікс `openrouter/`),
    а таксама лакальныя OpenAI-сумяшчальныя серверы кшталту LMStudio
    (префікс `openai/` + api_base).
    """

    def __init__(self, model_name: str, api_key: str = None, api_base: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base

    def chat(self, messages: list, temperature: float = 0.0, **kwargs) -> str:
        return completion(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            api_key=self.api_key,
            api_base=self.api_base,
            **kwargs,
        )


class LMStudioClient:
    """
    Родны кліент для LMStudio `/api/v1/chat`.

    Endpoint чакае `model`, `input`, `system_prompt`, `temperature` і вяртае
    JSON з `output[0].content`. Працуе з любым запушчаным локальна LMStudio.
    """

    DEFAULT_BASE = "http://localhost:1234/api/v1"

    def __init__(self, model_name: str, api_key: str = None, api_base: str = None):
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = (api_base or os.environ.get("LMSTUDIO_BASE_URL") or self.DEFAULT_BASE).rstrip("/")
        self._url = f"{self.api_base}/chat"

    def _response(self, content: str):
        class Message:
            pass
        msg = Message()
        msg.content = content

        class Choice:
            pass
        choice = Choice()
        choice.message = msg

        class Response:
            pass
        response = Response()
        response.choices = [choice]
        return response

    def chat(self, messages: list, temperature: float = 0.0, **kwargs) -> str:
        system_prompt = ""
        user_inputs = []
        for message in messages:
            if message.get("role") == "system":
                system_prompt = message.get("content", "")
            elif message.get("role") == "user":
                user_inputs.append(message.get("content", ""))

        if not user_inputs:
            raise ValueError("Няма user-паведамленняў для LMStudio /api/v1/chat")

        payload = {
            "model": self.model_name,
            "input": user_inputs[-1],
            "system_prompt": system_prompt,
            "temperature": temperature,
            "store": False,
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(self._url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        output = data.get("output", [])
        if not output:
            raise ValueError(f"Пусты output ад LMStudio: {data}")

        content = output[0].get("content", "")
        return self._response(content)


def make_client(model_name: str, api_key: str = None, api_base: str = None):
    """
    Стварае адпаведнага LLM-кліента.

    - `api_base`, які змяшчае `/api/v1` (але не `/v1/chat/completions`),
      лічыцца родным LMStudio endpoint.
    - У іншым выпадку выкарыстоўваецца LiteLLM (OpenAI-сумяшчальны).
    """
    base = api_base or os.environ.get("LMSTUDIO_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    if base and "/api/v1" in base and "/v1/chat/completions" not in base:
        return LMStudioClient(model_name, api_key=api_key, api_base=base)
    return LiteLLMClient(model_name, api_key=api_key, api_base=base)


def resolve_api_key(provided: str | None, env_names: list[str]) -> str | None:
    """Вяртае ключ: перададзены ўручную ці з пераменных асяроддзя."""
    if provided:
        return provided
    for name in env_names:
        value = os.environ.get(name)
        if value:
            return value
    return None
