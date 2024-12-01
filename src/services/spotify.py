from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from src.api.models.spotify import SpotifySearchResponse


class SpotifyService:
    def __init__(self, client_id: str, client_secret: str):
        self.spotify = Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )

    async def search(self, query: str) -> SpotifySearchResponse:
        results = self.spotify.search(query, type="track")
        tracks = results.get("tracks", {}).get("items", [])

        if not tracks:
            return SpotifySearchResponse()

        track = tracks[0]
        artist_data = self.spotify.artist(
            track["artists"][0]["external_urls"]["spotify"]
        )

        return SpotifySearchResponse(
            album_name=track["album"]["name"],
            release=track["album"]["release_date"].split("-")[0],
            album_image=track["album"]["images"][0]["url"] if track["album"]["images"] else "",
            artists=[artist["name"] for artist in track["artists"]],
            artist=track["artists"][0]["name"],
            title=track["name"],
            genre=artist_data.get("genres", [])
        )