from flask_mail import Message
from app.utils.functions import id_generator
from flask import render_template, Blueprint, request, session, jsonify
from flask import current_app as app
from werkzeug.security import check_password_hash

external_auth_bp = Blueprint(
    "external_auth_bp", "__name__", template_folder="templates", static_folder="static"
)


@external_auth_bp.post("/userAuth")
def userAuth():
    username = request.form["username"]
    password = request.form["password"]
    userfound = app.db.users.find_one({"username": username})

    if userfound and check_password_hash(userfound["password"], password):
        userid = userfound["_id"]
        session["username"] = username
        response = {"id": str(userid), "status": 200}
    # Credenciais incorretas
    else:
        response = {"id": None, "status": 401}

    return jsonify(response)


@external_auth_bp.post("/userRegister")
def userRegister():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]

    # Verifica se o usuário já existe
    userfound = app.db.users.find_one({"$or": [{"email": email}, {"username": username}]})
    if userfound == None:
        app.db.users.insert_one(
            {"username": username, "password": password, "email": email, "data": {}}
        )
        userfound = app.db.users.find_one({"username": username, "password": password})
        response = {"id": str(userfound["_id"]), "status": 200}
    else:
        response = {"id": None, "status": 401}

    return jsonify(response)


@external_auth_bp.post("/userRecover")
def userRecover():
    # Obtém o usuário e email informados no formulário
    email = request.form["email"]
    userfound = app.db.users.find_one({"email": email})

    if userfound != None:
        # Nova senha gerada
        generatedPass = id_generator()

        # Requisição por email
        msg = Message(
            "UX-Tracking password reset.",
            sender=app.mail_username,
            recipients=[email],
        )

        # estilizando a mensagem de e-mail
        msg.html = render_template(
            "email_forgot_pass.html",
            username=userfound["username"],
            generatedPass=generatedPass,
        )

        # Nova senha enviada
        app.mail.send(msg)

        # senha alterada
        _id = userfound["_id"]
        app.db.users.update_one({"_id": _id}, {"$set": {"password": generatedPass}})

        response = {"status": 200}

    # Se as credenciais estiverem incorretas, retorna para a página de redefinir senha
    else:
        response = {"status": 401}

    return jsonify(response)

@external_auth_bp.post('/userLogout')
def userLogout():
    session.clear()
    response = {"status": 200}
    return jsonify(response)