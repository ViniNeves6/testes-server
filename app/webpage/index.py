import io
import zipfile
from bson import ObjectId
from app.utils.data import userdata2frame, userdata_summary
from app.utils.functions import format_ISO
from flask import render_template, Blueprint, request, session, abort, send_file
from flask import current_app as app

index_bp = Blueprint(
    "index_bp", "__name__", template_folder="templates", static_folder="static"
)


# Define a rota para a página principal
@index_bp.post("/")
def index_post():
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        if not userfound:
            abort(404)

        # carrega o folder
        dataid = request.form.get("dataid")

        # verifica os dados da data solicitada
        collection_name = f"data_{userfound['_id']}"

        # Criação de DataFrames para diferentes tipos de dados
        trace_df = userdata2frame(
            app.db,
            collection_name,
            dataid,
            ["eye", "keyboard", "freeze", "click", "wheel", "mousemove"],
        )
        voice_df = userdata2frame(app.db, collection_name, dataid, "voice")
        face_df = userdata2frame(app.db, collection_name, dataid, "face")

        document = app.db[collection_name].find_one({"_id": ObjectId(dataid)})
        image_ids = []

        # Checa se a chave 'data' existe e é uma lista
        if "data" in document and isinstance(document["data"], list):
            # Itera por cada site na lista 'data'
            for site_data in document["data"]:
                # Checa se a chave 'images' existe no dicionário do site
                if "images" in site_data:
                    image_ids.extend(
                        site_data["images"]
                    )  # Adiciona as imagens ao array de IDs

        # abort(404, description=f"Document found {image_ids}, document: {document}, collection: {collection_name}")

        # cria um zip na memória para inserção dos dados selecionados
        memory_zip = io.BytesIO()
        with zipfile.ZipFile(memory_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Adicionar DataFrame de traços como CSV
            csv_buffer = io.StringIO()
            trace_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            zipf.writestr("trace.csv", csv_buffer.getvalue())

            # Adicionar DataFrame de voz como CSV
            csv_buffer = io.StringIO()
            voice_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            zipf.writestr("voice.csv", csv_buffer.getvalue())

            # Adicionar DataFrame de rosto como CSV
            csv_buffer = io.StringIO()
            face_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            zipf.writestr("emotion.csv", csv_buffer.getvalue())

            for image_id in image_ids:
                try:
                    # Recupera o arquivo de imagem do GridFS usando o ID
                    grid_out = app.fs.get(image_id).read()
                    image_name = f'{str(image_id)}.png'
                    if image_name not in zipf.namelist():
                        zipf.writestr(image_name, grid_out)
                except Exception as e:
                    abort(404, description=f"Erro ao recuperar a imagem {image_id}: {e}")

        # Retorna o objeto ZIP em memória para download ou outras operações
        memory_zip.seek(0)

        # Fornecendo o ZIP para download usando send_file
        response = send_file(
            memory_zip,
            as_attachment=True,
            download_name=f"{dataid}_data.zip",
            mimetype="application/zip",
        )
        return response

    else:
        return render_template("index.html", session=False, title="Home")


@index_bp.get("/")
def index_get():
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"
        documents = app.db[collection_name].find({}) 

        data, date_counts = userdata_summary(documents)
        
        data = list(reversed(data))[:5]
        
        # Separar as datas e suas contagens
        dates = list(date_counts.keys())
        values = list(date_counts.values())

        #transformando para formato ISO
        datesISO = format_ISO(dates)

        return render_template(
            "index.html",
            session=True,
            username=session["username"],
            title="Home",
            data=data,
            dates=datesISO,
            values=values,
        )

    else:
        return render_template("index.html", session=False, title="Home")
