import string
import random
import pandas as pd
import pytz
import os
import torch
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np
from datetime import datetime
from flask import current_app


id2label = {
    0: "RAIVA",
    1: "MEDO",
    2: "TRISTEZA",
    3: "SURPRESA",
    4: "ALEGRIA",
    5: "NOJO",
}


def format_ISO(dates):
    iso_format_dates = []

    for date in dates:
        date_obj = datetime.strptime(date, "%d/%m/%Y")
        iso_date = date_obj.strftime("%Y-%m-%d")
        iso_format_dates.append(iso_date)

    return iso_format_dates


def convert_utc_to_local(utc_dt):
    # Definir o fuso horário UTC
    utc = pytz.utc

    # Converter a data e hora UTC para um objeto datetime com fuso horário
    utc_dt = utc.localize(utc_dt)

    # Fuso horário local (exemplo: America/Sao_Paulo para Brasília)
    local_tz = pytz.timezone("America/Sao_Paulo")

    # Converter para o fuso horário local
    local_dt = utc_dt.astimezone(local_tz)

    return local_dt


def nlpBertimbau(df):

    if df.empty or len(df.columns) == 0:
        raise ValueError("DataFrame está vazio ou não possui colunas.")

    texts = []
    sentiment_dict = {sentiment: [] for sentiment in id2label.values()}
    for text in df["text"]:
        inputs = current_app.config.get("BERT_TOKENIZER")(text, return_tensors="pt")
        with torch.no_grad():
            logits = current_app.config.get("BERT_MODEL")(**inputs).logits

        normalize = lambda x, vec: 100 * (x - vec.min()) / (vec.max() - vec.min())
        normalized_logits = [normalize(element, logits) for element in logits]
        output = id2label[normalized_logits[0].argmax().item()]
        for i in range(0, len(normalized_logits[0])):
            sentiment_current = id2label[i]
            sentiment_dict[sentiment_current].append(
                round(normalized_logits[0][i].item(), 4)
            )
        texts.append(output)

    df["feeling"] = texts
    for value in id2label.values():
        df[value.lower()] = sentiment_dict[value]

    return df


def df_graph_sentiment(df):
    # contagem dos sentimentos para grafico radar
    audio_sentiment = list(df["feeling"])

    sentiment_count = {sentiment: 0 for sentiment in id2label.values()}

    for sentiment in audio_sentiment:
        if sentiment in id2label.values():
            sentiment_count[sentiment] += 1

    # criação de datafrime para grafico radar
    df_radar = pd.DataFrame(
        dict(
            Emocao=list(sentiment_count.keys()), Contagem=list(sentiment_count.values())
        )
    )

    # informações para gráfico dos sentimentos
    df_sentiment = pd.DataFrame(
        dict(
            time=list(df["time"]),
            raiva=list(df["raiva"]),
            medo=list(df["medo"]),
            tristeza=list(df["tristeza"]),
            surpresa=list(df["surpresa"]),
            alegria=list(df["alegria"]),
            nojo=list(df["nojo"]),
        )
    )

    # transformando para string
    df_sentiment["time"] = df_sentiment["time"].astype(str)

    return df_radar, df_sentiment


def model_kmeans(data, n_clusters, n_init, max_iter):
    x = data
    data["keys"] = data["keys"].fillna(0)
    data = pd.get_dummies(data)
    data = data.div(data.sum(axis=1), axis="rows")

    km = KMeans(n_clusters=n_clusters, max_iter=max_iter, n_init=n_init)
    X_t = km.fit_predict(data)

    x.loc[:, "cluster"] = X_t

    x.to_csv("Kmeans.csv", index=False)
    return


def model_meanshift(dados, n_qualite, samples):
    x = dados
    dados["keys"] = dados["keys"].fillna(0)
    dados = pd.get_dummies(dados)
    dados = dados.div(dados.sum(axis=1), axis="rows")

    bandwidth = estimate_bandwidth(dados, quantile=n_qualite, n_samples=samples)

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(dados)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    x.loc[:, "cluster"] = labels
    x.to_csv("Mean-Shift.csv", index=False)

    print(f"Número estimado de clusters: {n_clusters_}")
    return


def list_dates(dir):
    dates = []
    folders = sorted(os.listdir(dir))
    for item in folders:
        df = pd.read_csv(f"{dir}/{item}/trace.csv", encoding="iso-8859-1")
        pages = df.site.unique()
        items = item.split("-")
        items.append(pages)
        dates.append(items)
    dates = list(
        map(
            lambda time: [
                f"{time[0][6:8]}/{time[0][4:6]}/{time[0][0:4]}",
                f"{time[1][0:2]}:{time[1][2:4]}:{time[1][4:6]}",
                time[2],
                f"{time[0]}-{time[1]}",
            ],
            dates,
        )
    )
    return dates


def dirs2data(userfound, datadir):
    data = []
    for folder in userfound["data"]:
        if folder in os.listdir(datadir):
            data.append(
                {
                    "date": userfound["data"][folder]["date"],
                    "hour": userfound["data"][folder]["hour"],
                    "pages": userfound["data"][folder]["sites"],
                    "dir": folder,
                }
            )
    return data


def id_generator():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(8))


def plot_image(img, figsize_in_inches=(5, 5)):
    fig, ax = plt.subplots(figsize=figsize_in_inches)
    ax.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.show()
