# BelVoice — падрабязная інструкцыя па выкарыстанні

Гэты дакумент змяшчае прылады, прыклады і асаблівасці запуску кожнага модуля фрэймворку **BelVoice** на macOS (Apple Silicon, M5).

---

## 1. Базавае ўсталяванне

### 1.1. Патрабаванні

- Python **≥ 3.12** (шмат DL-бібліятэк працуе толькі на 3.11–3.12, таму на M5 рэкамендуецца `conda`/Miniforge з Python 3.12).
- Усталяваны `ffmpeg`:
  ```bash
  brew install ffmpeg
  ```
- Для `PhonemizationBelG2P` патрэбная Java:
  ```bash
  brew install openjdk
  ```

### 1.2. Усталёўка пакета

У каталогу з рэпазіторыем:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```

Для працы з цяжкімі мадэлямі лепш выкарыстоўваць `conda`:

```bash
conda create --name belvoice python=3.12
conda activate belvoice
pip install -e .
```

### 1.3. Актывацыя асяроддзя

Перад кожным запускам:

```bash
source .venv/bin/activate
# альбо
conda activate belvoice
```

---

## 2. Модульная арганізацыя

Кожны этап апрацоўкі — асобны клас. Камбінацыя модуляў адбываецца праз звычайныя выклікі:

- **TTS** (сінтэз): `нармалізацыя → націскі → фанемізацыя → TTS`
- **ASR** (распазнаванне): `разбіўка → (merge) → STT → (ITN)`

`__init__.py` ва ўсіх пакетах пустыя, таму імпарт выконваецца непасрэдна па файле з класам.

---

## 3. Модулі сінтэзу (TTS)

### 3.1. `NormalizationSimple`

- **Прызначэнне**: пераўтварае лічбы 0–9 і лацінскія літары ў словы. Рускія `и`/`щ` → `і`/`шч`.
- **Залежнасці**: няма.

```python
from belvoice.synth.normalization.NormalizationSimple import NormalizationSimple

text = "Ён адказаў ABC-123"
normalized = NormalizationSimple().normalize(text)
print(normalized)
# Ён адказаў  эй  бі  сі - адзін  два  тры
```

### 3.2. `NormalizationLLM`

- **Прызначэнне**: разумная нармалізацыя праз вялікую моўную мадэль.
- **Залежнасці**: `litellm==1.83.13` і API-ключ (напрыклад, `GEMINI_API_KEY`).
- **Параметры**: `model_name` з https://models.litellm.ai/.

```python
import os
from belvoice.synth.normalization.NormalizationLLM import NormalizationLLM

os.environ["GEMINI_API_KEY"] = "your_key"
normalizer = NormalizationLLM("gemini/gemini-3-flash-preview")
text = normalizer.normalize("Сустрэча а 14:30 у офісе EPAM.")
print(text)
```

### 3.3. `StressStat`

- **Прызначэнне**: расстаноўка націскаў па статыстычным слоўніку.
- **Залежнасці**: няма.

```python
from belvoice.synth.stress.StressStat import StressStat

text = "Ён адказаў ?"
stressed = StressStat().apply_stresses(text)
print(stressed)
# ё́н адказа́ў ?
```

### 3.4. `StressLLM`

- **Прызначэнне**: расстаноўка націскаў з улікам кантэксту праз LLM.
- **Залежнасці**: `litellm==1.84.0` і API-ключ.
- **Параметры**: `model_name` (толькі `gemini/...`).

```python
import os
from belvoice.synth.stress.StressLLM import StressLLM

os.environ["GEMINI_API_KEY"] = "your_key"
stress = StressLLM("gemini/gemini-3-flash-preview")
text = stress.apply_stresses("Ён адказаў ?")
print(text)
```

### 3.5. `PhonemizationBelG2P`

- **Прызначэнне**: пераўтварэнне тэксту з націскамі ў фанемную транскрыпцыю (BelG2P).
- **Залежнасці**: `jpype1==1.7.0`, `pooch==1.9.0`, Java.
- **Асаблівасці**: пры першым запуску спампоўваецца ~22 MiB jar-файл.

```python
from belvoice.synth.phonemization.PhonemizationBelG2P import PhonemizationBelG2P

