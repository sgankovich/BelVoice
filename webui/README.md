# BelVoice testing web UI — documentation

## What changed

The web UI was rebuilt to follow the same visual design system and interaction patterns as `sgankovich/podcast-generator`. The core Flask logic in `app.py` stayed unchanged; only the templates, styles, scripts and a small i18n layer were added or replaced.

## Files

| File | Purpose |
|------|---------|
| `webui/app.py` | Flask app, unchanged processing logic, added `ui_text` import, context processor and `/set-ui-language` route. |
| `webui/ui_text.py` | Belarusian/English UI string catalog, used by all templates. |
| `webui/templates/base.html` | New base layout: sidebar, topbar, command palette, language/theme/style/accent toggles. |
| `webui/templates/icons.html` | Jinja macro for inline SVG icons. |
| `webui/templates/index.html` | Main page: mode selector, provider config cards, TTS/ASR/input sections, result card. |
| `webui/static/app.css` | Design-system CSS from `podcast-generator` plus BelVoice-specific additions. |
| `webui/static/app.js` | Dashboard primitives: theme, style, accent, command palette, custom `belvoice:command` events. |
| `webui/README.md` | This file. |

## Design system

The UI is based on the Vellum/primitive-first dashboard system:

- **Theme tokens**: `data-mode` (`dark`/`light`), `data-style` (`modern`/`simple`), `data-accent` (`lime`, `coral`, `purple`, `blue`, `amber`, `pink`, `teal`).
- **Tokens**: CSS variables such as `--v-bg`, `--v-surface`, `--v-text`, `--v-lime`, etc.
- **Typography**: Google Fonts `DM Sans`, `Manrope`, `DM Mono`.
- **Icons**: inline stroke SVGs (Lucide style), no icon fonts.
- **Primitives**: cards, command palette, topbar/sidebar, toggles, accessible focus rings.

## How to run

```bash
cd /home/ubuntu/repos/BelVoice/webui
python3 -m venv belvoice_env
source belvoice_env/bin/activate
pip install flask
python app.py
```

Then open `http://localhost:5000` in your browser.

The app only needs Flask to render the UI. The heavy ML modules (`belvoice.*`) are imported lazily inside the processing functions, so UI-only testing does not require the full project dependency stack.

## User interface

1. **Topbar**
   - Search field opens the command palette (`⌘K` / `Ctrl+K`).
   - Language switcher `BY / EN`.
   - Day/night mode toggle.
   - Modern/simple style toggle.
   - Accent-color selector.

2. **Command palette**
   - Switch to a mode: `M T` (TTS), `M A` (ASR), `M N` (normalization), `M S` (stress), `M P` (phonemization).
   - Toggle theme `T M` and style `T S`.
   - Go home `G H`.

3. **Mode selector**
   - Radio buttons select the processing mode and reveal the relevant form sections.

4. **Provider configuration**
   - API keys, base URLs and model names are grouped into expandable cards for Mistral, OpenRouter, LMStudio, Gemini and OpenAI-compatible Whisper.

5. **Result card**
   - Shows the generated audio player, text output, intermediate pipeline steps and file path.

## How it works

- `app.py` injects `ui`, `ui_language` and `ui_languages` into every template via `@app.context_processor`.
- The language cookie `ui_language` is set by `POST /set-ui-language` from the topbar buttons.
- `app.js` dispatches `belvoice:command` for unknown command-palette actions; `index.html` listens to `focus-*` commands and updates the mode radio buttons and visible sections.
- Original form field names (`mode`, providers, `input_text`, `audio_file`, etc.) were preserved, so the Flask backend logic remains compatible.

## Notes

- No pre-commit hooks are configured for this repository.
- The UI is a single-page testing interface; multi-page wizard behavior was intentionally not added.
