from flask import Flask, request, redirect, session, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'some_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'spotify-auth-session'

cid = os.getenv('cid')
secret = os.getenv('secret')
redirect_uri = "http://localhost:3000/spotirec"
scope = "user-read-recently-played user-read-private"

sp_oauth = SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect_uri, scope=scope)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/spotirec')
def spotirec():
    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code)
        if token_info:
            token = token_info['access_token']
            spotify = spotipy.Spotify(auth=token)
            session['token_info'] = token_info

            tracks = spotify.current_user_recently_played(limit=50, after=None, before=None)
            user_name = spotify.current_user()

            return render_template('dashboard.html', user_name=user_name, tracks=tracks)
        else:
            return 'Failed to get the token'
    else:
        return 'Failed to get authentication code'

if __name__ == '__main__':
    app.run(port=3000)
