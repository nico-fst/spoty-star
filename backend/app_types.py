from typing import Dict, TypedDict, List

# NOTE: not listed attributes might exist in Spotify API but are not (yet) used in the app

class Playlist(TypedDict):
    description: str
    href: str
    id: str
    name: str
    tracks: Dict[str, int]  # z. B. {"href": ..., "total": ...}
    uri: str
    
class Track(TypedDict):
    album: Dict[str, object] # object since various types possible
    href: str
    id: str
    name: str
    uri: str

class FavEntry(TypedDict):
    added_at: str # ISO8601
    track: Track