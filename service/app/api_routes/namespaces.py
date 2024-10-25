from .auth import auth_ns
from .data import data_ns
from .view import view_ns

# Agrupar todos os namespaces em uma tupla para facilitar o registro
api_namespaces = (auth_ns, data_ns, view_ns)