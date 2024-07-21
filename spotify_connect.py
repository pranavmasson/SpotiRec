from flask import Flask, request, redirect, session, render_template, url_for
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import spotipy.util as util
from torch import cosine_similarity

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

def recommend_song(track_ids, target_track_id):
    token_info = get_token()
    if not token_info:
        raise Exception("No token available.")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Get features for the target track
    target_features = sp.audio_analysis(target_track_id)
    latest_tracks = get_latest_tracks_by_genre(genre)


    # Initialize an empty list to store features of other tracks
    track_features = []

    # Get features for each track in the list
    for track_id in track_ids:
        features = sp.audio_analysis(track_id)
        track_features.append(features)

    # Calculate cosine similarity
    similarities = cosine_similarity([target_features], track_features)[0]

    # Get the index of the most similar song (excluding the target song itself)
    best_match_index = np.argmax(similarities)

    # Return the most similar track ID
    return track_ids[best_match_index]

""" # Example usage:
track_ids = ['track_id1', 'track_id2', 'track_id3']  # List of track IDs
target_track_id = 'target_track_id'
recommended_track_id = recommend_song(track_ids, target_track_id)
print(f"Recommended Track ID: {recommended_track_id}") """

def get_playlists_by_genre(genre, limit=10):
    token_info = get_token()
    if not token_info:
        raise Exception("No token available.")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Replace spaces with '+' for URL encoding
    genre_query = genre.replace(' ', '+')
    results = sp.search(q='genre:"{}"'.format(genre_query), type='playlist', limit=limit)
    return results['playlists']['items']

def get_tracks_from_playlist(playlist_id, limit=10):
    token_info = get_token()
    if not token_info:
        raise Exception("No token available.")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.playlist_tracks(playlist_id, limit=limit)
    tracks = results['items']
    # Return a list of track IDs
    return [track['track']['id'] for track in tracks if track['track']]

def get_latest_tracks_by_genre(genre, num_playlists=5, tracks_per_playlist=5):
    token_info = get_token()
    if not token_info:
        raise Exception("No token available.")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    playlists = get_playlists_by_genre(genre, limit=num_playlists)
    all_tracks = []
    for playlist in playlists:
        playlist_id = playlist['id']
        tracks = get_tracks_from_playlist(playlist_id, limit=tracks_per_playlist)
        all_tracks.extend(tracks)
    return all_tracks


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
    token_info = get_token()
    if not token_info:
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    track_id = request.form['track_id']
    print(track_id)
    track_info = sp.audio_analysis(track_id)
    print(track_info)
    # Placeholder for future functionality to fetch recommendations based on track_id
    #return render_template('recommendations.html', track_id=track_id)

@app.route('/recommendations')
def recommendations():
    # This will display recommended songs (future functionality)
    return 'Here will be the recommendations based on the track.'


if __name__ == '__main__':
    app.run(port=3000)