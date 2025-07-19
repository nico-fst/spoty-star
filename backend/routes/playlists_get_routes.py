from flask import Blueprint
from typing import Dict, TypedDict, List

from ..app_types import Playlist
from ..utils import token_required
from ..utils_requests import spotify_get, spotify_post

playlists_get_bp = Blueprint('playlists_get_bp', __name__)


@playlists_get_bp.route('/api/currently_playing')
@token_required
def currently_playing():
    resp_playing = spotify_get("https://api.spotify.com/v1/me/player/currently-playing")
    
    if resp_playing:
        tracks = resp_playing.json()
        
        # -> resp.json()['item'] liefert album, artists, duration, ...
        track_name = tracks['item']['name']
        track_artist_name = tracks['item']['artists'][0]['name']
        track_year = tracks['item']['album']['release_date'].split('-')[0]
        
        return f'Aktuell läuft: {track_name} von {track_artist_name}, veröffentlicht im Jahr {track_year}'
    else:
        # TODO was kommt, wenn keiner läuft?
        return 'Kein Song läuft gerade'

@playlists_get_bp.route('/api/get_playlists')
@token_required
def get_playlists() -> List[Playlist]:
    '''returns user's first 100 playlists or [] if none or error'''
    
    existing_playlists = []
    offset = 0
    limit = 50
    
    while True:
        resp_pl = spotify_get(f"https://api.spotify.com/v1/me/playlists?offset={offset}&limit={limit}")
        playlists = resp_pl.json()['items']
        
        existing_playlists += playlists
        if resp_pl.json()['next'] is None:
            break
        offset += 50
    
    return existing_playlists[0:100]

@playlists_get_bp.route('/api/get_playlist/<playlist_name>')
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
