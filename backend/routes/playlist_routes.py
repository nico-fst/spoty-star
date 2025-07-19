from flask import Flask, session, jsonify
from flask import Blueprint
import requests
from utils import token_required
from app_types import Playlist
from typing import Dict, TypedDict, List

playlist_bp = Blueprint('playlist', __name__)

@playlist_bp.route('/api/currently_playing')
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

@playlist_bp.route('/api/get_playlists')
@token_required
def get_playlists() -> List[Playlist]:
    '''returns user's first 100 playlists or [] if none or error'''
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    
    existing_playlists = []
    offset = 0
    limit = 50
    
    while True:
        resp_pl = requests.get(f"https://api.spotify.com/v1/me/playlists?offset={offset}&limit={limit}", headers=headers)
        if not resp_pl.ok:
            return f"Fehler beim Abrufen der Playlists --- {resp_pl.json()}"
        playlists = resp_pl.json()['items']
        
        existing_playlists += playlists
        if resp_pl.json()['next'] is None:
            break
        offset += 50
    
    return existing_playlists[0:100]

@playlist_bp.route('/api/get_playlist/<playlist_name>')
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

@playlist_bp.route('/api/add_tracks_to_playlist/<playlist_name>/<track_uris>')
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

@playlist_bp.route('/api/split_playlist_into_decades/<playlist_name>')
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

@playlist_bp.route('/api/sort_playlist_into_decades/<playlist_name>')
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
