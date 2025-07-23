from flask import Blueprint
from .auth_routes import auth_bp
from .playlist_sort_routes import playlist_sort_bp
from .test_routes import test_bp
from .playlist_get_routes import playlist_get_bp
from .playlist_create_routes import playlist_create_bp
from .favs_routes import favs_bp
from .playlist_add_routes import playlist_add_bp

api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(playlist_sort_bp)
api_bp.register_blueprint(test_bp)
api_bp.register_blueprint(playlist_get_bp)
api_bp.register_blueprint(playlist_create_bp)
api_bp.register_blueprint(favs_bp)
api_bp.register_blueprint(playlist_add_bp)
