from fastapi import APIRouter, HTTPException, Depends
from src.api.models.spotify import (
    SpotifyTrackResponse,
    SpotifyArtistResponse,
    SpotifyAlbumResponse,
    SpotifyError
)
from src.services.spotify import SpotifyService
from src.config import get_settings, Settings
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_spotify_service(settings: Settings = Depends(get_settings)) -> SpotifyService:
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Spotify credentials not configured"
        )
    return SpotifyService(settings.spotify_client_id, settings.spotify_client_secret)

@router.post("/search",
    response_model=SpotifyTrackResponse,
    responses={500: {"model": SpotifyError}})
async def spotify_search(
    query: str,
    spotify_service: SpotifyService = Depends(get_spotify_service)
):
    try:
        return await spotify_service.search(query)
    except Exception as e:
        logger.error("Spotify search failed", error=str(e), query=query)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/artist",
    response_model=SpotifyArtistResponse,
    responses={500: {"model": SpotifyError}})
async def spotify_artist_info(
    query: str,
    spotify_service: SpotifyService = Depends(get_spotify_service)
):
    try:
        return await spotify_service.search(query, type="artist")
    except Exception as e:
        logger.error("Spotify artist search failed", error=str(e), query=query)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/album",
    response_model=SpotifyAlbumResponse,
    responses={500: {"model": SpotifyError}})
async def spotify_album_info(
    query: str,
    spotify_service: SpotifyService = Depends(get_spotify_service)
):
    try:
        return await spotify_service.search(query, type="album")
    except Exception as e:
        logger.error("Spotify album search failed", error=str(e), query=query)
        raise HTTPException(status_code=500, detail=str(e))