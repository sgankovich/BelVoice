from belvoice.synth.normalization.NormalizationLLM import NormalizationLLM
from belvoice.synth.stress.StressLLM import StressLLM

# Прыклад праз Mistral
normalizer = NormalizationLLM("mistral/mistral-small-latest")
print(normalizer.normalize("Сёння +25°C."))

stress = StressLLM("mistral/mistral-small-latest")
print(stress.apply_stresses("Я бачу Ілью"))

# Прыклад праз OpenRouter
# normalizer = NormalizationLLM("openrouter/mistralai/mistral-small-3.1-24b-instruct")
# stress = StressLLM("openrouter/mistralai/mistral-small-3.1-24b-instruct")

# Прыклад праз LMStudio (лакальна)
# normalizer = NormalizationLLM("openai/loaded-model", api_base="http://localhost:1234/v1", api_key="lm-studio")
# stress = StressLLM("openai/loaded-model", api_base="http://localhost:1234/v1", api_key="lm-studio")
