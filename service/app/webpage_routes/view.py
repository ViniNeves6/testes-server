from django.core.paginator import Paginator
from app.utils.data import userdata_summary
from flask import (
    render_template,
    Blueprint,
    session,
    request,
    abort,
)
from flask import current_app as app

from app.webpage_routes import login_required

view_bp = Blueprint(
    "view_bp", "__name__", template_folder="templates", static_folder="static"
)

@view_bp.get("/dataview")
@login_required
def dataview_get():
    # faz a leitura da base de dados de coletas do usuário
    userfound = app.db.users.find_one({"username": session["username"]})
    if not userfound:
        abort(404)

    return render_template(
        "data_view.html", username=session["username"], title="Visualização"
    )

@view_bp.get("/dataview/heatmap")
@login_required
def dataview_heatmap_get():
    # faz a leitura da base de dados de coletas do usuário
    userfound = app.db.users.find_one({"username": session["username"]})
    if not userfound:
        abort(404)

    collection_name = f"data_{userfound['_id']}"
    documents = app.db[collection_name].find({})

    data, _ = userdata_summary(documents)
    data = list(reversed(data))
    paginator = Paginator(data, 5)
    page_number = request.args.get("page_number", 1, type=int)
    page_obj = paginator.get_page(page_number)
    page_coleta = paginator.page(page_number).object_list

    return render_template(
        "data_view.html",
        username=session["username"],
        plot='heatmap',
        items=page_coleta,
        page_obj=page_obj,
        title="Visualização",
    )

@view_bp.get("/dataview/recording")
@login_required
def dataview_recording_get():
    # faz a leitura da base de dados de coletas do usuário
    userfound = app.db.users.find_one({"username": session["username"]})
    if not userfound:
        abort(404)

    collection_name = f"data_{userfound['_id']}"
    documents = app.db[collection_name].find({})

    data, _ = userdata_summary(documents)
    data = list(reversed(data))
    paginator = Paginator(data, 5)
    page_number = request.args.get("page_number", 1, type=int)
    page_obj = paginator.get_page(page_number)
    page_coleta = paginator.page(page_number).object_list

    return render_template(
        "data_view.html",
        username=session["username"],
        plot='recording',
        items=page_coleta,
        page_obj=page_obj,
        title="Visualização",
    )
