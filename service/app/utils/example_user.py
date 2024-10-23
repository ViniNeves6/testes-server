from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)
def gen_example(mongo, fs):
    try:
        # Verificar se já existe o usuário "admin"
        userfound = mongo.users.find_one({"username": "admin"})
        if userfound:
            logger.info("Usuário 'admin' já existe. Nenhuma ação necessária.")
            return
            
        # Não há usuários, então crie um novo teste
        new_user = {
            "username": "admin",
            "email": "uxtracking.service@gmail.com",
            "role": "admin",
            "password": generate_password_hash("ux12tracking")
        }
        mongo.users.insert_one(new_user)
        userfound = mongo.users.find_one({"username": "admin"})
        user_collection_name=f"data_{userfound['_id']}"
        
        with open("UX-Tracking Banner.png", 'rb') as f:
            contents = f.read()

        image_id = fs.put(contents, filename="default")

        data_admin = {
        "datetime": "2024-02-01T14:50:24Z",
        "sites": ["site1", "site2"],
        "data": [
            {
                "site": "site1",
                "images": [image_id],
                "interactions": [
                    {
                        "type": "eye",
                        "time": 1,
                        "image": image_id,
                        "class": "classe1",
                        "id": "id1",
                        "x": 10,
                        "y": 10,
                        "scroll": 10,
                        "height": 1000,
                        "value": "None"
                    },
                    {
                        "type": "mouse",
                        "time": 2,
                        "image": image_id,
                        "class": "classe2",
                        "id": "id2",
                        "x": 20,
                        "y": 20,
                        "scroll": 20,
                        "height": 1000,
                        "value": "None"
                    },
                    {
                        "type": "keyboard",
                        "time": 3,
                        "image": image_id,
                        "class": "classe3",
                        "id": "id3",
                        "x": 30,
                        "y": 30,
                        "scroll": 30,
                        "height": 1000,
                        "value": {
                            "key": "keys"
                        }
                    },
                    {
                        "type": "freeze",
                        "time": 4,
                        "image": image_id,
                        "class": "classe4",
                        "id": "id4",
                        "x": 40,
                        "y": 40,
                        "scroll": 40,
                        "height": 1000,
                        "value": "None"
                    }
                ]
            },
            {
                "site": "site2",
                "images": [image_id],
                "interactions": [
                    {
                        "type": "click",
                        "time": 5,
                        "image": image_id,
                        "class": "classe5",
                        "id": "id5",
                        "x": 50,
                        "y": 50,
                        "scroll": 50,
                        "height": 1200,
                        "value": "None"
                    },
                    {
                        "type": "wheel",
                        "time": 6,
                        "image": image_id,
                        "class": "classe6",
                        "id": "id6",
                        "x": 60,
                        "y": 60,
                        "scroll": 60,
                        "height": 1200,
                        "value": "None"
                    },
                    {
                        "type": "move",
                        "time": 7,
                        "image": image_id,
                        "class": "classe7",
                        "id": "id7",
                        "x": 70,
                        "y": 70,
                        "scroll": 70,
                        "height": 1200,
                        "value": "None"
                    },
                    {
                        "type": "voice",
                        "time": 8,
                        "image": image_id,
                        "class": "classe8",
                        "id": "id8",
                        "x": 80,
                        "y": 80,
                        "scroll": 80,
                        "height": 1200,
                        "value": {
                            "text": "string"
                        }
                    },
                    {
                        "type": "face",
                        "time": 9,
                        "image": image_id,
                        "class": "classe9",
                        "id": "id9",
                        "x": 90,
                        "y": 90,
                        "scroll": 90,
                        "height": 1200,
                        "value": {
                            "anger": 0.1,
                            "contempt": 0.1,
                            "disgust": 0.1,
                            "fear": 0.2,
                            "happy": 0.2,
                            "neutral": 0.1,
                            "sad": 0.1,
                            "surprise": 0.1
                        }
                    }
                ]
            }
        ]
        }

        # Inserir os dados de interação no MongoDB
        mongo[user_collection_name].insert_one(data_admin)
        logger.info(f"Dados de interação inseridos com sucesso para o usuário 'admin' na coleção: {user_collection_name}")

    except Exception as e:
        logger.error(f"Erro ao gerar exemplo para o usuário 'admin': {str(e)}")