# consumer/Dockerfile

# 1. Imagen base con Python 3.13
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Bogota /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# 2. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código del consumer
COPY consume.py .
COPY .env.example .env

# 5. Comando por defecto
CMD ["python", "consume.py"]
