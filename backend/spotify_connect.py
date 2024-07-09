import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
cid = 'cd61dc7b3c404b62aae79d5e3c1ef779'
secret = '2cfe66a686d94dbf926656c3da834236'
scope = "playlist-modify-public"
token = util.prompt_for_user_token('USERNAME_TO_AUTHORIZE',scope,client_id=cid,client_secret=secret,redirect_uri='http://localhost:3000/spotirec')
spotify = spotipy.Spotify(auth=token)  