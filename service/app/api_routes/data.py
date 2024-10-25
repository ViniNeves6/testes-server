import io
import re
import torch
import base64
from io import StringIO
from PIL import Image
from bson import ObjectId
import torch.nn.functional as F
from torchvision.transforms import v2 as T
from flask import request, jsonify, session, Response
from flask_restx import Namespace, Resource, fields
from flask import current_app as app

from app.utils.data import userdata2frame
from app.utils.functions import nlpBertimbau

data_ns = Namespace(
    "data", description="Operações de processamento de dados", path="/api/data"
)

# Modelos para Swagger
metadata_model = data_ns.model(
    "Metadata",
    {
        "userID": fields.String(required=True, description="ID do usuário"),
        "dateTime": fields.String(required=True, description="Data e hora do evento"),
        "site": fields.String(required=True, description="Nome do site"),
        "image": fields.String(required=True, description="Imagem em Base64"),
    },
)

data_model = data_ns.model(
    "Data",
    {
        "type": fields.List(
            fields.String, required=True, description="Tipo de interação"
        ),
        "time": fields.List(
            fields.Float, required=True, description="Tempo da interação"
        ),
        "class": fields.List(
            fields.String, required=True, description="Classe de interação"
        ),
        "id": fields.List(fields.String, required=True, description="ID da interação"),
        "x": fields.List(
            fields.Float, required=True, description="Posição X da interação"
        ),
        "y": fields.List(
            fields.Float, required=True, description="Posição Y da interação"
        ),
        "scroll": fields.List(
            fields.Boolean, required=True, description="Interação de rolagem"
        ),
        "value": fields.List(
            fields.String, required=True, description="Valor da interação"
        ),
    },
)

receive_model = data_ns.model(
    "Receive",
    {
        "metadata": fields.Nested(metadata_model, required=True),
        "data": fields.Nested(data_model, required=True),
    },
)

# Modelo para a requisição de face_expression
face_expression_model = data_ns.model(
    "FaceExpression",
    {"data": fields.String(required=True, description="Imagem codificada em Base64")},
)

# Modelo para a requisição do download de áudio
download_audio_model = data_ns.model(
    "DownloadAudioRequest",
    {
        "data": fields.String(
            required=True, description="Identificador da coleta de dados de voz"
        ),
    },
)


# Rota para envio dos dados
@data_ns.route("/receive")
class ReceiveData(Resource):
    @data_ns.expect(receive_model)
    def post(self):
        """
        Recebe dados de interação do usuário.

        **Entrada JSON**:
          - `metadata`: Metadados contendo informações sobre o usuário, data, site e imagem.
            - `userID`: ID do usuário (obrigatório).
            - `dateTime`: Data e hora do evento (obrigatório).
            - `site`: Nome do site (obrigatório).
            - `image`: Imagem codificada em Base64 (obrigatório).
          - `data`: Dados de interação com detalhes da interação do usuário.
            - `type`: Lista de tipos de interação (obrigatório).
            - `time`: Lista de tempos de cada interação (obrigatório).
            - `class`: Lista de classes de interação (obrigatório).
            - `id`: Lista de IDs de interação (obrigatório).
            - `x`: Lista de posições X (obrigatório).
            - `y`: Lista de posições Y (obrigatório).
            - `scroll`: Lista indicando se houve rolagem (obrigatório).
            - `value`: Lista de valores da interação (obrigatório).

        **Retorno**:
          - `status`: Código de status HTTP.
          - `message`: Mensagem de confirmação ou erro.

        **Códigos de Resposta**:
          - 200: Dados recebidos com sucesso.
          - 400: Dados JSON não encontrados.
          - 403: ID do usuário ausente ou usuário não encontrado.
        """
        content = request.get_json(silent=True)
        if not content:
            message = "No JSON data found"
            status = 400
            response = {"data": None, "message": message, "status": status}
            return jsonify(response), status

        metadata, data = content.get("metadata", {}), content.get("data", {})
        if not metadata.get("userID"):
            message = "No user ID provided"
            status = 403
            response = {"data": None, "message": message, "status": status}
            return jsonify(response), status

        userfound = app.db.users.find_one({"_id": ObjectId(metadata["userID"])})
        if not userfound:
            message = "User not found"
            status = 403
            response = {"data": None, "message": message, "status": status}
            return jsonify(response), status

        collection_name = f"data_{userfound['_id']}"
        result = app.db[collection_name].find_one({"datetime": metadata["dateTime"]})

        # inserção no mongo gridFS (id retornado)
        image_id = app.fs.put(
            base64.b64decode(re.sub("^data:image/\w+;base64,", "", metadata["image"]))
        )

        # Preparação da lista de interações
        interactions = [
            {
                "type": data["type"][i],
                "time": data["time"][i],
                "image": image_id,
                "class": data["class"][i],
                "id": data["id"][i],
                "x": data["x"][i],
                "y": data["y"][i],
                "scroll": data["scroll"][i],
                "height": metadata["height"],
                "value": data["value"][i],
            }
            for i in range(len(data["type"]))
        ]

        # Estrutura do documento para inserção ou atualização
        update = {
            "$addToSet": {"sites": metadata["site"]},
            "$setOnInsert": {"datetime": metadata["dateTime"]},
        }

        if result:
            # Verifica se o site já existe no documento
            site_exists = any(d["site"] == metadata["site"] for d in result["data"])
            if site_exists:
                # Adiciona as interações ao site existente
                update["$push"] = {
                    "data.$[elem].interactions": {"$each": interactions},
                    "data.$[elem].images": {"$each": [image_id]},
                }
                array_filters = [{"elem.site": metadata["site"]}]
                app.db[collection_name].update_one(
                    {"_id": result["_id"]}, update, array_filters=array_filters
                )
            else:
                # Adiciona um novo site ao array de dados
                new_site = {
                    "site": metadata["site"],
                    "images": [image_id],
                    "interactions": interactions,
                }
                update["$push"] = {"data": new_site}
                app.db[collection_name].update_one({"_id": result["_id"]}, update)
        else:
            # Insere um novo documento se não houver um existente para essa data
            new_document = {
                "datetime": metadata["dateTime"],
                "sites": [metadata["site"]],
                "data": [
                    {
                        "site": metadata["site"],
                        "images": [image_id],
                        "interactions": interactions,
                    }
                ],
            }
            app.db[collection_name].insert_one(new_document)

        # Retorna uma resposta de sucesso
        message = "Received"
        status = 200
        response = {"data": None, "message": message, "status": status}
        return jsonify(response), status


