import io
import json
import base64
from PIL import Image
from flask import request, jsonify, session
from flask_restx import Namespace, Resource, fields
from flask import current_app as app

from app.utils.data import userdata2frame, remove_non_utf8, userdata_summary
from app.utils.plot import create_blank_image_base64, generate_trace_recording
from app.api_routes import login_required

view_ns = Namespace(
    "view", description="Operações de visualização de dados", path="/api/view"
)

# Modelo para documentação da entrada da requisição
heatmap_request = view_ns.model(
    "HeatmapRequest",
    {"dir": fields.String(required=True, description="Diretório da coleta de dados")},
)

recording_request = view_ns.model(
    "RecordingRequest",
    {"dir": fields.String(required=True, description="Diretório da coleta de dados")},
)


# Rota de processamento de dados para heatmap
@view_ns.route("/heatmap")
class Heatmap(Resource):
    @view_ns.expect(heatmap_request)
    @login_required
    def post(self):
        """
        Processa dados de interações do usuário para visualização de heatmap.

        **Requer autenticação**

        Retorna as interações do tipo "click", "wheel" e "mousemove" em um formato adequado para visualização
        de heatmap, junto com as imagens associadas às interações e dados de voz correspondentes.

        **Parâmetros do JSON de entrada**:
          - `dir`: (string) O diretório específico que contém os dados da coleta.

        **Retorna**:
          - `plot`: Tipo de visualização (heatmap)
          - `images`: Imagens codificadas em Base64 associadas às interações
          - `trace`: Dados de interações para o heatmap (JSON)
          - `voice`: Dados de voz associados às interações (JSON)
        """
        # Validação da entrada
        data = request.get_json()
        if not data or "dir" not in data:
            return (
                jsonify({"message": "O campo 'dir' é obrigatório.", "status": "error"}),
                400,
            )

        dir = data["dir"]

        # Busca informações do usuário logado
        userfound = app.db.users.find_one({"username": session["username"]})
        if not userfound:
            return (
                jsonify({"message": "Usuário não encontrado.", "status": "error"}),
                404,
            )

        collection_name = f"data_{userfound['_id']}"
        results = {"plot": "heatmap", "images": {}, "trace": None, "voice": None}

        try:
            # Processa os dados de interação
            df_trace = userdata2frame(
                app.db, collection_name, dir, ["click", "wheel", "mousemove"]
            )
            df_audio = userdata2frame(app.db, collection_name, dir, "voice")

            # Filtra os DataFrames para reduzir o tamanho da resposta JSON
            filtered_df_trace = df_trace[
                ["time", "type", "x", "y", "image", "scroll"]
            ].copy()
            filtered_df_voice = df_audio[["text", "time", "image"]].copy()

            # Processamento das imagens associadas
            def process_image(im_id):
                try:
                    file_data = app.fs.get(im_id).read()
                    img = Image.open(io.BytesIO(file_data))
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG", optimize=True)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    return str(im_id), "data:image/png;base64," + img_base64
                except Exception as e:
                    print(f"Erro ao processar a imagem {im_id}: {e}")
                    return str(im_id), create_blank_image_base64()

            # Processa todas as imagens de forma síncrona
            results_img = {im_id: process_image(im_id) for im_id in df_trace["image"].unique()}
            results["images"] = results_img

            # Remove caracteres não UTF-8 dos DataFrames
            results["trace"] = remove_non_utf8(filtered_df_trace).to_json(
                orient="records"
            )
            results["voice"] = remove_non_utf8(filtered_df_voice).to_json(
                orient="records"
            )

            return jsonify(results), 200

        except Exception as e:
            print(f"Erro ao processar o heatmap: {e}")
            return (
                jsonify({"message": "Erro ao processar o heatmap", "error": str(e)}),
                500,
            )


# Rota de processamento de dados para recording
@view_ns.route("/recording")
class Recording(Resource):
    @view_ns.expect(recording_request)
    @login_required
    def post(self):
        """
        Processa dados de interações do usuário para visualização de gravação (recording).

        **Requer autenticação**

        Retorna as interações do tipo "eye", "keyboard", "freeze", "click", "wheel", e "mousemove" em um formato adequado
        para visualização de gravação, junto com as imagens e ícones associados.

        **Parâmetros do JSON de entrada**:
          - `dir`: (string) O diretório específico que contém os dados da coleta.

        **Retorna**:
          - `plot`: Tipo de visualização (recording)
          - `images`: Imagens codificadas em Base64 associadas às interações
          - `icons`: Ícones para as interações
          - `trace`: Dados de interações para a visualização de gravação (JSON)
        """
        # Validação da entrada
        data = request.get_json()
        if not data or "dir" not in data:
            return (
                jsonify({"message": "O campo 'dir' é obrigatório.", "status": "error"}),
                400,
            )

        dir = data["dir"]

        # Busca informações do usuário logado
        userfound = app.db.users.find_one({"username": session["username"]})
        if not userfound:
            return (
                jsonify({"message": "Usuário não encontrado.", "status": "error"}),
                404,
            )

        collection_name = f"data_{userfound['_id']}"
        results = {"plot": "recording", "images": {}, "icons": None, "trace": None}

        try:
            # Processa os dados de interação
            df_trace = userdata2frame(
                app.db,
                collection_name,
                dir,
                ["eye", "keyboard", "freeze", "click", "wheel", "mousemove"],
            )
            df_trace_site = df_trace[
                ["site", "type", "time", "x", "y", "scroll", "height"]
            ].copy()
            df_trace_site = remove_non_utf8(df_trace_site)

            # Gera os ícones para o recording
            full_ims, type_icon = generate_trace_recording(df_trace)
            results["icons"] = json.dumps(type_icon)



            # Processamento das imagens associadas
            def transform_b64(key, img):
                try:
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG", optimize=True)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    return str(key), "data:image/png;base64," + img_base64
                except Exception as e:
                    print(f"Erro ao processar a imagem {key}: {e}")
                    return str(key), create_blank_image_base64()

            # Processa todas as imagens de forma síncrona
            transform_img = {key: transform_b64(key, img) for key, img in full_ims.items()}
            results["images"] = dict(transform_img)

            # Dados das interações (trace)
            results["trace"] = df_trace_site.to_json(orient="records")

            return jsonify(results), 200

        except Exception as e:
            print(f"Erro ao processar o recording: {e}")
            return (
                jsonify({"message": "Erro ao processar o recording", "error": str(e)}),
                500,
            )
