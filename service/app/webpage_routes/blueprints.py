from .dataprocess import dataprocess_bp
from .errors import errors_bp
from .index import index_bp
from .infos import infos_bp
from .auth import auth_bp
from .view import view_bp

# Lista de todos os Blueprints para fácil registro
webpage_bps = (auth_bp, dataprocess_bp, errors_bp, index_bp, infos_bp, view_bp)