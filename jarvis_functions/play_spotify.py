import os
import spotipy

from dotenv import load_dotenv

from account.check_account import require_login


load_dotenv()

# Seting up spotify
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri='http://localhost:8888/callback',
    scope='user-library-read user-read-playback-state user-modify-playback-state'))  # Scope for currently playing song


ac_dc_playlist_url = "spotify:playlist:1HbAhSztnIcp67DbQBRw9j?si=cd8a3c6e5d8a4e41"

@require_login
def play_song(user_input:str):
    track_name = user_input
    result = sp.search(q=track_name, limit=1)

    # Get the song's URI
    track_uri = result['tracks']['items'][0]['uri']
    # Get the current device
    devices = sp.devices()
    # Find the LAPTOP_KOSI device by its ID
    pc_device_id = '9f209db1259e0ac1839d7db8ace6624ad5f5eaaa'

    # Start playback on the LAPTOP_KOSI device
    sp.start_playback(device_id=pc_device_id, uris=[track_uri])
@require_login
def play_music():
    sp.start_playback()  # Start playback (Play the song)
@require_login
def pause_music():
    sp.pause_playback()  # Pause the playback (Stop the song)