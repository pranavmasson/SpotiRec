from flask import Flask, request, redirect, session, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import spotipy.util as util

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'some_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'spotify-auth-session'

cid = os.getenv('cid')
secret = os.getenv('secret')
redirect_uri = "http://localhost:3000/spotirec"
scope = "user-read-recently-played"

sp_oauth = SpotifyOAuth(client_id=cid, client_secret=secret, redirect_uri=redirect_uri, scope=scope)

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    # Check if token has expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return token_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    session['token_info'] = token_info
    return redirect(url_for('spotirec'))

@app.route('/spotirec')
def spotirec():
    token_info = get_token()
    if not token_info:
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_recently_played()
    user_name = sp.current_user()['display_name']
    
    # Extracting tracks and removing duplicates based on track ID
    seen_ids = set()
    unique_tracks = []
    for item in results['items']:
        track = item['track']
        if track['id'] not in seen_ids:
            seen_ids.add(track['id'])
            unique_tracks.append(item)

    return render_template('dashboard.html', user_name=user_name, tracks=unique_tracks)

@app.route('/recommend', methods=['POST'])
def recommend():
    track_id = request.form['track_id']
    # Placeholder for future functionality to fetch recommendations based on track_id
    return render_template('recommendations.html', track_id=track_id)

@app.route('/recommendations')
def recommendations():
    # This will display recommended songs (future functionality)
    return 'Here will be the recommendations based on the track.'


if __name__ == '__main__':
    app.run(port=3000)