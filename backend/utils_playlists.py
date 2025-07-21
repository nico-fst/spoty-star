from flask import jsonify, session
from typing import List
from concurrent.futures import ThreadPoolExecutor

from .routes.playlists_get_routes import get_playlist
from .utils_requests import spotify_get
from .thread_context import set_access_token, get_access_token

def thread_spotify_get_tracks(tracks_href: str, offset: int, limit: int, access_token: str) -> List[dict]:
    set_access_token(access_token)
    return spotify_get(f"{tracks_href}?offset={offset}&limit={limit}").json()['items']

def subtract_uris_existing_in_playlist(playlist_name: str, track_uris: List[str]) -> bool:    
    try:
        tracks_href = get_playlist(playlist_name)['tracks']['href']
    except Exception as e:
        raise Exception(f"Error fetching playlist {playlist_name}: {str(e)}")
    
    # calculating how many playlists there are => how many threads needed
    resp_pl = spotify_get(f"{tracks_href}?limit=1")
    total_tracks = resp_pl.json()['total']
    print(f"➖ Total tracks in playlist '{playlist_name}': {total_tracks}")
    limit = 50 # since limit of 50 per req
    offsets = list(range(0, total_tracks, limit))

    access_token = get_access_token()  # in thread
    if not access_token:  # not in thread
        access_token = session.get('access_token')
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        all_tracks = list(
            executor.map(
                lambda offset: thread_spotify_get_tracks(tracks_href, offset, limit, access_token),
                offsets
            )
        )
    tracks = [track for batch in all_tracks for track in batch]
    
    existing_track_uris = [track['track']['uri'] for track in tracks]
        
    for track_uri in track_uris:
        if track_uri in existing_track_uris:
            track_uris.remove(track_uri)
        
    return track_uris