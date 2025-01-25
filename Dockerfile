# Imagem base do Python
FROM python:3.9-slim

# Diretório de trabalho no container
WORKDIR /app

# Copie todos os arquivos para o container
COPY . /app

# Instale dependências do sistema para Gradio e outras bibliotecas
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instale dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta padrão do Gradio
EXPOSE 7860

# Comando para rodar o aplicativo
CMD ["python", "app.py"]
