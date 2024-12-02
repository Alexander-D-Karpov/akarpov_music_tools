from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Union
from src.api.models.spotify import SpotifySearchResponse, SpotifyArtistResponse, SpotifyAlbumResponse
import structlog

logger = structlog.get_logger(__name__)


class SpotifyService:
    def __init__(self, client_id: str, client_secret: str):
        self.spotify = Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )

    async def search(self, query: str, type: str = "track") -> Union[
        SpotifySearchResponse, SpotifyArtistResponse, SpotifyAlbumResponse]:
        try:
            results = self.spotify.search(query, type=type)

            if type == "track":
                return self._process_track_search(results)
            elif type == "artist":
                return self._process_artist_search(results)
            elif type == "album":
                return self._process_album_search(results)
            else:
                raise ValueError(f"Unsupported search type: {type}")
        except Exception as e:
            logger.error("Spotify search failed", error=str(e), query=query, type=type)
            if type == "track":
                return SpotifySearchResponse()
            elif type == "artist":
                return SpotifyArtistResponse()
            else:
                return SpotifyAlbumResponse()

    def _process_track_search(self, results: dict) -> SpotifySearchResponse:
        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            return SpotifySearchResponse()

        track = tracks[0]
        artist_data = None
        try:
            artist_data = self.spotify.artist(
                track["artists"][0]["external_urls"]["spotify"]
            )
        except Exception as e:
            logger.error("Failed to fetch artist data", error=str(e))

        return SpotifySearchResponse(
            album_name=track["album"]["name"],
            release=track["album"]["release_date"].split("-")[0],
            album_image=track["album"]["images"][0]["url"] if track["album"].get("images") else "",
            artists=[artist["name"] for artist in track["artists"]],
            artist=track["artists"][0]["name"],
            title=track["name"],
            genre=artist_data.get("genres", []) if artist_data else []
        )

    def _process_artist_search(self, results: dict) -> SpotifyArtistResponse:
        artists = results.get("artists", {}).get("items", [])
        if not artists:
            return SpotifyArtistResponse()

        artist = artists[0]
        return SpotifyArtistResponse(
            name=artist.get("name", ""),
            genres=artist.get("genres", []),
            popularity=artist.get("popularity", 0),
            images=artist.get("images", []),
            external_urls=artist.get("external_urls", {})
        )

    def _process_album_search(self, results: dict) -> SpotifyAlbumResponse:
        albums = results.get("albums", {}).get("items", [])
        if not albums:
            return SpotifyAlbumResponse()

        album = albums[0]
        # Fetch additional album details if needed
        try:
            album_details = self.spotify.album(album["external_urls"]["spotify"])
            genres = album_details.get("genres", [])
        except Exception:
            genres = []

        return SpotifyAlbumResponse(
            name=album.get("name", ""),
            release_date=album.get("release_date", ""),
            total_tracks=album.get("total_tracks", 0),
            images=album.get("images", []),
            external_urls=album.get("external_urls", {}),
            artists=album.get("artists", []),
            genres=genres
        )