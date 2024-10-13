from flask import Flask, redirect, request, session, url_for
import requests
import base64
import json
from dotenv import load_dotenv
import os
from functools import wraps
from pprint import pprint
from typing import List, Dict, Union, Optional, TypedDict

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URL = 'http://localhost:5001/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'user-read-playback-state user-read-currently-playing playlist-modify-public playlist-modify-private'

class Playlist(TypedDict):
    description: str
    href: str
    id: str
    name: str
    tracks: Dict[str, int] # href, total
    uri: str

def token_required(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        token = session['access_token']
        if not token:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_f

@app.route('/')
def index():
    return 'Hello, melde dich an unter <a href="/login">Login</a>'

@app.route('/login')
def login():
    # login optional, debug: dass jedes Mal Anmeldung abgefragt
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URL}&prompt=login"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # args werden von Spotify an die URL /callback angehangen
    code = request.args.get('code')
    
    if not code:
        return 'Fehler beim Login: Kein Authorizaton Code erhalten'
    
    # Exchange Authorization Code -> Access token
    token_resp = requests.post(TOKEN_URL, data={
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': REDIRECT_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    
    # Response with Token
    token_info = token_resp.json()
    session['access_token'] = token_info['access_token']
    
    return redirect(url_for('currently_playing'))

@app.route('/currently_playing')
@token_required
def currently_playing():
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    
    # -> resp.json()['item'] liefert album, artists, duration, ...
    resp = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    
    if resp.status_code == 200 and resp.json():
        track_data = resp.json()
        
        track_name = track_data['item']['name']
        track_artist_name = track_data['item']['artists'][0]['name']
        track_year = track_data['item']['album']['release_date'].split('-')[0]
        
        return f'Aktuell läuft: {track_name} von {track_artist_name}, veröffentlicht im Jahr {track_year}'
    else:
        return 'Kein Song läuft gerade'

@app.route('/get_playlists')
@token_required
def get_playlists() -> List[Playlist]:
    headers = {'Authorization': f'Bearer {session["access_token"]}'}

    resp = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)

    if resp.status_code != 200:
        return "Fehler beim Abrufen der Playlists"
    
    resp_playlists = resp.json()['items']
    return [playlist for playlist in resp_playlists]

@app.route('/get_playlist/<playlist_name>')
@token_required
def get_playlist(playlist_name: str) -> Playlist:
    playlists = get_playlists()
    playlist_in_dict = [pl for pl in playlists if pl['name'].lower() == playlist_name.lower()]
    
    if len(playlist_in_dict) == 0:
        return f"Playlist {playlist_name} beim Nutzer nicht gefunden"
    
    return playlist_in_dict[0]

@app.route('/add_tracks_to_playlist/<playlist_name>/<track_uris>')
@token_required
def add_tracks_to_playlist(playlist_name: str, track_uris: List[str]):
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    
    tracks_href = get_playlist(playlist_name)['tracks']['href']
    
    resp_added = requests.post(
        tracks_href,
        json=track_uris, # expected as list von API even if only one
        headers=headers
    )
    
    if resp_added.status_code == 201:
        return f"Track {track_uris} erfolgreich zur Playlist {playlist_name} hinzugefügt"
    else:
        return f"Fehler beim Hinzufügen des Tracks {track_uris} zur Playlist {playlist_name} --- {resp_added.json()}"

@app.route('/test')
@token_required
def test():
    return add_tracks_to_playlist(
        "debug",
        [
            "spotify:track:7lEptt4wbM0yJTvSG5EBof",
            "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        ],
    )


if __name__ == '__main__':
    app.run(host="localhost", port=5001, debug=True)
