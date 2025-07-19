from typing import Dict, TypedDict

class Playlist(TypedDict):
    description: str
    href: str
    id: str
    name: str
    tracks: Dict[str, int]  # z. B. {"href": ..., "total": ...}
    uri: str