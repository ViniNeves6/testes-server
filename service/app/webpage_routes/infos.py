from flask import render_template, Blueprint, redirect, session, url_for

infos_bp = Blueprint("infos_bp", "__name__", template_folder="templates", static_folder="static")


@infos_bp.route("/equipe")
def equipe():
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("equipe.html", session=False, title="Equipe")


@infos_bp.route("/lancamentos")
def lancamentos():
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("lancamentos.html", session=False, title="Lancamentos")


@infos_bp.route("/publicacoes")
def publicacoes():
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("publicacoes.html", session=False, title="Publicacoes")


@infos_bp.route("/guia")
def guia(name=None):
    if "username" in session:
        return redirect(url_for("index_bp.index_get"))
    else:
        return render_template("guia.html", name=name, session=False, title="Guia")
