import base64
import os
import re
import subprocess
import tempfile
from pathlib import Path

import requests


class TTSMistral:
    """
    TTS праз Mistral Voxtral API.

    Дакументацыя: https://docs.mistral.ai/capabilities/speech/
    """

    SPEECH_URL = "https://api.mistral.ai/v1/audio/speech"
    VOICES_URL = "https://api.mistral.ai/v1/audio/voices"
    DEFAULT_MODEL = "voxtral-mini-tts-2603"

    def __init__(self, model_name: str = None, voice_id: str = None, api_key: str = None):
        self._model_name = model_name or self.DEFAULT_MODEL
        self._api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self._api_key:
            raise Exception("Памылка: не ўстаноўлены MISTRAL_API_KEY.")
        self._voice_id = voice_id or self._resolve_voice_id()

    def _resolve_voice_id(self) -> str:
        response = requests.get(
            self.VOICES_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            params={"type": "preset", "limit": 100},
            timeout=30,
        )
        response.raise_for_status()
        voices = response.json().get("items", [])
        if not voices:
            raise Exception("Не атрымалася атрымаць спіс галасоў Mistral.")
        return voices[0]["id"]

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

    def _response_format(self, output_path: str) -> str:
        ext = Path(output_path).suffix.lower()
        if ext in (".mp3",):
            return "mp3"
        if ext in (".wav",):
            return "wav"
        if ext in (".flac",):
            return "flac"
        if ext in (".ogg",):
            return "ogg"
        return "mp3"

    def _synthesize(self, text: str, response_format: str) -> bytes:
        payload = {
            "input": text,
            "model": self._model_name,
            "response_format": response_format,
            "voice_id": self._voice_id,
        }
        response = requests.post(
            self.SPEECH_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return base64.b64decode(data["audio_data"])

    def tts(self, text: str, output_file_path: str):
        response_format = self._response_format(output_file_path)
        chunks = self._split_text(text)

        if len(chunks) == 1:
            audio = self._synthesize(chunks[0], response_format)
            with open(output_file_path, "wb") as f:
                f.write(audio)
            return

        part_files = []
        for chunk in chunks:
            with tempfile.NamedTemporaryFile(suffix=f".{response_format}", delete=False) as tf:
                tf.write(self._synthesize(chunk, response_format))
                part_files.append(tf.name)

        list_path = tempfile.mktemp(suffix=".txt")
        with open(list_path, "w", encoding="utf-8") as f:
            for part in part_files:
                f.write(f"file '{part}'\n")

        try:
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_file_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        finally:
            for part in part_files:
                os.remove(part)
            os.remove(list_path)
