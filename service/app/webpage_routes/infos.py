from flask import render_template, Blueprint, redirect, session, url_for

infos_bp = Blueprint("infos_bp", "__name__", template_folder="templates", static_folder="static")


@infos_bp.route("/equipe")
def equipe():
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("infos/equipe.html", title="Equipe")


@infos_bp.route("/lancamentos")
def lancamentos():
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("infos/lancamentos.html", title="Lancamentos")


@infos_bp.route("/publicacoes")
def publicacoes():
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("infos/publicacoes.html", title="Publicacoes")


@infos_bp.route("/guia")
def guia(name=None):
    if "username" in session:
        return redirect(url_for("index_bp.home_get"))
    else:
        return render_template("infos/guia.html", name=name, title="Guia")
