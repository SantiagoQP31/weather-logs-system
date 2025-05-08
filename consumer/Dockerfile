# consumer/Dockerfile

# 1. Imagen base con Python 3.13
FROM python:3.13-slim

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
