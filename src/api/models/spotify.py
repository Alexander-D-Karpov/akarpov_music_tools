from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SpotifySearchResponse(BaseModel):
    album_name: str = ""
    album_image: str = ""
    release: str = ""
    artists: List[str] = []
    artist: str = ""
    title: str = ""
    genre: Optional[List[str]] = None
    album_image_path: Optional[str] = None

class SpotifyError(BaseModel):
    detail: str


class SpotifyArtistResponse(BaseModel):
    name: str = ""
    genres: List[str] = []
    popularity: int = 0
    images: List[Dict[str, Any]] = []
    external_urls: Dict[str, str] = {}

class SpotifyAlbumResponse(BaseModel):
    name: str = ""
    release_date: str = ""
    total_tracks: int = 0
    images: List[Dict[str, Any]] = []
    external_urls: Dict[str, str] = {}
    artists: List[Dict[str, Any]] = []
    genres: List[str] = []