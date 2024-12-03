from typing import Optional
import asyncio
from functools import lru_cache


class TranslationError(Exception):
    """Custom exception for translation-related errors."""
    pass


class TranslationService:
    """A service class for handling text translations using Google Translate.

    This class provides an async interface for translating text between different languages
    using the deep_translator library's GoogleTranslator backend.
    """

    def __init__(self, default_target_lang: str = "en"):
        """Initialize the translation service.

        Args:
            default_target_lang (str): Default target language code (ISO 639-1 format).
                                     Defaults to "en" (English).
        """
        self.default_target_lang = default_target_lang
        self._translator = None
        self._supported_languages = None

    @property
    def translator(self):
        """Lazy initialization of the GoogleTranslator."""
        if self._translator is None:
            try:
                from deep_translator import GoogleTranslator
                self._translator = GoogleTranslator
            except ImportError as e:
                raise TranslationError(
                    "Failed to import GoogleTranslator. Please ensure deep_translator is installed: "
                    "pip install deep_translator"
                ) from e
        return self._translator

    @lru_cache(maxsize=1)
    def get_supported_languages(self) -> set:
        """Get a set of supported language codes.

        Returns:
            set: Set of supported language codes.

        Raises:
            TranslationError: If unable to fetch supported languages.
        """
        try:
            translator_instance = self.translator(source='auto', target='en')
            return set(translator_instance.get_supported_languages())
        except Exception as e:
            raise TranslationError(f"Failed to fetch supported languages: {str(e)}") from e

    def _validate_languages(self, source_lang: str, target_lang: str) -> None:
        """Validate the source and target language codes.

        Args:
            source_lang (str): Source language code.
            target_lang (str): Target language code.

        Raises:
            ValueError: If language codes are invalid.
        """
        if source_lang != "auto":
            supported_langs = self.get_supported_languages()
            if source_lang not in supported_langs:
                raise ValueError(f"Unsupported source language: {source_lang}")

        if target_lang not in self.get_supported_languages():
            raise ValueError(f"Unsupported target language: {target_lang}")

    async def translate(
            self,
            text: str,
            source_lang: str = "auto",
            target_lang: Optional[str] = None
    ) -> str:
        """Translate text from source language to target language.

        Args:
            text (str): Text to translate.
            source_lang (str): Source language code (ISO 639-1 format) or "auto" for
                             automatic detection. Defaults to "auto".
            target_lang (Optional[str]): Target language code (ISO 639-1 format).
                                       If None, uses the default target language.

        Returns:
            str: Translated text.

        Raises:
            TranslationError: If translation fails.
            ValueError: If input parameters are invalid.
        """
        if not text:
            return text

        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        target_lang = target_lang or self.default_target_lang

        # Validate language codes
        self._validate_languages(source_lang, target_lang)

        try:
            # Run the translation in a thread pool to avoid blocking
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
            target_lang: Optional[str] = None,
            chunk_size: int = 5
    ) -> list[str]:
        """Translate multiple texts in parallel.

        Args:
            texts (list[str]): List of texts to translate.
            source_lang (str): Source language code. Defaults to "auto".
            target_lang (Optional[str]): Target language code.
            chunk_size (int): Number of concurrent translations. Defaults to 5.

        Returns:
            list[str]: List of translated texts.
        """
        if not texts:
            return []

        target_lang = target_lang or self.default_target_lang

        # Process translations in chunks to avoid overwhelming the service
        results = []
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            tasks = [
                self.translate(text, source_lang, target_lang)
                for text in chunk
            ]
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions in the results
            for result in chunk_results:
                if isinstance(result, Exception):
                    raise result
                results.append(result)

        return results