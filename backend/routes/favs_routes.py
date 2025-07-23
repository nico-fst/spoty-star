from flask import Blueprint, session, jsonify
from concurrent.futures import ThreadPoolExecutor
import os
from typing import List

from ..app_types import FavEntry, Playlist, Track
from ..utils import token_required
from ..utils_requests import spotify_get
from ..thread_context import set_access_token
from ..utils import str_to_datetime, iso8601_to_datetime
from ..app_constants import MAX_THREADS


favs_bp = Blueprint('favs_bp', __name__)

def favEntries_to_tracks(fav_entries: List[FavEntry]) -> List[Track]:
    return [fav_entry["track"] for fav_entry in fav_entries]

def thread_get_favs_chunk(limit: int, offset: int, access_token: str, datetime_start = None, datetime_end = None):
    set_access_token(access_token)
    resp = spotify_get(f"https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}")
    items = resp.json()['items']
    
    # does not rely on Spotfy result being sorted by date
    if datetime_start or datetime_end:
        filtered = []
        for item in items:
            added_at = iso8601_to_datetime(item['added_at'])
            # returns only if in range or no range specified
            if (not datetime_start or added_at >= datetime_start) and (not datetime_end or added_at <= datetime_end):
                filtered.append(item)
        return filtered
    else:
        return items

def get_favs(date_start: str = None, date_end: str = None) -> List[FavEntry]:
    ''' fetches favs in [date_start, date_end], expects converted to datetime objects '''
    
    limit = 50
    access_token = session.get('access_token') # wei in f nicht bekannt

    tracks_total = spotify_get("https://api.spotify.com/v1/me/tracks?limit=1").json()['total']
    print(f" Total favorite tracks fetchable: {tracks_total}")
    offsets = list(range(0, tracks_total, limit))

    datetime_start = str_to_datetime(date_start) if date_start else None
    datetime_end = str_to_datetime(date_end) if date_end else None

    print(f" Using {MAX_THREADS} threads since {os.cpu_count()} CPUs available.")
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        favs_list_list = list(
            executor.map(
                lambda offset: thread_get_favs_chunk(limit, offset, access_token, datetime_start, datetime_end), # function
                offsets # iterable
            )
        )

    favs = [song for result in favs_list_list for song in result]  # weil List[List[songs]]
    print(f"fetched and filtered to {len(favs)} favorite tracks.")

    return favs

@favs_bp.route('/api/get_favs/')
@token_required
def get_favs_route():
    return jsonify(get_favs())

@favs_bp.route('/api/get_favs/<date_start>/<date_end>')
@token_required
def get_favs_range(date_start: str, date_end: str):
    return jsonify(get_favs(date_start, date_end))
