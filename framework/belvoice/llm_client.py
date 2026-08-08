import os

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


def resolve_api_key(provided: str | None, env_names: list[str]) -> str | None:
    """Вяртае ключ: перададзены ўручную ці з пераменных асяроддзя."""
    if provided:
        return provided
    for name in env_names:
        value = os.environ.get(name)
        if value:
            return value
    return None
