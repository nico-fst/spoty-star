from flask import Blueprint, session, jsonify
from typing import Dict, TypedDict, List
import requests
from concurrent.futures import ThreadPoolExecutor

from ..app_types import Playlist
from ..utils import token_required
from ..utils_requests import spotify_get, spotify_post
from ..thread_context import set_access_token, get_access_token
from ..app_constants import MAX_THREADS

playlist_get_bp = Blueprint('playlist_get_bp', __name__)


def thread_spotify_get_tracks(
    tracks_href: str, offset: int, limit: int, access_token: str
) -> List[dict]:
    set_access_token(access_token)
    return spotify_get(f"{tracks_href}?offset={offset}&limit={limit}").json()["items"]


@playlist_get_bp.route("/api/currently_playing")
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

def thread_get_playlists(limit: int, offset: int, access_token: str) -> List[Playlist]:
    set_access_token(access_token)
    return spotify_get(f"https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}")


@playlist_get_bp.route("/api/get_playlists")
@token_required
def get_playlists() -> List[Playlist]:
    '''returns user's first 100 playlists or [] if none or error'''

    # calculating how many playlists there are => how many threads needed
    resp_pl = spotify_get("https://api.spotify.com/v1/me/playlists?limit=1")
    total_playlists = resp_pl.json()['total']
    offsets = list(range(0, total_playlists, 50))  # Spotify API allows max 50 per request

    access_token = get_access_token()  # in thread
    if not access_token:  # not in thread
        access_token = session.get('access_token')

    with ThreadPoolExecutor(max_workers=40) as executor:
        playlists_list_list = list(
            executor.map(
                lambda offset: thread_get_playlists(50, offset, access_token).json()['items'],
                offsets
            )
        )

    playlists = [playlist for result in playlists_list_list for playlist in result]  # weil List[List[playlists]]
    return playlists


@playlist_get_bp.route("/api/get_playlist/<playlist_name>")
@token_required
def get_playlist(playlist_name: str) -> Playlist:
    try:
        playlists = get_playlists()
    except Exception as e:
        raise Exception(f"Error fetching playlists: {str(e)}")
    
    playlist_in_dict = [pl for pl in playlists if pl['name'].lower() == playlist_name.lower()]
    if len(playlist_in_dict) == 0:
        raise Exception(f"Playlist {playlist_name} nicht gefunden")
    
    return playlist_in_dict[0]
