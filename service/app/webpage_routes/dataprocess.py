import io
import json
import base64
import gridfs
import asyncio
import zipfile
from PIL import Image
import pandas as pd
from io import StringIO
from bson import ObjectId
from datetime import datetime
from django.core.paginator import Paginator
from app.utils.functions import nlpBertimbau, df_graph_sentiment
from app.utils.data import userdata2frame, remove_non_utf8, userdata_summary
from app.utils.plot import create_blank_image_base64, generate_trace_recording
from flask import (
    render_template,
    Blueprint,
    redirect,
    session,
    url_for,
    request,
    flash,
    Response,
    abort,
)
from flask import current_app as app

data_bp = Blueprint(
    "data_bp", "__name__", template_folder="templates", static_folder="static"
)


@data_bp.post("/datafilter/<username>/<metadata>")
def datafilter_post(username, metadata):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"  # pasta dos documentos

        if metadata == "datetime":
            # adiciona as datas à seção
            session["dates"] = request.form.getlist("dates[]")

            # refireciona pra seleção dos traços
            return redirect(
                url_for("data_bp.datafilter_get", username=username, metadata="pages")
            )

        elif metadata == "pages":
            session["pages"] = request.form.getlist("pages[]")
            username = session.get("username")

            dates = session.get("dates")

            # Preparando o DataFrame vazio com colunas definidas
            columns_trace = [
                "site",
                "image",
                "type",
                "time",
                "class",
                "id",
                "mouseClass",
                "mouseID",
                "x",
                "y",
                "scroll",
                "height",
                "keys",
            ]
            tracefiltered = pd.DataFrame(columns=columns_trace)

            columns_audio = [
                "site",
                "image",
                "type",
                "time",
                "class",
                "id",
                "mouseClass",
                "mouseID",
                "x",
                "y",
                "scroll",
                "height",
                "text",
            ]
            audiofiltered = pd.DataFrame(columns=columns_audio)

            # Preparando o DataFrame vazio com colunas definidas
            columns_emotions = [
                "site",
                "image",
                "type",
                "time",
                "class",
                "id",
                "mouseClass",
                "mouseID",
                "x",
                "y",
                "scroll",
                "height",
                "anger",
                "contempt",
                "disgust",
                "fear",
                "happy",
                "neutral",
                "sad",
                "surprise",
            ]
            facefiltered = pd.DataFrame(columns=columns_trace)

            # Criando o arquivo ZIP em memória
            memory_zip = io.BytesIO()
            with zipfile.ZipFile(memory_zip, "w", zipfile.ZIP_DEFLATED) as zipf:

                # Filtyrar dados para cada data especificada
                for date in dates:

                    # preparando dataframes
                    trace_df = userdata2frame(
                        app.db,
                        collection_name,
                        date,
                        [
                            "eye",
                            "keyboard",
                            "freeze",
                            "click",
                            "wheel",
                            "mousemove",
                        ],
                    )

                    voice_df = userdata2frame(app.db, collection_name, date, "voice")
                    face_df = userdata2frame(app.db, collection_name, date, "face")

                    # data da coleta
                    document = app.db[collection_name].find_one({"_id": ObjectId(date)})
                    date = document["datetime"]
                    date_obj = datetime.fromisoformat(date.rstrip("Z"))
                    date_part = date_obj.date().strftime("%d/%m/%Y")

                    # tratando os dados de acordo com as pages
                    df_site_trace = trace_df[trace_df.site.isin(session["pages"])]
                    df_site_voice = voice_df[voice_df.site.isin(session["pages"])]
                    df_site_face = face_df[face_df.site.isin(session["pages"])]

                    # Adiciona a coluna 'data' no início de todos os DataFrames
                    df_site_trace.insert(
                        0, "data", [date_part] * len(df_site_trace.index), True
                    )
                    df_site_voice.insert(
                        0, "data", [date_part] * len(df_site_voice.index), True
                    )
                    df_site_face.insert(
                        0, "data", [date_part] * len(df_site_face.index), True
                    )

                    # tratando os dados
                    tracefiltered = pd.concat([df_site_trace, tracefiltered])
                    audiofiltered = pd.concat([df_site_voice, audiofiltered])
                    facefiltered = pd.concat([df_site_face, facefiltered])

                    # tratando as imagens
                    image_ids = []

                    if "data" in document and isinstance(document["data"], list):
                        for site_data in document["data"]:
                            if site_data["site"] in session["pages"]:
                                if "images" in site_data:
                                    image_ids.extend(site_data["images"])

                    # guardando as imagens no zip
                    app.fs = gridfs.GridFS(app.db)

                    for image_id in image_ids:
                        try:
                            grid_out = app.fs.get(image_id).read()
                            image_name = f"{str(image_id)}.png"
                            if image_name not in zipf.namelist():
                                zipf.writestr(image_name, grid_out)

                        except Exception as e:
                            abort(
                                404,
                                description=f"Erro ao recuperar a imagem {image_id}: {e}",
                            )

                # verifica se os arquivos estão vazios
                if not tracefiltered.empty:
                    csv_buffer = io.StringIO()
                    tracefiltered.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    zipf.writestr("trace.csv", csv_buffer.read())
                if not audiofiltered.empty:
                    csv_buffer = io.StringIO()
                    audiofiltered.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    zipf.writestr("voice.csv", csv_buffer.read())

                if not facefiltered.empty:
                    csv_buffer = io.StringIO()
                    facefiltered.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    zipf.writestr("face.csv", csv_buffer.read())

            # Preparar o arquivo para download
            memory_zip.seek(0)
            return Response(
                memory_zip,
                headers={
                    "Content-Type": "application/zip",
                    "Content-Disposition": f"attachment; filename={username}_data.zip;",
                },
            )

        else:
            flash("404\nPage not found!")
            return render_template(
                "data_filter.html", username=username, title="Coletas"
            )

    # se o usuário não está logado
    else:
        return render_template("index.html", session=False, title="Home")


