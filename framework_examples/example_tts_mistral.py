from belvoice.synth.tts.TTSMistral import TTSMistral

# Патрабуецца MISTRAL_API_KEY у пераменных асяроддзя
# Можна таксама перадаць api_key= і voice_id= у канструктар

tts = TTSMistral()
tts.tts("Hello world!", "out-mistral.mp3")
print("Вынік захаваны ў out-mistral.mp3")