phonemizer = PhonemizationBelG2P()
phonemes = phonemizer.convert("ё́н адказа́ў")
print(phonemes)
# jˈɔn atkazˈau̯
```

### 3.6. `TTSCoquiTTS`

- **Прызначэнне**: сінтэз гаворкі праз CoquiTTS, навучанай на беларускіх галасах.
- **Залежнасці**: `TTS==0.22.0` (патрабуе Python 3.11). Мадэль спампоўваецца аўтаматычна з HuggingFace.
- **Метад**: `tts(text, output_file_path)`.

```python
from belvoice.synth.tts.TTSCoquiTTS import TTSCoquiTTS

synth = TTSCoquiTTS()
synth.tts("jˈɔn atkazˈau̯", "output-coqui.wav")
print("Захавана ў output-coqui.wav")
```

### 3.7. `TTSOmniVoice`

- **Прызначэнне**: SOTA-сінтэз праз OmniVoice.
- **Залежнасці**: `omnivoice==0.1.2`.
- **Заўвага**: патрабуе GPU. На Mac M5 `mps` можа не падтрымлівацца.

```python
from belvoice.synth.tts.TTSOmniVoice import TTSOmniVoice

synth = TTSOmniVoice()
synth.tts("Ён адказаў ?", "output-omnivoice.wav")
```

---

## 4. Модулі распазнавання (ASR)

### 4.1. `SplitSileroVAD`

- **Прызначэнне**: разбіўка аўдыё на маўленчыя сегменты праз Silero VAD.
- **Залежнасці**: `silero-vad==6.2.1`, `torch`, `numpy`.
- **Метад**: `split(audio_file_path, **vad_params)`.
- **Вынік**: `VoiceFile` са спісам `VoicePart`.

```python
from belvoice.asr.split.SplitSileroVAD import SplitSileroVAD

splitter = SplitSileroVAD()
data = splitter.split("test.wav")
print(data.to_string())
```

### 4.2. `SplitPyannote`

- **Прызначэнне**: разбіўка/дыярызацыя праз `pyannote`.
- **Залежнасці**: `pyannote.audio==4.0.4`.
- **Параметры**: `segmentation_only=True` (толькі VAD) ці `False` (з дыярызацыяй спікераў).
- **Заўвага**: можа запатрабаваць токен HuggingFace.

```python
from belvoice.asr.split.SplitPyannote import SplitPyannote

splitter = SplitPyannote(segmentation_only=True)
data = splitter.split("test.wav")
print(data.to_string())
```

### 4.3. `SttFacebook` (`STTFacebook`)

- **Прызначэнне**: распазнаванне праз Omnilingual ASR.
- **Залежнасці**: PyTorch 2.8.0, `fairseq2==0.6.0`, `omnilingual_asr`.
- **Мадэлі**: `omniASR_LLM_Unlimited_300M_v2`, `omniASR_LLM_Unlimited_1B_v2`.
- **Метады**:
  - `transcript_file(audio_path)` — увесь файл.
  - `transcript_parts(voice_file)` — па сегментах.

```python
from belvoice.asr.stt.STTFacebook import SttFacebook
from belvoice.asr.SplitData import VoiceFile

asr = SttFacebook("omniASR_LLM_Unlimited_300M_v2")

# Поўны файл
text = asr.transcript_file("test.wav")
print(text)

# Па частках
data = VoiceFile.load_from_json("test.json", audio_files_base=".")
asr.transcript_parts(data)
print(data.to_string())
```

### 4.4. `STTNvidia`

- **Прызначэнне**: распазнаванне праз Nvidia NeMo.
- **Залежнасці**: `nemo_toolkit[asr]==2.7.3`.
- **Падтрымліваемыя мадэлі**:
  - `nvidia/stt_be_fastconformer_hybrid_large_pc`
  - `nvidia/stt_be_conformer_transducer_large`
  - `nvidia/stt_be_conformer_ctc_large`
- **Параметры**: `model_name`, `att_context_size=[128, 128]` для доўгіх файлаў.

```python
from belvoice.asr.stt.STTNvidia import STTNvidia
from belvoice.asr.SplitData import VoiceFile

