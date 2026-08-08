from belvoice.synth.normalization.NormalizationLLM import NormalizationLLM
from belvoice.synth.stress.StressLLM import StressLLM

# Прыклад праз Mistral
# normalizer = NormalizationLLM("mistral/mistral-small-latest")
# print(normalizer.normalize("Сёння +25°C."))

# stress = StressLLM("mistral/mistral-small-latest")
# print(stress.apply_stresses("Я бачу Ілью"))

# Прыклад праз OpenRouter
# normalizer = NormalizationLLM("openrouter/mistralai/mistral-small-3.1-24b-instruct")
# stress = StressLLM("openrouter/mistralai/mistral-small-3.1-24b-instruct")

# Прыклад праз родны LMStudio endpoint /api/v1/chat
# Запушчаны LMStudio мусіць мець загружаную мадэль.
normalizer = NormalizationLLM(
    "qwen/qwen3.6-35b-a3b",
    api_base="http://localhost:1234/api/v1",
)
print(normalizer.normalize("Сёння +25°C."))

stress = StressLLM(
    "qwen/qwen3.6-35b-a3b",
    api_base="http://localhost:1234/api/v1",
)
print(stress.apply_stresses("Я бачу Ілью"))

# Альтэрнатыва праз OpenAI-сумяшчальны LMStudio endpoint /v1/chat/completions
# normalizer = NormalizationLLM("openai/loaded-model", api_base="http://localhost:1234/v1")
# stress = StressLLM("openai/loaded-model", api_base="http://localhost:1234/v1")