# Rota para análise de expressão facial
@data_ns.route("/face_expression")
class FaceExpression(Resource):
    @data_ns.expect(face_expression_model)
    def post(self):
        """
        Recebe uma imagem e retorna a expressão facial inferida.

        **Entrada JSON**:
          - `data`: Imagem codificada em Base64 (obrigatório).

        **Retorno**:
          - `status`: Código de status HTTP.
          - `message`: Mensagem de sucesso ou erro.
          - `data`: Dicionário com a expressão facial e respectivas probabilidades.

        **Códigos de Resposta**:
          - 200: Expressão facial inferida com sucesso.
          - 500: Erro interno durante o processamento da imagem.
        """
        try:
            image_data = request.form["data"]
            # Converte a Base64 para bytes
            header, image_data = image_data.split(",", 1)
            image_bytes = base64.b64decode(image_data)
            # Abre a imagem com Pillow
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Define a sequência de transformações
            transform = T.Compose(
                [
                    T.Resize(96),
                    T.ToTensor(),
                    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ]
            )

            # Aplica as transformações na imagem
            image_transformed = transform(image).unsqueeze(0)

            # Realiza a inferência
            with torch.no_grad():
                outputs = app.model_fer(image_transformed)
                outputs = F.softmax(outputs, dim=1)
            result = outputs.tolist()

            labels = [
                "anger",
                "contempt",
                "disgust",
                "fear",
                "happy",
                "neutral",
                "sad",
                "surprise",
            ]

            result_dict = {label: prob for label, prob in zip(labels, result[0])}

            # Retorna uma resposta de sucesso
            message = "Success"
            status = 200
            response = {"data": result_dict, "message": message, "status": status}
            return jsonify(response), status

        except Exception as e:
            message = f"Error: {e}"
            status = 500
            response = {"data": None, "message": message, "status": status}
            return jsonify(response), status


@data_ns.route("/downloadAudio")
class DownloadAudio(Resource):
    @data_ns.expect(download_audio_model)
    def post(self):
        """
        Gera um arquivo CSV com os dados de análise de voz do usuário para download.

        **Entrada JSON**:
          - `data`: Identificador da coleta de dados de voz a ser processada (obrigatório).

        **Retorno**:
          - Arquivo CSV com o conteúdo das interações de voz analisadas.

        **Códigos de Resposta**:
          - 200: CSV gerado com sucesso e pronto para download.
          - 400: Erro de requisição, campo `data` ausente ou inválido.
          - 404: Usuário não encontrado ou dados de voz não encontrados.
        """
        # Verifica se o usuário está na sessão
        userfound = app.db.users.find_one({"username": session.get("username")})
        if not userfound:
            return jsonify({"message": "Usuário não encontrado.", "status": 404}), 404

        collection_name = f"data_{userfound['_id']}"

        # Valida a entrada de dados
        data = request.get_json()
        valueData = data.get("data")
        if not valueData:
            return (
                jsonify({"message": "Campo 'data' é obrigatório.", "status": 400}),
                400,
            )

        # Processa os dados de voz
        df_voice = userdata2frame(app.db, collection_name, valueData, "voice")
        df_nlBertimbau = nlpBertimbau(df_voice)

        # Converte o DataFrame em CSV e prepara para o download
        csv_buffer = StringIO()
        df_nlBertimbau.to_csv(csv_buffer, index=False)
        file_content = csv_buffer.getvalue()

        return Response(
            file_content,
            headers={
                "Content-Type": "text/csv",
                "Content-Disposition": "attachment; filename=voice.csv",
            },
        )
