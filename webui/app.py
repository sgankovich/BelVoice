import json
import os
import sys
import uuid
from pathlib import Path

from flask import Flask, flash, render_template, request, send_from_directory, url_for

# Дазваляем імпартаваць belvoice з framework/ пры запуску з гэтага файла
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "framework"))

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "belvoice-webui-dev")

CONFIG_FILE = Path(__file__).resolve().parent / "ui_config.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "static" / "outputs"
UPLOAD_DIR = Path(__file__).resolve().parent / "static" / "uploads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "mistral_api_key": "",
    "mistral_chat_model": "mistral/mistral-small-latest",
    "mistral_tts_model": "voxtral-mini-tts-2603",
    "openrouter_api_key": "",
    "openrouter_chat_model": "openrouter/mistralai/mistral-small-3.1-24b-instruct",
    "openrouter_tts_model": "google/gemini-3.1-flash-tts-preview",
    "lmstudio_base_url": "http://localhost:1234/api/v1",
    "lmstudio_api_key": "",
    "lmstudio_model": "qwen/qwen3.6-35b-a3b",
    "gemini_api_key": "",
    "gemini_model": "gemini/gemini-3-flash-preview",
    "openai_base_url": "http://localhost:1234/v1",
    "openai_api_key": "lm-studio",
    "openai_model": "whisper-1",
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            merged = dict(DEFAULT_CONFIG)
            merged.update(saved)
            return merged
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config):
    safe = {k: config.get(k, DEFAULT_CONFIG.get(k, "")) for k in DEFAULT_CONFIG}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def env_or_value(key, value):
    if value:
        os.environ[key] = value
    return os.environ.get(key)


def get_llm_args(provider, config):
    if provider == "mistral":
        return {
            "model_name": config["mistral_chat_model"] or DEFAULT_CONFIG["mistral_chat_model"],
            "api_key": env_or_value("MISTRAL_API_KEY", config["mistral_api_key"].strip()),
        }
    if provider == "openrouter":
        return {
            "model_name": config["openrouter_chat_model"] or DEFAULT_CONFIG["openrouter_chat_model"],
            "api_key": env_or_value("OPENROUTER_API_KEY", config["openrouter_api_key"].strip()),
        }
    if provider == "lmstudio":
        return {
            "model_name": config["lmstudio_model"] or DEFAULT_CONFIG["lmstudio_model"],
            "api_key": config["lmstudio_api_key"].strip() or None,
            "api_base": config["lmstudio_base_url"] or DEFAULT_CONFIG["lmstudio_base_url"],
        }
    if provider == "gemini":
        return {
            "model_name": config["gemini_model"] or DEFAULT_CONFIG["gemini_model"],
            "api_key": env_or_value("GEMINI_API_KEY", config["gemini_api_key"].strip()),
        }
    return None


def normalize_text(text, provider, config):
    if not provider or provider == "none":
        return text
    if provider == "simple":
        from belvoice.synth.normalization.NormalizationSimple import NormalizationSimple
        return NormalizationSimple().normalize(text)
    args = get_llm_args(provider, config)
    if args:
        from belvoice.synth.normalization.NormalizationLLM import NormalizationLLM
        return NormalizationLLM(**args).normalize(text)
    return text


def apply_stress(text, provider, config):
    if not provider or provider == "none":
        return text
    if provider == "stat":
        from belvoice.synth.stress.StressStat import StressStat
        return StressStat().apply_stresses(text)
    args = get_llm_args(provider, config)
    if args:
        from belvoice.synth.stress.StressLLM import StressLLM
        return StressLLM(**args).apply_stresses(text)
    return text


def phonemize_text(text):
    from belvoice.synth.phonemization.PhonemizationBelG2P import PhonemizationBelG2P
    return PhonemizationBelG2P().convert(text)


def synthesize(text, provider, config, output_path: str):
    if provider == "coqui":
        from belvoice.synth.tts.TTSCoquiTTS import TTSCoquiTTS
        TTSCoquiTTS().tts(text, output_path)
    elif provider == "omnivoice":
        from belvoice.synth.tts.TTSOmniVoice import TTSOmniVoice
        TTSOmniVoice().tts(text, output_path)
    elif provider == "mistral":
        from belvoice.synth.tts.TTSMistral import TTSMistral
        model = config["mistral_tts_model"] or DEFAULT_CONFIG["mistral_tts_model"]
        api_key = env_or_value("MISTRAL_API_KEY", config["mistral_api_key"].strip())
        TTSMistral(model_name=model, api_key=api_key).tts(text, output_path)
    elif provider == "openrouter":
        from belvoice.synth.tts.TTSOpenRouter import TTSOpenRouter
        model = config["openrouter_tts_model"] or DEFAULT_CONFIG["openrouter_tts_model"]
        api_key = env_or_value("OPENROUTER_API_KEY", config["openrouter_api_key"].strip())
        TTSOpenRouter(model_name=model, api_key=api_key).tts(text, output_path)
    else:
        raise ValueError(f"Невядомы TTS-правайдэр: {provider}")


