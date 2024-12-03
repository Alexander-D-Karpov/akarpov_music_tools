from typing import Optional
import asyncio
from functools import lru_cache


class TranslationError(Exception):
    """Custom exception for translation-related errors."""
    pass


class TranslationService:
    """A service class for handling text translations using Google Translate."""

    def __init__(self):
        self._translator = None

    @property
    def translator(self):
        """Lazy initialization of the GoogleTranslator."""
        if self._translator is None:
            try:
                from deep_translator import GoogleTranslator
                self._translator = GoogleTranslator
            except ImportError as e:
                raise TranslationError(
                    "Failed to import GoogleTranslator. Please ensure deep_translator is installed"
                ) from e
        return self._translator

    async def translate(
            self,
            text: str,
            source_lang: str = "auto",
            target_lang: str = "english"
    ) -> str:
        """Translate text from source language to target language."""
        if not text:
            return text

        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        try:
            loop = asyncio.get_running_loop()
            translator_instance = self.translator(source=source_lang, target=target_lang)

            result = await loop.run_in_executor(
                None,
                translator_instance.translate,
                text
            )

            if not result:
                raise TranslationError("Translation returned empty result")

            return result

        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}") from e

    async def translate_batch(
            self,
            texts: list[str],
            source_lang: str = "auto",
            target_lang: str = "english",
            chunk_size: int = 5
    ) -> list[str]:
        """Translate multiple texts in parallel."""
        if not texts:
            return []

        results = []
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            tasks = [
                self.translate(text, source_lang, target_lang)
                for text in chunk
            ]
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in chunk_results:
                if isinstance(result, Exception):
                    raise result
                results.append(result)

        return results