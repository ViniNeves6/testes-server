from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify, session, render_template
from flask import current_app as app
from flask_mail import Message

from app.utils.functions import id_generator

api_auth_bp = Blueprint("api_auth_bp", "__name__", url_prefix="/api/auth")


# Rota de registro
@api_auth_bp.post("/register")
def register_post():
    # Obtém o usuário, a senha e o email informados no corpo da requisição
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # Verifica se o email ou nome de usuário já existe na coleção de usuários
    email_found = app.db.users.find_one({"email": email})
    username_found = app.db.users.find_one({"username": username})

    if email_found:
        id = None
        message = "Esse email já foi cadastrado."
        status = 401
        response = {"data": id, "message": message, "status": status}
        return jsonify(response), status

    if username_found:
        id = None
        message = "Esse nome de usuário já está em uso."
        status = 401
        response = {"data": id, "message": message, "status": status}
        return jsonify(response), status

    # Cria o hash da senha
    hashed_password = generate_password_hash(password)

    # Insere o novo usuário na coleção de usuários
    app.db.users.insert_one(
        {
            "username": username,
            "password": hashed_password,
            "email": email,
            "role": "user",
        }
    )

    # Cria uma coleção específica para o usuário
    userfound = app.db.users.find_one({"username": username})
    user_collection_name = f"data_{userfound['_id']}"
    app.db[user_collection_name].insert_one(
        {"message": f"Coleção criada para o usuário {username}."}
    )

    # Retorna uma resposta de sucesso
    id = str(userfound["_id"])
    message = "Registro bem-sucedido!"
    status = 200
    response = {"data": id, "message": message, "status": status}
    return jsonify(response), status


# Rota de login
@api_auth_bp.post("/login")
def login_post():
    # Obtém o usuário e a senha informados no corpo da requisição
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Procura o usuário no banco de dados
    userfound = app.db.users.find_one({"username": username})

    # Verifica se o usuário foi encontrado
    if not userfound:
        message = "Usuário não encontrado!"
        status = 404
        response = {"message": message, "status": status}
        return jsonify(response), status

    # Verifica se a senha está correta
    if not check_password_hash(userfound["password"], password):
        message = "Senha incorreta!"
        status = 401
        response = {"message": message, "status": status}
        return jsonify(response), status

    # Login bem-sucedido
    session["username"] = username
    _id = str(userfound["_id"])
    message = "Login bem-sucedido!"
    status = 200
    response = {"data": _id, "message": message, "status": status}
    return jsonify(response), status


@api_auth_bp.post("/recover_password")
def recover_password_post():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    userfound = app.db.users.find_one({"username": username, "email": email})

    # Se as credenciais estiverem incorretas, retorna para a página de redefinir senha
    if not userfound:
        status = 404
        message = "Usuário não encontrado."
        response = {"status": status, "message": message}

    # Nova senha gerada
    generated_pass = id_generator()
    hashed_pass = generate_password_hash(generated_pass)

    # Requisição por email
    msg = Message(
        "UX-Tracking password reset.",
        sender=app.mail_username,
        recipients=[email],
    )

    # estilizando a mensagem de e-mail
    msg.html = render_template(
        "email_forgot_pass.html",
        username=username,
        generatedPass=generated_pass,
    )

    # Nova senha enviada
    app.mail.send(msg)

    # senha alterada
    _id = userfound["_id"]
    app.db.users.update_one({"_id": _id}, {"$set": {"password": hashed_pass}})
    status = 200
    message = "Senha alterada com sucesso! Cheque sua caixa de entrada do email."
    response = {"status": status, "message": message}
    return jsonify(response), status


# Define a rota para a página de alteração de senha
@api_auth_bp.post("/change_pass")
def change_pass():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    new_password = data.get("newpassword")
    confirm_new_password = data.get("confirm_newpassword")

    # Verifica se o usuário existe
    userfound = app.db.users.find_one({"username": username})

    if not userfound:
        message = "Usuário não encontrado!"
        status = 404
        return jsonify({"message": message, "status": status}), status

    # Verifica se a senha atual está correta
    if not check_password_hash(userfound["password"], password):
        message = "Senha atual incorreta!"
        status = 401
        return jsonify({"message": message, "status": status}), status

    # Verifica se as novas senhas correspondem
    if new_password != confirm_new_password:
        message = "As novas senhas não coincidem!"
        status = 400
        return jsonify({"message": message, "status": status}), status

    # Atualiza a senha no banco de dados
    new_password_hash = generate_password_hash(new_password)
    app.db.users.update_one(
        {"_id": userfound["_id"]}, {"$set": {"password": new_password_hash}}
    )
    session["username"] = username

    message = "Senha alterada com sucesso!"
    status = 200
    return jsonify({"message": message, "status": status}), status


# Rota de logout
@api_auth_bp.post("/logout")
def logout():
    session.clear()
    message = "Logout realizado com sucesso!"
    status = 200
    response = {"message": message, "status": status}
    return jsonify(response), status
