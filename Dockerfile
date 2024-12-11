# Use a base image for Python
FROM python:3.11

# Define o diretório de trabalho
WORKDIR /app

# Install dependencies required for OpenCV
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt requirements.txt
    
# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo da aplicação para o diretório de trabalho
COPY . .

ENV PYTHONPATH=/app
