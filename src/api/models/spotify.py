from pydantic import BaseModel
from typing import List, Optional

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