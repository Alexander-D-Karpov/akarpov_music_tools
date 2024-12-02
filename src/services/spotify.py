from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)


def clean_spotify_response(data: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(data, dict):
        return {
            k: clean_spotify_response(v)
            for k, v in data.items()
            if k != 'available_markets'
        }
    elif isinstance(data, list):
        return [clean_spotify_response(item) for item in data]
    return data


class SpotifyService:
    def __init__(self, client_id: str, client_secret: str):
        self.spotify = Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )

    def _get_album_tracks(self, album_id: str) -> List[Dict[str, Any]]:
        try:
            tracks = self.spotify.album_tracks(album_id)
            return clean_spotify_response(tracks.get('items', []))
        except Exception as e:
            logger.error("Failed to fetch album tracks", error=str(e))
            return []

    async def search(self, query: str, type: str = "track") -> Dict[str, Any]:
        try:
            results = self.spotify.search(query, type=type, limit=1)
            if type == "track":
                return self._process_track_data(results)
            elif type == "artist":
                return self._process_artist_data(results)
            elif type == "album":
                return self._process_album_data(results)
            raise ValueError(f"Unsupported search type: {type}")
        except Exception as e:
            logger.error("Search failed", error=str(e), query=query, type=type)
            return {}

    def _process_artist_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        artists = results.get("artists", {}).get("items", [])
        if not artists:
            return {}

        artist = clean_spotify_response(artists[0])
        return {
            "name": artist.get("name", ""),
            "link": artist.get("external_urls", {}).get("spotify", ""),
            "meta": {
                "followers": artist.get("followers", {}).get("total", 0),
                "popularity": artist.get("popularity", 0),
                "type": artist.get("type", ""),
            },
            "image_url": next((img["url"] for img in artist.get("images", []) if img.get("url")), ""),
            "genres": artist.get("genres", []),
            "popularity": artist.get("popularity", 0),
            "images": artist.get("images", []),
            "external_urls": artist.get("external_urls", {}),
            "full_data": artist
        }

    def _process_album_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        albums = results.get("albums", {}).get("items", [])
        if not albums:
            return {}

        album = albums[0]
        album_id = album["id"]

        full_album = clean_spotify_response(self.spotify.album(album_id))
        tracks = self._get_album_tracks(album_id)

        return {
            "name": album.get("name", ""),
            "link": album.get("external_urls", {}).get("spotify", ""),
            "meta": {
                "album_type": album.get("album_type", ""),
                "release_date_precision": album.get("release_date_precision", ""),
                "total_tracks": album.get("total_tracks", 0),
                "type": album.get("type", ""),
            },
            "image_url": next((img["url"] for img in album.get("images", []) if img.get("url")), ""),
            "release_date": album.get("release_date", ""),
            "total_tracks": album.get("total_tracks", 0),
            "images": album.get("images", []),
            "external_urls": album.get("external_urls", {}),
            "artists": clean_spotify_response(album.get("artists", [])),
            "genres": full_album.get("genres", []),
            "tracks": tracks,
            "full_data": full_album
        }

    def _process_track_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            return {}

        track = tracks[0]
        artist_id = track["artists"][0]["id"]
        album_id = track["album"]["id"]

        artist_data = clean_spotify_response(self.spotify.artist(artist_id))
        album_data = clean_spotify_response(self.spotify.album(album_id))
        track_data = clean_spotify_response(track)

        return {
            "album_name": track["album"]["name"],
            "album_image": track["album"]["images"][0]["url"] if track["album"]["images"] else "",
            "release": track["album"]["release_date"].split("-")[0],
            "artists": [artist["name"] for artist in track["artists"]],
            "artist": track["artists"][0]["name"],
            "title": track["name"],
            "genre": artist_data.get("genres", []),
            "meta": {
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit"),
                "popularity": track.get("popularity"),
                "preview_url": track.get("preview_url"),
                "track_number": track.get("track_number"),
                "type": track.get("type"),
            },
            "album_meta": album_data,
            "full_data": track_data,
            "external_urls": track.get("external_urls", {})
        }