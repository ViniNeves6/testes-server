from flask import (
    render_template,
    Blueprint,
    redirect,
    url_for,
    session,
    url_for,
)

from app.webpage_routes import login_required

auth_bp = Blueprint(
    "auth_bp", "__name__", template_folder="templates", static_folder="static"
)


@auth_bp.get("/register")
@login_required
def register_get():
    return render_template("register.html", session=False, title="Registrar")


@auth_bp.get("/login")
def login_get():
    # Se a requisição for GET, exibe a página de login
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("login.html", session=False, title="Login")


@auth_bp.get("/forgot_pass")
def forgot_pass_get():
    return render_template("forgot_pass.html", session=False, title="Esqueci a senha")
