# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copie os arquivos do projeto para o diretório de trabalho
COPY . /app

# Instale as dependências do sistema necessárias para algumas bibliotecas
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta padrão usada pelo Gradio
EXPOSE 7860

# Comando para rodar o aplicativo
CMD ["python", "app.py"]
