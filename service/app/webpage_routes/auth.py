from flask import (
    render_template,
    Blueprint,
    redirect,
    url_for,
    session,
    url_for,
)

auth_bp = Blueprint(
    "auth_bp", "__name__", template_folder="templates", static_folder="static"
)


@auth_bp.get("/register")
def register_get():
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("auth/register.html", session=False, title="Registrar")


@auth_bp.get("/login")
def login_get():
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("auth/login.html", session=False, title="Login")


@auth_bp.get("/forgot_pass")
def forgot_pass_get():
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("auth/forgot_pass.html", session=False, title="Esqueci a senha")
