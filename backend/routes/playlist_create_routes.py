from flask import Blueprint, session, jsonify
from typing import Dict, TypedDict, List
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from ..app_types import Playlist, FavEntry, Track
from ..utils import token_required
from ..utils_requests import spotify_get, spotify_post
from ..thread_context import set_access_token, get_access_token
from .playlist_get_routes import get_playlists
from ..utils_playlists import get_user_id
from .favs_routes import get_favs, favEntries_to_tracks
from ..utils import str_to_datetime, get_end_of_month
from .playlist_add_routes import add_tracks_to_playlist
from ..exceptions import SpotifyAPIError, LoggedOutError, ClientError

playlist_create_bp = Blueprint("playlist_create_bp", __name__)


def create_empty_playlist(title: str) -> Playlist:
    playlists = get_playlists()
    user_id = get_user_id()

    if any(pl["name"] == title for pl in playlists):
        raise ClientError(f"Playlist {title} exists already.")

    resp = spotify_post(
        f"https://api.spotify.com/v1/users/{user_id}/playlists", {"name": title}
    )

    return resp.json(), 201


@playlist_create_bp.route("/api/create_monthlist/<year>/<month>")
@token_required
def create_monthlist(year: str, month: str) -> Playlist:
    selected_date = datetime(int(year), int(month), 1)
    now = datetime.now()
    month = month.zfill(2)

    if selected_date > now:
        raise ClientError(
            f"Cannot create playlist for future dates.", "FutureDateError"
        )

    title = f"[Time] {year}::{month.zfill(2)}"

    empty_playlist, status = create_empty_playlist(title)

    filtered_favs: List[FavEntry] = get_favs(
        f"{year}-{month}-01", f"{year}-{month}-{get_end_of_month(year, month)}"
    )
    filtered_tracks: List[Track] = favEntries_to_tracks(filtered_favs)

    resp_snapshot = add_tracks_to_playlist(empty_playlist, filtered_tracks)
    return "done", 201


@playlist_create_bp.route("/api/does_monthlist_exist/<playlist_name>")
@token_required
def does_monthlist_exist(playlist_name: str) -> bool:
    title = f"[Time] {playlist_name[0:4]}::{playlist_name[5:7]}"
    playlists = get_playlists()

    exists: bool = any(pl["name"] == title for pl in playlists)
    print(f"{title} does exist: {exists}")
    return jsonify(exists)
