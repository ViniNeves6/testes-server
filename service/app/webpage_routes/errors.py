from flask import render_template, Blueprint
from werkzeug.exceptions import HTTPException

errors_bp = Blueprint("errors_bp", "__name__", template_folder="templates", static_folder="static")


# manipuladores de erro
@errors_bp.errorhandler(404)
def page_not_found(error):
    message = "A página que você está tentando acessar não foi encontrada neste servidor. Isso pode ocorrer devido a uma URL incorreta, uma página removida ou um link desatualizado."
    return render_template("erros/erro.html", erro=404, message=message), 404


@errors_bp.errorhandler(500)
def internal_server_error(error):
    message = "O servidor encontrou um erro interno e não pôde atender à sua solicitação. Isso pode ser devido a uma sobrecarga no servidor ou a um erro na aplicação."
    return render_template("erros/erro.html", erro=500, message=message), 500


@errors_bp.errorhandler(403)
def forbidden(error):
    message = "Você não tem permissão para acessar o recurso solicitado. Ele está protegido contra leitura ou não é legível pelo servidor."
    return render_template("erros/erro.html", erro=403, message=message), 403


@errors_bp.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        message = "Ops! Parece que encontramos um problema ao processar sua solicitação. Por favor, tente novamente mais tarde."
        return render_template("erro.html", message=message)

    message = "O servidor encontrou um erro interno e não pôde atender à sua solicitação. Isso pode ser devido a uma sobrecarga no servidor ou a um erro na aplicação."
    return render_template("erros/erro.html", erro=500, message=message), 500