@data_bp.get("/datafilter/<username>/<metadata>")
def datafilter_get(username, metadata):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"  # pasta dos documentos
        documents = app.db[collection_name].find({})

        data, date_counts = userdata_summary(documents)  # informações documentos

        if metadata == "datetime":
            # Paginação das coletas
            data = list(reversed(data))
            paginator = Paginator(data, 5)
            page_number = request.args.get("page_number", 1, type=int)
            page_obj = paginator.get_page(page_number)
            page_coleta = paginator.page(page_number).object_list

            return render_template(
                "data_filter.html",
                username=username,
                metadata=metadata,
                items=page_coleta,
                page_obj=page_obj,
                title="Coletas",
            )

        elif metadata == "pages":
            dates = session["dates"]

            # verifica quais datas estão disponíveis
            pages = []

            for date in dates:
                # procurando os sites dos documentos pelo id
                document = app.db[collection_name].find_one({"_id": ObjectId(date)})
                site = document["sites"]
                for page in site:
                    if page not in pages:
                        pages.append(page)

            return render_template(
                "data_filter.html",
                username=username,
                metadata=metadata,
                items=pages,
                title="Coletas",
            )

        else:
            flash("404\nPage not found!")
            return render_template(
                "data_filter.html", username=username, title="Coletas"
            )

    # se o usuário não está logado
    else:
        return redirect(url_for("index_bp.index_get"))


@data_bp.post("/dataanalysis/<username>/<model>")
def dataanalysis_post(username, model):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"  # pasta dos documentos

        dir = request.form["dir"]

        if model == "kmeans":
            return
        elif model == "meanshift":
            return
        elif model == "bertimbau":
            results = {}
            df_voice = userdata2frame(app.db, collection_name, dir, "voice")
            try:
                df_audio = nlpBertimbau(df_voice)
                df_radar, df_sentiment = df_graph_sentiment(df_audio)

                # transformando os df em json para serem processados no js
                results["result1"] = df_radar.to_json(orient="records")
                results["result2"] = df_sentiment.to_json(orient="records")
                results["result3"] = True

            except:
                results["result1"] = (
                    "Não foi possível processar a coleta, áudio ausente!"
                )
                results["result2"] = True
                results["result3"] = False

            return results

        else:
            flash("404\nPage not found!")
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )

    # usuário não está logado
    else:
        flash("Faça o login para continuar!")
        return render_template("login.html", session=False, title="Login")


@data_bp.get("/dataanalysis/<username>/<model>")
def dataanalysis_get(username, model):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"
        documents = app.db[collection_name].find({})

        data, date_counts = userdata_summary(documents)

        models = ["kmeans", "meanshift", "bertimbau"]
        if model == "default":
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )
        elif model in models:
            # Paginação das coletas
            data = list(reversed(data))
            paginator = Paginator(data, 5)
            page_number = request.args.get("page_number", 1, type=int)
            page_obj = paginator.get_page(page_number)
            page_coleta = paginator.page(page_number).object_list

            return render_template(
                "data_analysis.html",
                username=username,
                model=model,
                items=page_coleta,
                page_obj=page_obj,
                title="Análise",
            )
        else:
            flash("404\nPage not found!")
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )
    else:
        flash("Faça o login para continuar!")
        return render_template("login.html", session=False, title="Login")


