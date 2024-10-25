from flask import session, jsonify
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se o usuário está autenticado na sessão
        if "username" not in session:
            # Retorna uma resposta JSON com status 401 (não autorizado)
            return jsonify({"message": "Faça o login para continuar", "status": "unauthorized"}), 401
        # Caso esteja autenticado, continua para a função
        return f(*args, **kwargs)
    return decorated_function
