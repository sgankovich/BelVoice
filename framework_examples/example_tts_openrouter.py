from belvoice.synth.tts.TTSOpenRouter import TTSOpenRouter

# Патрабуецца OPENROUTER_API_KEY у пераменных асяроддзя
# Працуе з мадэлямі Gemini TTS праз OpenRouter, напрыклад google/gemini-3.1-flash-tts-preview

tts = TTSOpenRouter()
tts.tts("Прывітанне, свет!", "out-openrouter.wav")
print("Вынік захаваны ў out-openrouter.wav")