@data_bp.post("/downloadAudio")
def downloadAudio():
    userfound = app.db.users.find_one({"username": session["username"]})
    collection_name = f"data_{userfound['_id']}"

    valueData = request.form["data"]

    df_voice = userdata2frame(app.db, collection_name, valueData, "voice")
    df_nlBertimbau = nlpBertimbau(df_voice)

    # Convertendo o DataFrame em um buffer de texto
    csv_buffer = StringIO()
    df_nlBertimbau.to_csv(csv_buffer, index=False)

    # Obtendo o conteúdo do buffer como uma string
    file_content = csv_buffer.getvalue()

    return Response(
        file_content,
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=voice.csv",
        },
    )


@data_bp.post("/dataview/<username>/<plot>")
async def dataview_post(username, plot):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        collection_name = f"data_{userfound['_id']}"
        dir = request.form["dir"]

        if plot == "heatmap":
            results = {}
            full_base64 = {}

            df_trace = userdata2frame(
                app.db,
                collection_name,
                dir,
                ["click", "wheel", "mousemove"],
            ) 
            
            df_audio = userdata2frame(app.db, collection_name, dir, "voice")

            # Filtra os DataFrames para diminuir o tamanho do JSON enviado
            filtered_df_trace = df_trace[["time", "type", "x", "y", "image", "scroll"]].copy()
            filtered_df_voice = df_audio[["text", "time", "image"]].copy()

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

            async def async_process_image(im_id):
                return await asyncio.to_thread(process_image, im_id)

            tasks = [async_process_image(im_id) for im_id in df_trace["image"]]
            results_img = await asyncio.gather(*tasks)

            for im_id, img_base64 in results_img:
                full_base64[im_id] = img_base64

            # Remove caracteres não UTF-8 dos DataFrames
            filtered_df_trace = remove_non_utf8(filtered_df_trace)
            filtered_df_voice = remove_non_utf8(filtered_df_voice)

            results["plot"] = "heatmap"
            results["images"] = json.dumps(full_base64)
            results["trace"] = filtered_df_trace.to_json(orient="records")
            results["voice"] = filtered_df_voice.to_json(orient="records")

            return results

        elif plot == "recording":
            results = {}
            full_base64 = {}

            df_trace = userdata2frame(
                app.db,
                collection_name,
                dir,
                ["eye", "keyboard", "freeze", "click", "wheel", "mousemove"],
            )

            full_ims, type_icon = generate_trace_recording(df_trace)

            async def transform_b64(key, img):
                try:
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG", optimize=True)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    return str(key), "data:image/png;base64," + img_base64
                except Exception as e:
                    print(f"Erro ao processar a imagem {key}: {e}")
                    return str(key), create_blank_image_base64()

            tasks = [transform_b64(key, img) for key, img in full_ims.items()]
            transform_img = await asyncio.gather(*tasks)

            for key, img in transform_img:
                full_base64[key] = img

            df_trace_site = df_trace[
                ["site", "type", "time", "x", "y", "scroll", "height"]
            ].copy()

            # resultados enviados para js
            results["plot"] = "recording"
            results["images"] = json.dumps(full_base64)
            results["icons"] = json.dumps(type_icon)
            results["trace"] = df_trace_site.to_json(orient="records")

            return results

        elif plot == "nlp":
            return

        else:
            flash("404\nPage not found!")
            return render_template(
                "data_analysis.html", username=username, title="Análise"
            )

    # usuário não está logado
    else:
        flash("Faça o login para continuar!")
        return render_template("login.html", session=False, title="Login")


@data_bp.get("/dataview/<username>/<plot>")
def dataview_get(username, plot):
    if "username" in session:
        # faz a leitura da base de dados de coletas do usuário
        userfound = app.db.users.find_one({"username": session["username"]})
        if not userfound:
            abort(404)

        collection_name = f"data_{userfound['_id']}"
        documents = app.db[collection_name].find({})

        plots = ["heatmap", "recording"]

        if plot == "default":
            return render_template(
                "data_view.html", username=username, title="Visualização"
            )
        elif plot in plots:
            data, _ = userdata_summary(documents)
            data = list(reversed(data))
            paginator = Paginator(data, 5)
            page_number = request.args.get("page_number", 1, type=int)
            page_obj = paginator.get_page(page_number)
            page_coleta = paginator.page(page_number).object_list

            return render_template(
                "data_view.html",
                username=username,
                plot=plot,
                items=page_coleta,
                page_obj=page_obj,
                title="Visualização",
            )
        else:
            flash("404\nPage not found!")
            return render_template(
                "data_view.html", username=username, title="Visualização"
            )
    else:
        flash("Faça o login para continuar!")
        return render_template("login.html", session=False, title="Login")
