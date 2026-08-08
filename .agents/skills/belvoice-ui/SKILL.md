---
name: BelVoice Web UI End-to-End Testing
description: How to set up and drive the BelVoice testing web UI for end-to-end validation.
---

# Devin Secrets Needed
- `MISTRAL_API_KEY`
- `OPENROUTER_API_KEY`
- `GEMINI_API_KEY` (optional, only for ASR)

# Environment setup
- Source venv: `source /home/ubuntu/belvoice_env/bin/activate`
- Java 21: `export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64`
- PYTHONPATH: `export PYTHONPATH=/home/ubuntu/repos/BelVoice/framework`

# Run the Flask web UI
```bash
/home/ubuntu/belvoice_env/bin/python /home/ubuntu/repos/BelVoice/webui/app.py
```
The app listens on `http://localhost:5000`.

When real cloud keys are needed, pass them through the `env` parameter of `exec` rather than hard-coding:
```
MISTRAL_API_KEY=secret:session:MISTRAL_API_KEY
OPENROUTER_API_KEY=secret:session:OPENROUTER_API_KEY
```

# Mode devinids (from a recent snapshot)
- TTS pipeline: `0`
- ASR: `1`
- Normalization: `2`
- Stress: `3`
- Phonemization: `4`

# Test notes
- CoquiTTS (local) outputs WAV.
- Mistral Voxtral outputs MP3.
- OpenRouter / Gemini TTS outputs WAV.
- Normalization and Stress with `mistral/` and `openrouter/` work through the single-mode selectors.
- ASR depends on `GEMINI_API_KEY` (Gemini) or a running LMStudio at `localhost:1234` (OpenAI-compatible). Without them the UI shows the expected error banner.

# Known gotchas
- The `<textarea>` and text inputs are not reliably cleared by `press_key Backspace`; use `Control+a` followed by `type`, or set the value via `browser console` (`document.getElementById('...').value = '...'`) to avoid appended input.
- `select_option` updates `selectedIndex` correctly, but the returned HTML snapshot may show stale `selected="true"` attributes. Trust the request/response result, not the snapshot markup, for provider state.
- After submitting config fields, the form is repopulated from the config loaded at the start of the request, so newly saved values do **not** appear until the next page reload.
- Filling API keys in the UI writes them to `webui/ui_config.json` and sets `os.environ` for the running Flask process. To switch back to environment-provided keys, restore `ui_config.json` to empty defaults and restart the Flask server.