asr = STTNvidia("nvidia/stt_be_fastconformer_hybrid_large_pc")

# Поўны файл
text = asr.transcript_file("test.wav")
print(text)

# Па частках
data = VoiceFile.load_from_json("test.json", audio_files_base=".")
asr.transcript_parts(data)
print(data.to_string())
```

### 4.5. `STTGemini`

- **Прызначэнне**: распазнаванне праз Google Gemini API.
- **Залежнасці**: `litellm==1.83.13`, `GEMINI_API_KEY`.
- **Падтрымліваемыя фарматы**: wav, mp3, ogg, opus, aac, flac.
- **Метады**:
  - `transcript_file(audio_path)` — увесь файл.
  - `transcript_parts(voice_file)` — па сегментах.
  - `transcript_parts_with_timestamps(voice_file)` — з таймстэмпамі.

```python
import os
from belvoice.asr.stt.STTGemini import STTGemini
from belvoice.asr.SplitData import VoiceFile

os.environ["GEMINI_API_KEY"] = "your_key"

asr = STTGemini("gemini/gemini-3-flash-preview")

# Поўны файл
text = asr.transcript_file("test.wav")
print(text)

# Па частках з таймстэмпамі
data = VoiceFile.load_from_json("test.json", audio_files_base=".")
asr.transcript_parts_with_timestamps(data)
print(data.to_string())
```

### 4.6. `MergeWindow`

- **Прызначэнне**: аб’яднанне малых сегментаў у кавалкі да 8–10 хвілін.
- **Залежнасці**: няма.
- **Параметры**: `min_pause`, `min_segment_duration`, `max_segment_duration`.

```python
from belvoice.asr.merge.MergeWindow import MergeWindow
from belvoice.asr.SplitData import VoiceFile

data = VoiceFile.load_from_json("test.json", audio_files_base=".")
MergeWindow().merge(data)
print(data.to_string())
```

### 4.7. `MergeGraph`

- **Прызначэнне**: аб’яднанне сегментаў праз пошук найкарацейшага шляху ў графе.
- **Залежнасці**: `networkx==3.6.1`.
- **Параметр**: `max_segment_duration` (па змоўчванні 10 хвілін).

```python
from belvoice.asr.merge.MergeGraph import MergeGraph
from belvoice.asr.SplitData import VoiceFile

data = VoiceFile.load_from_json("test.json", audio_files_base=".")
MergeGraph(max_segment_duration=10 * 60).merge(data)
print(data.to_string())
```

---

## 5. Дапаможны клас `VoiceFile`

Размешчаны ў `belvoice.asr.SplitData`.

- `VoiceFile(audio_file_path, audio_files_base)` — стварэнне.
- `VoiceFile.load_from_json(json_path, audio_files_base)` — загрузка сегментаў з JSON.
- `data.save_to_json(path)` — захаванне.
- `data.to_string()` — вывад у JSON.
- `data.dump_stat()` — статыстыка па сегментах.
- `VoiceFile.extract_wav(audio_file, start, end, convert_to_format="wav")` — выразанне кавалка праз ffmpeg.
- `data.segment2wav(segment)` — стварэнне тэмпавага wav для сегмента.

Прыклад структуры JSON:

```json
{
    "audio_file_path": "test.wav",
    "segments": [
        {
            "start": 0.21,
            "end": 2.59,
            "speaker_id": "SPEAKER_00",
            "plain_text": null,
            "optimized_text": null
        }
    ]
}
```

---

## 6. Гатовыя паслядоўнасці

### 6.1. TTS: тэкст → аўдыё

```python
from belvoice.synth.normalization.NormalizationSimple import NormalizationSimple
from belvoice.synth.stress.StressStat import StressStat
from belvoice.synth.phonemization.PhonemizationBelG2P import PhonemizationBelG2P
from belvoice.synth.tts.TTSCoquiTTS import TTSCoquiTTS

text = "Ён адказаў ABC-123"

text = NormalizationSimple().normalize(text)
text = StressStat().apply_stresses(text)
phonemes = PhonemizationBelG2P().convert(text)

