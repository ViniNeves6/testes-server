import pandas as pd
from bson import ObjectId
from datetime import datetime
from collections import Counter
from app.utils.functions import convert_utc_to_local


def userdata2frame(mongo_db, collection_name, id, data_type):
    """
    Extrai dados de interações do MongoDB e os organiza em um DataFrame.

    Parâmetros:
    -----------
    mongo_db : pymongo.database.Database
        Instância do banco de dados MongoDB.
    collection_name : str
        Nome da coleção onde os dados estão armazenados.
    id : str
        ID do documento a ser consultado.
    data_type : list ou str
        Tipo de dados de interação a serem extraídos. Pode ser uma lista de tipos ou uma string
        indicando um tipo específico ('voice', 'face', etc.).

    Retorna:
    --------
    pd.DataFrame
        DataFrame contendo as interações filtradas com as colunas apropriadas.
        df: site,image,type,time,class,id,x,y,scroll,height,keys

    Descrição:
    ----------
    A função realiza os seguintes passos:
    1. Define as colunas básicas para o DataFrame.
    2. Extende as colunas com campos específicos dependendo do tipo de dados de interação.
    3. Cria um pipeline de agregação para:
        a. Filtrar o documento pelo ID fornecido.
        b. Desagregar o array de 'data'.
        c. Projetar campos necessários e filtrar as interações com base no tipo fornecido.
        d. Remover subdocumentos que não possuem interações.
    4. Executa o pipeline no MongoDB e coleta os registros resultantes.
    5. Itera sobre os registros, organizando os dados em um formato adequado.
    6. Cria um DataFrame a partir dos dados organizados e retorna o DataFrame.
    """

    # Definindo as colunas básicas
    keys = [
        "site",
        "image",
        "type",
        "time",
        "class",
        "id",
        "x",
        "y",
        "scroll",
        "height",
    ]

    # Extendendo com campos específicos de interação
    if isinstance(data_type, list):
        keys.append("keys")
    elif data_type == "voice":
        data_type = [data_type]
        keys.append("text")
    elif data_type == "face":
        data_type = [data_type]
        keys.extend(
            [
                "anger",
                "contempt",
                "disgust",
                "fear",
                "happy",
                "neutral",
                "sad",
                "surprise",
            ]
        )

    pipeline = [
        {"$match": {"_id": ObjectId(id)}},  # Filtra pelo ID do documento
        {"$unwind": "$data"},  # Desagrega o array 'data'
        {
            "$project": {  # Projetar campos necessários e filtrar interações
                "site": "$data.site",
                "images": "$data.images",
                "interactions": {
                    "$filter": {
                        "input": "$data.interactions",
                        "as": "interaction",
                        "cond": {"$in": ["$$interaction.type", data_type]},
                    }
                },
            }
        },
        {
            "$match": {"interactions.0": {"$exists": True}}
        },  # Remove subdocumentos com interações vazias
    ]

    cursor = mongo_db[collection_name].aggregate(pipeline)
    records_list = list(cursor)

    all_data = []

    for record in records_list:
        site = record.get("site")
        for interaction in record.get("interactions", []):
            line = {
                "site": site,
                "type": interaction.get("type"),
                "image": interaction.get("image"),
                "time": interaction.get("time"),
                "class": interaction.get("class"),
                "id": interaction.get("id"),
                "x": interaction.get("x"),
                "y": interaction.get("y"),
                "scroll": interaction.get("scroll"),
                "height": interaction.get("height"),
            }
            # Tratando o campo value
            value_data = interaction.get("value", {})
            if isinstance(value_data, dict):
                line.update(value_data)

            all_data.append(line)

    # Criando DataFrame de uma vez
    df = pd.DataFrame(all_data, columns=keys)
    return df


def userdata_summary(documents):
    """
    Gera um resumo dos dados de interações a partir de uma lista de documentos do MongoDB.

    Parâmetros:
    -----------
    documents : list
        Lista de documentos do MongoDB, onde cada documento contém informações de interação.

    Retorna:
    --------
    tuple
        Uma tupla contendo:
        - data : list of dict
            Lista de dicionários com informações resumidas de cada documento.
            Cada dicionário contém os campos:
            - id : ObjectId
                ID do documento.
            - date : str
                Data da interação no formato 'dd/mm/yyyy'.
            - time : datetime.time
                Hora da interação.
            - sites : list
                Lista de sites presentes no documento.
        - date_counts : collections.Counter
            Contador com o número de ocorrências de cada data.
    """

    data = []
    date_arr = []
    for doc in documents:
        try:
            # Obtenha a string de data e hora do documento
            date_str = doc["datetime"]

            # Converter para data e hora
            date_obj = datetime.fromisoformat(date_str.rstrip("Z"))

            #converte UTC para horário local
            local_date_obj = convert_utc_to_local(date_obj)

            date_part = local_date_obj.date().strftime("%d/%m/%Y")
            time_part = local_date_obj.time().strftime("%H:%M:%S")

            date_arr.append(date_part)
            # Criando o objeto data com todas as informações da coleta
            data.append(
                {
                    "id": doc["_id"],  # id do documento
                    "date": date_part,  # data do documento
                    "time": time_part,  # hora do documento
                    "sites": doc["sites"],  # sites presentes no documento
                }
            )

        except Exception as e:
            print(f"Error processing document {doc['_id']}: {e}")

    # Contar as ocorrências de cada data
    date_counts = Counter(date_arr)

    return data, date_counts


def remove_non_utf8(df):
    """
    Remove caracteres que não são UTF-8 de um DataFrame.

    Parâmetros:
    df (pandas.DataFrame): O DataFrame a ser processado.

    Retorna:
    pandas.DataFrame: Um novo DataFrame com todos os caracteres não UTF-8 removidos ou ignorados.
    """

    def safe_str(x):
        """
        Tenta converter um valor para uma string UTF-8 válida, removendo caracteres não UTF-8.

        Parâmetros:
        x: O valor a ser convertido.

        Retorna:
        str: Uma string UTF-8 válida ou uma string vazia se a conversão falhar.
        """
        try:
            return str(x).encode('utf-8', errors='ignore').decode('utf-8')
        except:
            return ''

    # Aplica a função safe_str a todos os elementos do DataFrame
    return df.applymap(safe_str)