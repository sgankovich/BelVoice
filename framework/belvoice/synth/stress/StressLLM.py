import importlib.resources
import json
import re

from belvoice.llm_client import make_client


class StressLLM:
    """
    Пазначэнне націскаў праз LLM.

    Падтрымлівае мадэлі з LiteLLM, у тым ліку `mistral/...`, `openrouter/...`,
    і лакальныя OpenAI-сумяшчальныя правайдэры (LMStudio) праз `api_base`.
    """

    PROMPT = """
    Ты - прафесійны беларускі лінгвіст. Адкажы на пытанне - які з двух варыянтаў адпавядае кантэксту. Не пішы падрабязны адказ, напішы толькі літару варыянта: {VARIANTS}.
    {GRAMMAR}

    Прааналізуй граматыку слова "{WORD}", выдзеленае квадратнымі дужкамі ў тэксце:
    """

    def __init__(self, model_name: str, api_key: str = None, api_base: str = None):
        dir = importlib.resources.files(__package__)
        with (dir.joinpath('stresses-nohomographs.json').open('r', encoding='utf-8') as json_file):
            self._stresses_nohomographs = json.load(json_file)
        with (dir.joinpath('stresses-grammar.json').open('r', encoding='utf-8') as json_file):
            self._stresses_grammar = json.load(json_file)
        self._client = make_client(model_name, api_key=api_key, api_base=api_base)

    def apply_stresses(self, text: str) -> str:
        word_pattern = r'([ёйцукенгшўзхфывапролджэячсмітьбю\u02BC\u0301]+)'

        parts = re.split(word_pattern, text, flags=re.IGNORECASE)
        for i, part in enumerate(parts):
            if not re.fullmatch(word_pattern, part, flags=re.IGNORECASE) or "\u0301" in part:
                continue

            part_unstressed = part.replace("\u0301", "")
            part_lower = part_unstressed.lower()

            if part_unstressed in self._stresses_nohomographs:
                parts[i] = self._stresses_nohomographs[part_unstressed]
            elif part_lower in self._stresses_nohomographs:
                parts[i] = self._stresses_nohomographs[part_lower]
            elif part_unstressed in self._stresses_grammar or part_lower in self._stresses_grammar:
                parts[i] = f"[{part}]"
                context_text = "".join(parts)
                resolved = self.request_llm(part_unstressed, context_text)
                if resolved:
                    parts[i] = resolved

        return "".join(parts)

    def request_llm(self, word: str, text: str) -> str | None:
        """
        Запыт да LLM для вызначэння націскаў у слове.
        :param word: слова, у якім трэба вызначыць націск
        :param text: тэкст для апрацоўкі, дзе слова пазначана квадратнымі дужкамі
        :return: слова з націскам (\u0301) альбо None
        """
        grammar = self._stresses_grammar.get(word)
        if not grammar:
            grammar = self._stresses_grammar.get(word.lower())
        if not grammar:
            return None

        variants = '"A", "B" ці "C"' if len(grammar["stressByVariant"]) == 3 else '"A" ці "B"'

        messages = [
            {"role": "system",
             "content": self.PROMPT
             .replace("{GRAMMAR}", grammar["promptText"])
             .replace("{WORD}", word)
             .replace("{VARIANTS}", variants)},
            {"role": "user", "content": text}
        ]

        response = self._client.chat(messages, temperature=0.0)
        result_variant = response.choices[0].message.content.strip()
        return grammar["stressByVariant"].get(result_variant)
