from flask import Flask, redirect, request, session, url_for, jsonify, send_from_directory
import requests
import base64
import json
from dotenv import load_dotenv
import os
from functools import wraps
from pprint import pprint
from typing import List, Dict, Union, Optional, TypedDict
from flask_cors import CORS

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, '../spoty-star/dist/assets'),
    template_folder=os.path.join(BASE_DIR, '../spoty-star/dist')
)
app.secret_key = os.getenv('SECRET_KEY') # für Flask-Session
cors = CORS(app, origins="*") #TODO change later

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URL = 'http://localhost:5001/api/callback'
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
        if not 'access_token' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_f

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/api/login')
def login():
    # login optional, debug: dass jedes Mal Anmeldung abgefragt
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URL}&prompt=login"
    return redirect(auth_url)

@app.route('/api/callback')
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

@app.route('/api/currently_playing')
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

@app.route('/api/get_playlists')
@token_required
def get_playlists() -> List[Playlist]:
    '''returns all user's playlist of [] if none or error'''
    headers = {'Authorization': f'Bearer {session["access_token"]}'}

    resp = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)

    if resp.status_code != 200:
        raise Exception("Fehler beim Abrufen der Playlists")
    
    resp_playlists = resp.json()['items']
    return [playlist for playlist in resp_playlists]

@app.route('/api/get_playlist/<playlist_name>')
@token_required
def get_playlist(playlist_name: str) -> Playlist:
    try:
        playlists = get_playlists()
    except Exception as e:
        return str(e)
    
    playlist_in_dict = [pl for pl in playlists if pl['name'].lower() == playlist_name.lower()]
    if len(playlist_in_dict) == 0:
        raise Exception(f"Playlist {playlist_name} nicht gefunden")
    
    return playlist_in_dict[0]

def subtract_uris_existing_in_playlist(playlist_name: str, track_uris: List[str]) -> bool:
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    
    try:
        tracks_href = get_playlist(playlist_name)['tracks']['href']
    except Exception as e:
        return str(e)
    
    existing_track_uris = []
    offset = 0
    limit = 100

    while True:
        resp_tracks = requests.get(f'{tracks_href}?offset={offset}&limit={limit}', headers=headers)
        if not resp_tracks.ok:
            return f"Fehler beim Abrufen der Tracks der Playlist {playlist_name} --- {resp_tracks.json()}"
        tracks = resp_tracks.json()['items']
    
        existing_track_uris += [track['track']['uri'] for track in tracks]
        if len(tracks) < limit:
            break
        offset += 100
        
    for track_uri in track_uris:
        if track_uri in existing_track_uris:
            track_uris.remove(track_uri)
        
    return track_uris

@app.route('/api/add_tracks_to_playlist/<playlist_name>/<track_uris>')
@token_required
def add_tracks_to_playlist(playlist_name: str, track_uris) -> List[str]:
    headers = {'Authorization': f'Bearer {session["access_token"]}'}

    try:
        tracks_href = get_playlist(playlist_name)['tracks']['href']  # -> link to tracks in playlist_name
    except Exception as e:
        return str(e)
    resp_tracks = requests.get(tracks_href, headers=headers)  # -> tracks in playlist_name

    # only add new tracks
    new_track_uris = subtract_uris_existing_in_playlist(playlist_name, track_uris)
    if len(new_track_uris) == 0:
        return f"Keine neuen Tracks zum Hinzufügen in Playlist {playlist_name} gefunden"

    resp_added = requests.post(
        tracks_href,
        json=new_track_uris, # expected as list von API even if only one
        headers=headers
    )

    if resp_added.status_code == 201:
        return f"Track {track_uris} erfolgreich zur Playlist {playlist_name} hinzugefügt"
    else:
        return f"Fehler beim Hinzufügen des Tracks {track_uris} zur Playlist {playlist_name} --- {resp_added.json()}"

def date_to_decade(date: str) -> str:
    '''macht aus YYYY-MM-DD die auf Decade abgerundetes YYYY (e.g. 1974 -> 1970)'''
    year = date.split("-")[0]
    return str(int(year) // 10 * 10)

@app.route('/api/split_playlist_into_decades/<playlist_name>')
@token_required
def split_playlist_into_decades(playlist_name: str) -> Dict[str, List[str]]:
    headers = {"Authorization": f'Bearer {session["access_token"]}'}

    try:
        tracks_href = get_playlist(playlist_name)['tracks']['href']
    except Exception as e:
        return str(e)
    
    resp_tracks = requests.get(tracks_href, headers=headers)
    if not resp_tracks.ok:
        return f"Fehler beim Abrufen der Tracks der Playlist {playlist_name} --- {resp.json()}"
    else:
        tracks = resp_tracks.json()['items']

        tracks_with_decades = [
            {
                "name": track["track"]["name"],
                "year": date_to_decade(track["track"]["album"]["release_date"]),
                "uri": track["track"]["uri"],
            }
            for track in tracks
        ]
        
        tracks_by_decades = {}
        for track in tracks_with_decades:
            if track['year'] not in tracks_by_decades:
                tracks_by_decades[track['year']] = []
            tracks_by_decades[track['year']].append(track)

        return tracks_by_decades

@app.route('/api/sort_playlist_into_decades/<playlist_name>')
@token_required
def sort_playlist_into_decades(playlist_name: str):
    '''sortiert die Playlist in einzelne Decaden-Playlists'''
    headers = {"Authorization": f'Bearer {session["access_token"]}'}

    tracks_by_decade = split_playlist_into_decades(playlist_name)
    decades = {
        "1960": "[Aera] 20th::60s",
        "1970": "[Aera] 20th::70s",
        "1980": "[Aera] 20th::80s",
        "1990": "[Aera] 20th::90s",
        "2000": "[Aera] 21th::00s",
        "2010": "[Aera] 21th::10s",
        "2020": "[Aera] 21th::20s",
    }

    for decade, playlist in decades.items():
        if decade in tracks_by_decade:
            track_uris_of_this_decade = [track['uri'] for track in tracks_by_decade[decade]]
            add_tracks_to_playlist(playlist, track_uris_of_this_decade)
            add_tracks_to_playlist(playlist[:-3], track_uris_of_this_decade)

    print("sieh nach")
    return jsonify({"message": f"Playlist {playlist_name} erfolgreich nach Jahrzehnten sortiert!"})

# @app.route('/sort')
# @token_required
# def sort():
    
@app.route('/api/test')
@token_required
def test():
    # # test adding tracks to playlist
    # return add_tracks_to_playlist(
    #     "[Aera] 21th::20s",
    #     [
    #         # "spotify:track:7lEptt4wbM0yJTvSG5EBof",
    #         "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",  # Speak to Me, 1970, Pink Floyd
    #     ],
    # )

    # # test splitting playlist into decades
    # return split_playlist_into_decades("debug")

    # # test getting playlist with weird symbols
    # return get_playlist("[Aera] 21th::20s")

    # test sorting playlist into decades
    # return split_playlist_into_decades("debug")
    return sort_playlist_into_decades("[Time] 2022::08")

    # return str(
    #     subtract_uris_existing_in_playlist(
    #         "[Aera] 21th::20s", ["spotify:track:6rqhFgbbKwnb9MLmUQDhG6"]
    #     )
    # )


if __name__ == '__main__':
    # python3 app.py
    app.run(host="localhost", port=5001, debug=True)
