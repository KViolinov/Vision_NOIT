import os
import threading
import spotipy


class SpotifyClient:
    def __init__(self) -> None:
        self._client: spotipy.Spotify | None = None
        self._lock = threading.Lock()

    def _get_client(self) -> spotipy.Spotify:
        with self._lock:
            if self._client is None:
                client_id = os.getenv("SPOTIFY_CLIENT_ID")
                client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
                if not client_id or not client_secret:
                    raise EnvironmentError("Spotify credentials not configured.")
                self._client = spotipy.Spotify(
                    auth_manager=spotipy.SpotifyOAuth(
                        client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri="http://localhost:8888/callback",
                        scope="user-library-read user-read-playback-state user-modify-playback-state",
                    )
                )
        return self._client

    def current_playback(self):
        return self._get_client().current_playback()
