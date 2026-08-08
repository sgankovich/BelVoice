import os
from pathlib import Path

import requests


class STTOpenAI:
    """
    Распазнаванне маўлення праз OpenAI-сумяшчальны `/audio/transcriptions` endpoint.

    Працуе з:
    - лакальным LMStudio, калі загружаная мадэль Whisper (`http://localhost:1234/v1`);
    - уласным OpenAI-правайдэрам ці іншым сумяшчальным серверам.
    """

    DEFAULT_MODEL = "whisper-1"

    def __init__(self, model_name: str = None, api_base: str = None, api_key: str = None):
        self._model_name = model_name or self.DEFAULT_MODEL
        self._api_base = api_base or os.environ.get("OPENAI_API_BASE") or "http://localhost:1234/v1"
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY") or "lm-studio"

    def _endpoint(self) -> str:
        base = self._api_base.rstrip("/")
        return f"{base}/audio/transcriptions"

    def transcribe(self, audio_file_path: str, language: str = None) -> str:
        """Вяртае тэкст транскрыпцыі аднаго аўдыяфайла."""
        data = {"model": self._model_name}
        if language:
            data["language"] = language

        with open(audio_file_path, "rb") as f:
            files = {"file": (Path(audio_file_path).name, f)}
            headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
            response = requests.post(
                self._endpoint(),
                headers=headers,
                files=files,
                data=data,
                timeout=120,
            )

        response.raise_for_status()
        return response.json().get("text", "")
