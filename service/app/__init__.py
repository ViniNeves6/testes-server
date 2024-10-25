import pymongo
import logging
from flask import Flask
from authlib.integrations.flask_client import OAuth
import os
import gridfs
from flask_mail import Mail
from simple_colors import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from dotenv import load_dotenv
from flask_restx import Api

# Carregar variáveis do arquivo .env
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.example_user import gen_example
from app.utils.models import load_fer, load_bert
from config import configure_app

from service.app.api_routes.namespaces import api_namespaces


def send_email(app, subject, body):
    # Configurar as informações de email
    sender_email = app.config.get("MAIL_USERNAME")
    sender_password = app.config.get("MAIL_PASSWORD")
    receiver_email = "flavio.moura@itec.ufpa.br"

    # Criar o objeto de mensagem
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Adicionar o corpo da mensagem
    message.attach(MIMEText(body, "plain"))

    # Enviar o email usando SMTP
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()


# declarando o servidor
def create_app(environment="production"):
    # Criar o objeto Flask
    app = Flask(__name__)

    # Configuração básica do log
    loglevel = logging.DEBUG if environment == "development" else logging.INFO
    logging.basicConfig(level=loglevel)

    # Configurações baseadas no ambiente
    configure_app(app, environment)
    logging.info("Aplicação configurada.")

    # Carregando o email
    app.config["MAIL"] = Mail(app)

    # Inicializar MongoClient e armazenar no app.config
    mongo_client = pymongo.MongoClient(app.config.get("MONGO_URI"))
    app.config["MONGO_CLIENT"] = (
        mongo_client  # cliente para testar a conexão com o mongodb (poderá ser removido posteriormente)
    )
    app.config["MONGO_DB"] = mongo_client.uxtracking
    app.config["MONGO_FS"] = gridfs.GridFS(app.config.get("MONGO_DB"))
    logging.info("Configuração do MongoDB bem sucedidada.")

    try:
        app.config.get("MONGO_DB").command("ping")
        logging.info("Conexão com o MongoDB foi bem sucedida.")
    except pymongo.errors.ConnectionFailure as e:
        logging.error(f"Falha ao conectar ao MongoDB: {e}")

    # verifica se não há nenhum usuário no banco, então cria um usuário exemplo
    gen_example(app.config.get("MONGO_DB"), app.config.get("MONGO_FS"))

    """for bp in webpage_bps:
        app.register_blueprint(bp, url_prefix="/")"""

    # Inicializar flask_restx Api e adicionar namespaces
    api = Api(
        title="UX-Tracking API",
        version="1.0",
        doc='/api/doc',
        description="API da ferramenta UX-Tracking\n\nFerramenta de captura multimodal de suporte à avaliação da experiência do usuário.",
    )

    # Adicionar os namespaces
    for ns in api_namespaces:
        api.add_namespace(ns)

    # facial expression model
    app.config["FER_MODEL"] = load_fer()

    # bert model
    app.config["BERT_TOKENIZER"], app.config["BERT_MODEL"] = load_bert()

    # autenticação google
    app.config["OAUTH"] = OAuth(app)

    # Inicializar a API na aplicação Flask
    api.init_app(app)

    return app
