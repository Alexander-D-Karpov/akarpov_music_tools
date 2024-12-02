from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class SpotifyResponse(BaseModel):
    name: str = ""
    link: str = ""
    meta: Dict[str, Any] = {}
    image_url: str = ""
    external_urls: Dict[str, str] = {}
    full_data: Dict[str, Any] = {}

class SpotifyTrackResponse(SpotifyResponse):
    album_name: str = ""
    album_image: str = ""
    album_meta: Dict[str, Any] = {}
    release: str = ""
    artists: List[str] = []
    artist: str = ""
    title: str = ""
    genre: List[str] = []

class SpotifyArtistResponse(SpotifyResponse):
    genres: List[str] = []
    popularity: int = 0
    images: List[Dict[str, Any]] = []

class SpotifyAlbumResponse(SpotifyResponse):
    release_date: str = ""
    total_tracks: int = 0
    images: List[Dict[str, Any]] = []
    artists: List[Dict[str, Any]] = []
    genres: List[str] = []
    tracks: List[Dict[str, Any]] = []

class SpotifyError(BaseModel):
    status: int
    message: str