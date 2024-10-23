import io
import base64
from PIL import Image
from flask import current_app as app

def create_blank_image_base64():
    """
    Cria uma imagem em branco (branca) e a codifica em base64.

    Retorna:
    --------
    str
        Uma string contendo a imagem codificada em base64 no formato apropriado para uso em HTML.

    Descrição:
    ----------
    A função realiza os seguintes passos:
    1. Cria uma nova imagem em branco com dimensões 100x100 pixels e cor branca.
    2. Salva a imagem em um buffer de bytes no formato PNG.
    3. Codifica o conteúdo do buffer de bytes em base64.
    4. Retorna a string codificada em base64 no formato 'data:image/png;base64,<base64_data>'.
    """

    blank_image = Image.new(
        "RGB", (100, 100), color="white"
    )  # Cria uma imagem branca 100x100
    buffered = io.BytesIO()
    blank_image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return "data:image/png;base64," + img_base64


def generate_trace_recording(df_trace):
    """
    Cria uma gravação dos frames e define os ícones para tipos de interação a partir de um DataFrame de traços.

    Parâmetros:
    df_trace (DataFrame): DataFrame contendo os traços de navegação. Deve incluir colunas como "site", "image", "scroll" e "height".

    Retorna:
    tuple: Um tuplo contendo:
        - full_ims: Imagem composta de página inteira gerada a partir dos frames.
        - type_icon: Dicionário mapeando tipos de interação para ícones específicos.
    """

    # Obtém o ID da imagem da primeira linha do dataframe df_trace
    id_im = df_trace["image"][0]
    
    # Lê a imagem do sistema de arquivos usando o ID obtido
    im = app.fs.get(id_im).read()

    # Abre a imagem usando a biblioteca PIL e obtém suas dimensões
    with Image.open(io.BytesIO(im)) as im:
        width, height = im.size

    # Inicializa um dicionário para armazenar os frames por site
    frames = {}

    # Agrupa o dataframe por "site" e processa cada grupo separadamente
    for site, group in df_trace.groupby("site"):
        # Obtém os IDs únicos das imagens para o grupo atual
        images = group["image"].unique()
        frames[site] = {}
        for frame in images:
            # Encontra o índice da primeira ocorrência da imagem no grupo
            id0 = group[group["image"] == frame].index[0]
            # Obtém as colunas "scroll" e "height" para essa ocorrência
            columns = group.loc[id0, ["scroll", "height"]]
            # Armazena essas informações no dicionário frames
            frames[site][frame] = columns.to_dict()

    # Gera uma imagem de página inteira a partir dos frames
    full_ims = gen_fullpage(width, height, frames)

    # Define ícones para cada tipo de interação (referência: https://plotly.com/python/marker-style/)
    type_icon = {
        "freeze": "hourglass",
        "eye": "circle-open",
        "click": "x",
        "mousemove": "circle",
        "wheel": "diamond-tall-dot",
        "keyboard": "hash",
    }

    return full_ims, type_icon


def gen_fullpage(width, height, frames):
    """
    Gera uma imagem completa para cada site a partir de uma série de capturas de tela.

    Args:
        width (int): A largura da imagem composta.
        height (int): A altura inicial da imagem composta.
        frames (dict): Um dicionário onde as chaves são os nomes dos sites e os valores são dicionários.
                       Cada dicionário contém chaves para cada imagem de uma captura de tela e valores que são
                       dicionários contendo informações sobre a posição de rolagem (scroll).

    Returns:
        dict: Um dicionário onde as chaves são os nomes dos sites e os valores são as imagens completas geradas.
    """

    # Dicionário para armazenar as imagens completas geradas
    full_ims = {}

    # Itera sobre cada site e suas respectivas imagens de captura de tela
    for site, image in frames.items():
        # Calcula a altura total necessária para a imagem composta
        height_full = int(height + max(item["scroll"] for item in image.values()))
        
        # Cria uma nova imagem em branco com a largura especificada e a altura calculada
        compose_im = Image.new("RGB", (width, height_full), "white")

        # Itera sobre cada imagem e suas informações de posição de rolagem
        for image_name, item in image.items():
            try:
                # Lê os dados da imagem do sistema de arquivos
                img_data = app.fs.get(image_name).read()
                
                # Abre a imagem a partir dos dados em bytes
                with Image.open(io.BytesIO(img_data)) as img:
                    # Cola a imagem na posição correta na imagem composta
                    compose_im.paste(img, (0, int(item["scroll"])))
            except:
                # Ignora quaisquer erros que ocorram ao processar a imagem
                pass

        # Armazena a imagem completa no dicionário full_ims
        full_ims[site] = compose_im

    # Retorna o dicionário contendo todas as imagens completas geradas
    return full_ims