TTSCoquiTTS().tts(phonemes, "output.wav")
```

### 6.2. ASR: аўдыё → тэкст

```python
from belvoice.asr.split.SplitSileroVAD import SplitSileroVAD
from belvoice.asr.stt.STTNvidia import STTNvidia

data = SplitSileroVAD().split("test.wav")
asr = STTNvidia("nvidia/stt_be_fastconformer_hybrid_large_pc")
asr.transcript_parts(data)
print(data.to_string())
```

### 6.3. ASR для доўгіх файлаў (split → merge → STT)

```python
from belvoice.asr.split.SplitSileroVAD import SplitSileroVAD
from belvoice.asr.merge.MergeWindow import MergeWindow
from belvoice.asr.stt.STTGemini import STTGemini
import os

os.environ["GEMINI_API_KEY"] = "your_key"

data = SplitSileroVAD().split("long.wav")
MergeWindow().merge(data)

asr = STTGemini("gemini/gemini-3-flash-preview")
asr.transcript_parts(data)

data.save_to_json("result.json")
```

---

## 7. Пераменныя асяроддзя

| Пераменная | Прызначэнне | Модулі |
|---|---|---|
| `GEMINI_API_KEY` | Ключ для Gemini | `NormalizationLLM`, `StressLLM`, `STTGemini` |
| `TORCH_DEVICE` | `cpu`, `cuda`, `mps` | `SplitSileroVAD`, `SplitPyannote`, `STTNvidia` |

Прыклад:

```bash
export TORCH_DEVICE=cpu
export GEMINI_API_KEY="your_key"
python your_script.py
```

---

## 8. Асаблівасці Mac M5 (Apple Silicon)

1. **Python 3.14** у вас усталяваны праз Homebrew. Базавыя модулі (`NormalizationSimple`, `StressStat`, `Merge*`) працуюць. Для DL-мадэляў варта стварыць `conda` асяроддзе з Python 3.12:
   ```bash
   brew install miniforge
   conda create --name belvoice python=3.12
   conda activate belvoice
   pip install -e .
   ```

2. **`mps`**: спрабуйце `export TORCH_DEVICE=mps`, калі мадэль падтрымлівае Apple Silicon. Калі ўзнікаюць памылкі — вярніце `cpu`.

3. **Java**: `PhonemizationBelG2P` запускае JVM праз `jpype1`. Усталюйце `openjdk`.

4. **ffmpeg**: усе ASR-модулі чытаюць аўдыё праз ffmpeg. Усталёўка: `brew install ffmpeg`.

5. **Найлепшы аўдыёфармат для ASR**: WAV, PCM, 16000 Hz, 16-bit, mono.

---

## 9. Частыя праблемы

- **`TypeError: 'module' object is not callable`** — у прыкладах часам ідзе імпарт пакета замест класа. Выкарыстоўвайце поўны імпарт: `from belvoice.synth.stress.StressStat import StressStat`.
- **`No module named 'TTS'`** — для `TTSCoquiTTS` трэба `pip install TTS==0.22.0` (лепш на Python 3.11).
- **`jpype.JVMNotFoundException`** — не ўсталявана Java: `brew install openjdk`.
- **Памылкі ладу PyTorch на Python 3.14** — перайдзіце на Python 3.12.
- **Памылкі з `mps`** — `export TORCH_DEVICE=cpu`.
- **`GEMINI_API_KEY`** не ўстаноўлены — `STTGemini`, `NormalizationLLM`, `StressLLM` не запусцяцца без яго.

---

## 10. Mistral, OpenRouter і LMStudio

### 10.1. TTS праз Mistral (`TTSMistral`)

Патрабуецца `MISTRAL_API_KEY`.

```python
from belvoice.synth.tts.TTSMistral import TTSMistral

