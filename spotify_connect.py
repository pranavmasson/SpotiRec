from dotenv import load_dotenv
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, redirect, session, url_for
import os


load_dotenv()

app = Flask(__name__)
app.secret_key = 'some_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'spotify-auth-session'


cid = os.getenv('cid')
secret = os.getenv('secret')
redirect_uri = 'http://localhost:3000/spotirec'
scope = "playlist-modify-public"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    auth_url = 'https://accounts.spotify.com/authorize'
    response_type = 'code'
    state = ''
    show_dialog = 'true'

    url = f'{auth_url}?response_type={response_type}&client_id={cid}&scope={scope}&redirect_uri={redirect_uri}&state={state}&show_dialog={show_dialog}'
    return redirect(url)


@app.route('/spotirec')
def spotirec():
    code = request.args.get('code')
    if code:
        token_info = util.prompt_for_user_token(
            'USERNAME_TO_AUTHORIZE',
            scope,
            client_id=cid,
            client_secret=secret,
            redirect_uri=redirect_uri
        )
        spotify = spotipy.Spotify(auth=token_info['access_token'])
        session['token_info'] = token_info
        return render_template('success.html')
    else:
        return 'Failed to get authentication code'
    
if __name__ == '__main__':
    app.run(port=3000) 