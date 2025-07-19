from flask import jsonify
from typing import List

from .routes.playlists_get_routes import get_playlist
from .utils_requests import spotify_get

def subtract_uris_existing_in_playlist(playlist_name: str, track_uris: List[str]) -> bool:    
    try:
        tracks_href = get_playlist(playlist_name)['tracks']['href']
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    existing_track_uris = []
    offset = 0
    limit = 100

    while True:
        resp_tracks = spotify_get(f'{tracks_href}?offset={offset}&limit={limit}')
        tracks = resp_tracks.json()['items']
    
        existing_track_uris += [track['track']['uri'] for track in tracks]
        if len(tracks) < limit:
            break
        offset += 100
        
    for track_uri in track_uris:
        if track_uri in existing_track_uris:
            track_uris.remove(track_uri)
        
    return track_uris