from belvoice.llm_client import LiteLLMClient


class NormalizationLLM:
    """
    Разумная нармалізацыя тэксту праз LLM.

    Падтрымлівае мадэлі з LiteLLM, у тым ліку `mistral/...`, `openrouter/...`,
    і лакальныя OpenAI-сумяшчальныя правайдэры (LMStudio) праз `api_base`.
    """

    """
    Prompt, based on the from https://arxiv.org/abs/2511.03080v1
    """
    PROMPT = """
    You are an accurate text normalizer for Belarusian language. Your task is to normalize unstandardized text from the following categories to truly reflects how the real speech is, based on the context:
    - Cardinal
    - Date
    - Decimal
    - Ordinal
    - Fraction
    - Time
    - Currency
    - Unit (Measure)
    - Electronic Address (URL or Email)
    - Initialism or Acronym
    - ISBN
    - Roman Numeral
    - Telephone
    - Sports Score
    - Mathematical Expression
    - Symbol
    - Abbreviation
    - Chemical Formula
    - Legal Reference
    - Vehicle or Product Code
    - Geographic Coordinates
    - Version Number
    - License Plate or Serial Number
    - Musical Notation
    - Stock Ticker
    - Biological Classification
    - Address
    - Other unnormalized text
    
    Some important rules:
    - When normalizing acronyms, spell out to their full forms for clarity, except when the acronym is a widely recognized and pronounceable name (e.g. “NASA” or “NASCAR”). In those cases, keep the acronym as-is and pronounce it as a word.
    - If the acronym combines a letter and a word, split accordingly.
    - Convert punctuation that is spoken aloud into words. For example, write ‘dot’ instead of a period in URLs and emails.
    - To ensure clarity, segment compound words, websites and file names into recognizable component words rather than keeping them as a whole word.
    - Symbols in a file name should be read as is.
    - Common file extensions (.jpeg, .jpg, .txt, etc) should be spoken out. Uncommon file extensions should be spelled out.
    
    DO NOT include any extra commentary, greetings, or explanations in your output. Only return the revised text.
    """

    def __init__(self, model_name: str, api_key: str = None, api_base: str = None):
        self._client = LiteLLMClient(model_name, api_key=api_key, api_base=api_base)

    def normalize(self, text_to_normalize: str) -> str:
        messages = [
            {"role": "system", "content": self.PROMPT},
            {"role": "user", "content": text_to_normalize}
        ]

        response = self._client.chat(messages, temperature=0.0)
        return response.choices[0].message.content
