from deep_translator import GoogleTranslator

class TranslationService:
    async def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "en"
    ) -> str:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)