def transcribe(audio_path, provider, config):
    if provider == "gemini":
        from belvoice.asr.stt.STTGemini import STTGemini
        env_or_value("GEMINI_API_KEY", config["gemini_api_key"].strip())
        model = config["gemini_model"] or DEFAULT_CONFIG["gemini_model"]
        return STTGemini(model).transcript_file(audio_path)
    if provider == "openai":
        from belvoice.asr.stt.STTOpenAI import STTOpenAI
        model = config["openai_model"] or DEFAULT_CONFIG["openai_model"]
        api_base = config["openai_base_url"] or DEFAULT_CONFIG["openai_base_url"]
        api_key = env_or_value("OPENAI_API_KEY", config["openai_api_key"].strip()) or "lm-studio"
        return STTOpenAI(model_name=model, api_base=api_base, api_key=api_key).transcribe(audio_path)
    raise ValueError(f"Невядомы ASR-правайдэр: {provider}")


def run_pipeline(params):
    config = load_config()
    for key in DEFAULT_CONFIG:
        config[key] = params.get(key, DEFAULT_CONFIG[key])
    save_config(config)

    mode = params.get("mode", "tts")

    if mode == "tts":
        text = params.get("input_text", "")
        if not text.strip():
            raise ValueError("Увядзіце тэкст для сінтэзу.")

        normalizer = params.get("tts_normalization_provider", "none")
        stresser = params.get("tts_stress_provider", "none")
        phonemizer = params.get("tts_phonemization_provider", "none")
        tts_provider = params.get("tts_tts_provider", "coqui")

        steps = []
        current = text
        steps.append(("Уваход", current))

        if normalizer != "none":
            current = normalize_text(current, normalizer, config)
            steps.append(("Нармалізацыя", current))

        if stresser != "none":
            current = apply_stress(current, stresser, config)
            steps.append(("Натцiскі", current))

        if phonemizer != "none":
            current = phonemize_text(current)
            steps.append(("Фанемы", current))

        ext = ".mp3" if tts_provider == "mistral" else ".wav"
        output_filename = f"{uuid.uuid4().hex}{ext}"
        output_path = OUTPUT_DIR / output_filename
        synthesize(current, tts_provider, config, str(output_path))

        return {
            "mode": "tts",
            "audio_url": url_for("static", filename=f"outputs/{output_filename}"),
            "audio_path": str(output_path),
            "text": current,
            "steps": steps,
        }

    if mode == "asr":
        if "audio_file" not in request.files:
            raise ValueError("Запампуйце аўдыяфайл.")
        file = request.files["audio_file"]
        if file.filename == "":
            raise ValueError("Файл не выбраны.")
        upload_name = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = UPLOAD_DIR / upload_name
        file.save(upload_path)

        asr_provider = params.get("asr_provider", "gemini")
        text = transcribe(str(upload_path), asr_provider, config)
        return {
            "mode": "asr",
            "text": text,
            "upload_path": str(upload_path),
        }

    if mode == "normalization":
        text = params.get("input_text", "")
        provider = params.get("normalization_provider", "simple")
        result = normalize_text(text, provider, config)
        return {"mode": "normalization", "text": result}

    if mode == "stress":
        text = params.get("input_text", "")
        provider = params.get("stress_provider", "stat")
        result = apply_stress(text, provider, config)
        return {"mode": "stress", "text": result}

    if mode == "phonemization":
        text = params.get("input_text", "")
        result = phonemize_text(text)
        return {"mode": "phonemization", "text": result}

    raise ValueError(f"Невядомы рэжым: {mode}")


@app.route("/", methods=["GET", "POST"])
def index():
    config = load_config()
    result = None
    error = None

    if request.method == "POST":
        try:
            result = run_pipeline(request.form)
        except Exception as exc:
            error = str(exc)
            app.logger.exception("Памылка апрацоўкі")

    return render_template("index.html", config=config, result=result, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
