from fastapi import APIRouter, HTTPException, Depends
from src.api.models.spotify import SpotifySearchResponse, SpotifyError
from src.services.spotify import SpotifyService
from src.config import get_settings, Settings
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/search",
             response_model=SpotifySearchResponse,
             responses={500: {"model": SpotifyError}})
async def spotify_search(query: str, settings: Settings = Depends(get_settings)):
    try:
        if not settings.spotify_client_id or not settings.spotify_client_secret:
            raise ValueError("Spotify credentials not configured")

        spotify_service = SpotifyService(
            settings.spotify_client_id,
            settings.spotify_client_secret
        )
        return await spotify_service.search(query)
    except ValueError as ve:
        logger.error("Spotify credentials missing", error=str(ve))
        raise HTTPException(
            status_code=500,
            detail="Spotify service is not properly configured"
        )
    except Exception as e:
        logger.error("Spotify search failed", error=str(e), query=query)
        raise HTTPException(status_code=500, detail=str(e))
