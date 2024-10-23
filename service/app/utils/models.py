from torchvision import models
from huggingface_hub import hf_hub_download
import torch.nn as nn
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def load_bert(model_name="LPO-UFPA/bertimbau-finetuned"):
    """
    Carrega um modelo BERT finetunado e o tokenizer correspondente diretamente do Hugging Face.

    Args:
        model_name (str): O nome do modelo pré-treinado no Hugging Face Hub.

    Returns:
        tokenizer (transformers.PreTrainedTokenizer): O tokenizer do modelo carregado.
        modelBert (transformers.PreTrainedModel): O modelo BERT carregado para classificação de sequência.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    modelBert = AutoModelForSequenceClassification.from_pretrained(model_name)
    return tokenizer, modelBert


def load_fer(repo_id="LPO-UFPA/fer_uxtracking", filename="efficientnet.pth", device=None):
    """
    Carrega um modelo EfficientNet para reconhecimento de emoções faciais (FER) com pesos pré-treinados
    baixados do Hugging Face Hub. A função permite carregar o modelo para a CPU ou GPU, dependendo do dispositivo.

    Args:
        repo_id (str): O repositório no Hugging Face Hub de onde baixar os pesos do modelo.
        filename (str): O nome do arquivo de pesos a ser baixado.
        device (torch.device, opcional): O dispositivo no qual o modelo será carregado. Se não especificado,
                                         o modelo será carregado para a GPU se disponível, ou CPU por padrão.

    Returns:
        model (torch.nn.Module): O modelo EfficientNet carregado e pronto para inferência.
    """
    # Definir dispositivo como CPU ou GPU (se disponível)
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Caminho local onde o modelo será salvo
    path = "service/app/static/"
    
    # Baixar pesos do modelo via Hugging Face Hub
    fer_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=path
    )
    
    # Carregar o modelo EfficientNet sem pesos pré-treinados
    model = models.efficientnet_b0(weights=None)
    
    # Substituir a cabeça de classificação pelo classificador personalizado
    num_ftrs = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.1),
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.BatchNorm1d(512),
        nn.Dropout(0.1),
        nn.Linear(512, 8),  # Supondo 8 classes para reconhecimento de emoções
    )
    
    # Carregar os pesos do modelo treinado
    model.load_state_dict(
        torch.load(
            fer_path,
            map_location=device
        )
    )
    
    # Mover o modelo para o dispositivo especificado (CPU ou GPU)
    model.to(device)
    
    # Colocar o modelo em modo de avaliação
    model.eval()

    return model
