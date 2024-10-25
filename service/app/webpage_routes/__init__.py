from flask import session, redirect, url_for, flash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Faça o login para continuar!")
            return redirect(url_for("auth_bp.login_get"))
        return f(*args, **kwargs)
    return decorated_function