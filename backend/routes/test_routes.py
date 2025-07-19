from flask import Blueprint
from utils import token_required
from .playlist_routes import sort_playlist_into_decades

test_bp = Blueprint('test', __name__)

@test_bp.route('/api/test')
@token_required
def test():
    # # test adding tracks to playlist
    # return add_tracks_to_playlist(
    #     "[Aera] 21th::20s",
    #     [
    #         # "spotify:track:7lEptt4wbM0yJTvSG5EBof",
    #         "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",  # Speak to Me, 1970, Pink Floyd
    #     ],
    # )

    # # test splitting playlist into decades
    # return split_playlist_into_decades("debug")

    # # test getting playlist with weird symbols
    # return get_playlist("[Aera] 21th::20s")

    # test sorting playlist into decades
    # return split_playlist_into_decades("debug")
    return sort_playlist_into_decades("[Time] 2022::08")

    # return str(
    #     subtract_uris_existing_in_playlist(
    #         "[Aera] 21th::20s", ["spotify:track:6rqhFgbbKwnb9MLmUQDhG6"]
    #     )
    # )

@test_bp.route('/api/reaching_test')
def reaching_test():
    return "Success!"
    
@test_bp.route('/api/reaching_test_with_token')
@token_required
def reaching_test_with_token():
    return "Success!"
