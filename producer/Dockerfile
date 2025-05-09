# producer/Dockerfile

# 1. Base image con Python 3.13
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Bogota /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# 2. Establecer directorio de trabajo
WORKDIR /app

# 3. Copiar requirements e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar resto del código
COPY send.py . 
COPY .env.example .env

# 5. Comando por defecto
CMD ["python", "send.py"]
