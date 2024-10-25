from flask import (
    request,
    jsonify,
    session,
    render_template,
    current_app as app,
)
from flask_mail import Message
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.functions import id_generator
from app.api_routes import login_required

auth_ns = Namespace("auth", description="Operações de autenticação", path="/api/auth")

# Modelo para a requisição de registro
register_model = auth_ns.model(
    "Register",
    {
        "username": fields.String(required=True, description="Nome de usuário"),
        "password": fields.String(required=True, description="Senha"),
        "email": fields.String(required=True, description="Email"),
    },
)

# Modelo para o login
login_model = auth_ns.model(
    "Login",
    {
        "username": fields.String(required=True, description="Nome de usuário"),
        "password": fields.String(required=True, description="Senha"),
    },
)

# Modelo para recuperação de senha
recover_pass_model = auth_ns.model(
    "RecoverPassword",
    {
        "username": fields.String(required=True, description="Nome de usuário"),
        "email": fields.String(required=True, description="Email"),
    },
)


# Modelo para mudança de senha
change_pass_model = auth_ns.model(
    "ChangePassword",
    {
        "username": fields.String(required=True, description="Nome de usuário"),
        "password": fields.String(required=True, description="Senha atual"),
        "newpassword": fields.String(required=True, description="Nova senha"),
        "confirm_newpassword": fields.String(
            required=True, description="Confirmação da nova senha"
        ),
    },
)


# Rota de registro
@auth_ns.route("/register")
class Register(Resource):
    @auth_ns.expect(register_model)
    def post(self):
        """
        Registra um novo usuário.

        **Entrada JSON**:
          - `username`: Nome de usuário (obrigatório).
          - `password`: Senha do usuário (obrigatório).
          - `email`: Endereço de email do usuário (obrigatório).

        **Retorno**:
          - `data`: ID do usuário cadastrado (string).
          - `message`: Mensagem de confirmação do registro.
          - `status`: Código de status HTTP.

        **Códigos de Resposta**:
          - 200: Registro bem-sucedido.
          - 401: Email ou nome de usuário já em uso.
        """
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
@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """
        Realiza o login do usuário.

        **Entrada JSON**:
          - `username`: Nome de usuário (obrigatório).
          - `password`: Senha do usuário (obrigatório).

        **Retorno**:
          - `data`: ID do usuário logado (string).
          - `message`: Mensagem de confirmação do login.
          - `status`: Código de status HTTP.

        **Códigos de Resposta**:
          - 200: Login bem-sucedido.
          - 401: Senha incorreta.
          - 404: Usuário não encontrado.
        """
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


# Rota de mudança de senha
@auth_ns.route("/recover_password")
class RecoverPassword(Resource):
    @auth_ns.expect(recover_pass_model)
    def post(self):
        """
        Recupera a senha do usuário.

        **Entrada JSON**:
          - `username`: Nome de usuário (obrigatório).
          - `email`: Email cadastrado do usuário (obrigatório).

        **Retorno**:
          - `status`: Código de status HTTP.
          - `message`: Mensagem informando o status da recuperação de senha.

        **Códigos de Resposta**:
          - 200: Senha recuperada e enviada ao email.
          - 404: Usuário não encontrado.
        """
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        userfound = app.db.users.find_one({"username": username, "email": email})

        # Se as credenciais estiverem incorretas, retorna para a página de redefinir senha
        if not userfound:
            status = 404
            message = "Usuário não encontrado."
            response = {"status": status, "message": message}
            return jsonify(response), status

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


# Rota de mudança de senha
@auth_ns.route("/change_pass")
class ChangePassword(Resource):
    @auth_ns.expect(change_pass_model)
    def put(self):
        """
        Altera a senha do usuário.

        **Entrada JSON**:
          - `username`: Nome de usuário (obrigatório).
          - `password`: Senha atual do usuário (obrigatório).
          - `newpassword`: Nova senha (obrigatório).
          - `confirm_newpassword`: Confirmação da nova senha (obrigatório).

        **Retorno**:
          - `status`: Código de status HTTP.
          - `message`: Mensagem de confirmação da alteração de senha.

        **Códigos de Resposta**:
          - 200: Senha alterada com sucesso.
          - 400: Confirmação de nova senha não corresponde.
          - 401: Senha atual incorreta.
          - 404: Usuário não encontrado.
        """
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
@auth_ns.route("/logout")
class Logout(Resource):
    @login_required
    def delete(self):
        """
        Realiza o logout do usuário atual.

        **Requer autenticação**

        **Retorno**:
          - `status`: Código de status HTTP.
          - `message`: Mensagem de confirmação de logout.

        **Códigos de Resposta**:
          - 200: Logout realizado com sucesso.
        """
        session.clear()
        message = "Logout realizado com sucesso!"
        status = 200
        response = {"message": message, "status": status}
        return jsonify(response), status
