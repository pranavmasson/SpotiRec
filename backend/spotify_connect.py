import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID='80739f8423c94704885edf2f4db60bfc'
SPOTIPY_CLIENT_SECRET='2b0b53ab4bea406e9f1bb06a58031ea4'
SPOTIPY_REDIRECT_URI='http://127.0.0.1:5000/oauth/callback'

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])