tts = TTSMistral()
tts.tts("Hello world!", "out-mistral.mp3")
```

- Мадэль: `voxtral-mini-tts-2603` (перадвызначаная).
- Голас выбіраецца аўтаматычна са спісу preset галасоў, калі не пазначаны `voice_id`.
- Доўгі тэкст разбіваецца на часткі і складаецца ў адзін файл праз ffmpeg.

### 10.2. TTS праз OpenRouter (`TTSOpenRouter`)

Патрабуецца `OPENROUTER_API_KEY`. Выкарыстоўвае мадэль `google/gemini-3.1-flash-tts-preview`.

```python
from belvoice.synth.tts.TTSOpenRouter import TTSOpenRouter

tts = TTSOpenRouter()
tts.tts("Прывітанне, свет!", "out-openrouter.wav")
```

- API вяртае raw PCM (24 kHz, 16-bit, mono), які канвертуецца ў патрэбны фармат праз ffmpeg.

### 10.3. LLM-модулі праз Mistral/OpenRouter/LMStudio

`NormalizationLLM` і `StressLLM` цяпер прымаюць `api_key` і `api_base`:

```python
from belvoice.synth.normalization.NormalizationLLM import NormalizationLLM
from belvoice.synth.stress.StressLLM import StressLLM

# Mistral
normalizer = NormalizationLLM("mistral/mistral-small-latest")
stress = StressLLM("mistral/mistral-small-latest")

# OpenRouter
normalizer = NormalizationLLM("openrouter/mistralai/mistral-small-3.1-24b-instruct")

# LMStudio родны endpoint /api/v1/chat
normalizer = NormalizationLLM(
    "qwen/qwen3.6-35b-a3b",
    api_base="http://localhost:1234/api/v1",
)

# LMStudio OpenAI-сумяшчальны endpoint /v1/chat/completions
normalizer = NormalizationLLM(
    "openai/loaded-model",
    api_base="http://localhost:1234/v1",
    api_key="lm-studio",
)
```

### 10.4. ASR праз LMStudio (`STTOpenAI`)

Калі ў LMStudio загружаная мадэль Whisper і ўключаны сервер:

```python
from belvoice.asr.stt.STTOpenAI import STTOpenAI

asr = STTOpenAI()  # http://localhost:1234/v1
print(asr.transcribe("test.wav", language="be"))
```

### 10.5. Патрэбныя пераменныя асяроддзя

| Пераменная | Прызначэнне | Выкарыстоўваецца ў |
|---|---|---|
| `MISTRAL_API_KEY` | Ключ Mistral | `TTSMistral`, `NormalizationLLM`, `StressLLM` |
| `OPENROUTER_API_KEY` | Ключ OpenRouter | `TTSOpenRouter`, `NormalizationLLM`, `StressLLM` |
| `OPENAI_API_BASE` | Базавы URL для `STTOpenAI` | `STTOpenAI` |
| `OPENAI_API_KEY` | Ключ для OpenAI-сумяшчальнага endpoint | `STTOpenAI` |
| `LMSTUDIO_BASE_URL` | Базавы URL для роднага LMStudio endpoint | `NormalizationLLM`, `StressLLM` |

---

## 11. Тэставы Web UI

Каталог `webui/` утрымлівае аднастронкавае Flask-прыкладанне для тэставання ўсіх рэжымаў.

### Запуск

```bash
pip install -e ".[webui]"   # альбо pip install flask
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export PYTHONPATH=framework
python webui/app.py
```

Адкрыйце `http://localhost:5000` у браузеры.

### Магчымасці
- Наладка токенаў і мадэляў для Mistral, OpenRouter, LMStudio, Gemini і OpenAI-сумяшчальнага ASR.
- Рэжымы: **TTS-пайплайн**, **ASR**, **Нармалізацыя**, **Націскі**, **Фанемізацыя**.
- TTS-пайплайн дазваляе паслядоўна выбраць правайдэра для нармалізацыі, націскаў, фанемізацыі і сінтэзу.
- Падтрымка воблачных мадэляў (Mistral Voxtral, OpenRouter/Gemini TTS) і лакальных (LMStudio, CoquiTTS).
- Выніковыя аўдыяфайлы захоўваюцца ў `webui/static/outputs/` і прайграюцца ў браузеры.

> Нататка: канфігурацыя (токены, base URL, мадэлі) захоўваецца ў `webui/ui_config.json` на дыску, таму не дабаўляйце яго ў git.
