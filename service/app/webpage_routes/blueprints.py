from ..api_routes.auth import auth_bp
from .dataprocess import data_bp
from .errors import errors_bp
from .index import index_bp
from .infos import infos_bp
from .pass_handler import pass_bp

# Lista de todos os Blueprints para fácil registro
webpage_bps = (auth_bp, data_bp, errors_bp, index_bp, infos_bp, pass_bp)