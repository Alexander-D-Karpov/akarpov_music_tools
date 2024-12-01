from fastapi import APIRouter, HTTPException
from src.api.models.translation import TranslationRequest, TranslationResponse
from src.services.translation import TranslationService
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    try:
        translation_service = TranslationService()
        translated_text = await translation_service.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        return TranslationResponse(translated_text=translated_text)
    except Exception as e:
        logger.error("Translation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))