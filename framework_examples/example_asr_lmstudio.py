from belvoice.asr.stt.STTOpenAI import STTOpenAI

# Патрабуецца LMStudio з загружанай мадэллю Whisper і ўключаным серверам.
# Прадвызначаны endpoint: http://localhost:1234/v1

asr = STTOpenAI()
text = asr.transcribe("test.wav", language="be")
print(f"Тэкст: {text}")
