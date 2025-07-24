from flask import Flask, session, jsonify
from flask import Blueprint
import requests
from typing import Dict, TypedDict, List

from ..app_types import Playlist
from ..utils_requests import spotify_get, spotify_post
from ..utils import date_to_decade
from .playlist_get_routes import get_playlist
from ..utils import token_required
from ..utils_playlists import subtract_uris_existing_in_playlist

playlist_sort_bp = Blueprint("playlist_sort_bp", __name__)


@playlist_sort_bp.route("/api/add_tracks_to_playlist/<playlist_name>/<track_uris>")
@token_required
def add_tracks_to_playlist(playlist_name: str, track_uris) -> List[str]:
    tracks_href = get_playlist(playlist_name)["tracks"][
        "href"
    ]  # -> link to tracks in playlist_name

    # only add new tracks
    new_track_uris = subtract_uris_existing_in_playlist(playlist_name, track_uris)
    if len(new_track_uris) == 0:
        return f"Did not find any new tracks to add to {playlist_name}."

    resp_added = spotify_post(
        tracks_href,
        json=new_track_uris,  # expected as list von API even if only one
    )

    return resp_added


@playlist_sort_bp.route("/api/split_playlist_into_decades/<playlist_name>")
@token_required
def split_playlist_into_decades(playlist_name: str) -> Dict[str, List[str]]:
    tracks_href = get_playlist(playlist_name)["tracks"]["href"]

    resp_tracks = spotify_get(tracks_href)
    tracks = resp_tracks.json()["items"]

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
        if track["year"] not in tracks_by_decades:
            tracks_by_decades[track["year"]] = []
        tracks_by_decades[track["year"]].append(track)

    return tracks_by_decades


def sort_playlist_in_playlists(
    decade: str, playlist: str, tracks_by_decade: Dict[str, List[str]]
):
    if decade in tracks_by_decade:
        track_uris_of_this_decade = [track["uri"] for track in tracks_by_decade[decade]]
        add_tracks_to_playlist(playlist, track_uris_of_this_decade)
        add_tracks_to_playlist(playlist[:-3], track_uris_of_this_decade)


@playlist_sort_bp.route("/api/sort_playlist_into_decades/<playlist_name>")
@token_required
def sort_playlist_into_decades(playlist_name: str):
    """sortiert die Playlist in einzelne Decaden-Playlists"""
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

    for decade, decade_playlist in decades.items():
        sort_playlist_in_playlists(decade, decade_playlist, tracks_by_decade)

    return jsonify({"message": f"Playlist {playlist_name} successfully sorted!"}), 201
