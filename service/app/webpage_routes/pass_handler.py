from flask_mail import Message
from app.utils.functions import id_generator
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, Blueprint, request, redirect, session, flash, url_for
from flask import current_app as app

pass_bp = Blueprint("pass_bp", "__name__", template_folder="templates", static_folder="static")

# Define a rota para reset de password
@pass_bp.post("/forgot_pass")
def forgot_pass_post():
    # Obtém o usuário e email informados no formulário
    username = request.form["username"]
    email = request.form["email"]
    userfound = app.db.users.find_one({"username": username, "email": email})

    if userfound != None:
        # Se as credenciais estiverem corretas, envia um email para o usuário
        # com a nova senha criada e redireciona para o login

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
            "email_forgot_pass.html", username=username, generatedPass=generatedPass
        )

        # Nova senha enviada
        app.mail.send(msg)

        flash("E-mail enviado com sucesso!")

        # senha alterada
        new_password_hash = generate_password_hash(generatedPass)
        _id = userfound["_id"]
        app.db.users.update_one({"_id": _id}, {"$set": {"password": new_password_hash}})

        # Redirecionar para o login após o envio do email e atualização da senha
        return redirect(url_for("auth_bp.login_get", title="Login", session=False))

    # Se as credenciais estiverem incorretas, retorna para a página de redefinir senha
    else:
        flash("Usuário incorreto")
        return render_template(
            "forgot_pass.html", session=False, title="Esqueci a senha"
        )


@pass_bp.get("/forgot_pass")
def forgot_pass_get():
    return render_template("forgot_pass.html", session=False, title="Esqueci a senha")


# Define a rota para a página de alteração de senha
@pass_bp.post("/change_pass")
def change_pass():
    if "username" in session:
        # Obtém o usuário e a senha informados no formulário
        username = session["username"]
        password = request.form["password"]
        newpassword = request.form["newpassword"]
        newpassword2 = request.form["confirm_newpassword"]

        # Verifica se as credenciais estão corretas
        userfound = app.db.users.find_one({"username": username})
        if userfound and check_password_hash(userfound["password"], password):
            if newpassword == newpassword2:
                _id = userfound["_id"]
                new_password_hash = generate_password_hash(newpassword)
                app.db.users.update_one({"_id": _id}, {"$set": {"password": new_password_hash}})
                # Usuário logado
                return redirect(
                    url_for(
                        "index_bp.index_get",
                        session=True,
                        title="Home",
                        username=session["username"],
                    )
                )

            else:
                flash(
                    "Verifique se ambas as novas senhas são iguais e tente novamente!"
                )
                return render_template("index.html", session=True, title="Home")
        else:
            flash("A senha atual está incorreta!")
            return render_template("index.html", session=True, title="Home")

    else:
        flash("Faça o login!")
        return render_template("login.html", session=False, title="Login")
