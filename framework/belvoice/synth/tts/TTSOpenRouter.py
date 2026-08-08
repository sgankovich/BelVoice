import os
import re
import subprocess
import tempfile
from pathlib import Path

import requests


class TTSOpenRouter:
    """
    TTS праз OpenRouter з выкарыстаннем мадэлі Gemini TTS Preview.

    Дэталі: https://openrouter.ai/docs/features/audio
    """

    API_URL = "https://openrouter.ai/api/v1/audio/speech"
    DEFAULT_MODEL = "google/gemini-3.1-flash-tts-preview"
    DEFAULT_VOICE = "Charon"
    DEFAULT_REFERER = "https://github.com/Belarus/BelVoice"
    DEFAULT_TITLE = "BelVoice"

    def __init__(self, model_name: str = None, voice: str = None, api_key: str = None,
                 referer: str = None, title: str = None):
        self._model_name = model_name or self.DEFAULT_MODEL
        self._voice = voice or self.DEFAULT_VOICE
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self._api_key:
            raise Exception("Памылка: не ўстаноўлены OPENROUTER_API_KEY.")
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": referer or self.DEFAULT_REFERER,
            "X-OpenRouter-Title": title or self.DEFAULT_TITLE,
        }

    def _split_text(self, text: str, max_chars: int = 1500) -> list[str]:
        if len(text) <= max_chars:
            return [text]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current = ""
        for sentence in sentences:
            if current and len(current) + len(sentence) + 1 > max_chars:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip() if current else sentence
        if current:
            chunks.append(current)
        return chunks if chunks else [text[:max_chars]]

    def _is_pcm_target(self, output_path: str) -> bool:
        return Path(output_path).suffix.lower() in (".raw", ".pcm")

    def _synthesize(self, text: str) -> bytes:
        payload = {
            "model": self._model_name,
            "input": text,
            "voice": self._voice,
            "response_format": "pcm",
        }
        response = requests.post(
            self.API_URL,
            headers=self._headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.content

    def _convert_pcm(self, pcm_path: str, output_path: str):
        subprocess.run(
            ["ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", pcm_path, output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def tts(self, text: str, output_file_path: str):
        chunks = self._split_text(text)

        if self._is_pcm_target(output_file_path) and len(chunks) == 1:
            with open(output_file_path, "wb") as f:
                f.write(self._synthesize(chunks[0]))
            return

        pcm_parts = []
        for chunk in chunks:
            with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as tf:
                tf.write(self._synthesize(chunk))
                pcm_parts.append(tf.name)

        merged_pcm = tempfile.mktemp(suffix=".raw")
        try:
            with open(merged_pcm, "wb") as out:
                for path in pcm_parts:
                    with open(path, "rb") as part:
                        out.write(part.read())
                    os.remove(path)

            if self._is_pcm_target(output_file_path):
                os.replace(merged_pcm, output_file_path)
            else:
                self._convert_pcm(merged_pcm, output_file_path)
                os.remove(merged_pcm)
        except Exception:
            for path in pcm_parts:
                if os.path.exists(path):
                    os.remove(path)
            if os.path.exists(merged_pcm):
                os.remove(merged_pcm)
            raise
