# Imagem base oficial do Python
FROM python:3.11-slim

# Definir variáveis de ambiente para execução limpa do Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependências de sistema para compilação e leitura de formatos científicos
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código do projeto
COPY . .

# Comando padrão: executar os testes e gerar tabelas analíticas
CMD ["python", "scripts/generate_powerbi_tables.py"]
