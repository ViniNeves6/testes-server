import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Configurações de email
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_NAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.getenv("DEV_MONGO_URI")


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.getenv("DEV_MONGO_URI")


class ProductionConfig(Config):
    MONGO_URI = os.getenv("MONGO_URI")


def configure_app(app, config_name):
    """
    Configura a aplicação de acordo com o ambiente (produção, desenvolvimento, teste).
    Lança um erro claro se a configuração fornecida for inválida ou se houver erro de carregamento.

    Parâmetros:
        app: Instância da aplicação Flask.
        config_name: Nome da configuração a ser carregada (development, testing, production).

    Exceções:
        ValueError: Se um config_name inválido for fornecido.
    """

    # Definindo os ambientes válidos
    valid_configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    if config_name in valid_configs:
        app.config.from_object(valid_configs[config_name])
    else:
        raise ValueError(
            f"Configuração '{config_name}' não é válida. "
            f"As opções disponíveis são: {', '.join(valid_configs.keys())}."
        )
