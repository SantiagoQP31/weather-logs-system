# 1. Imagen base
FROM python:3.13-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar código
COPY .env.example .env
COPY main.py .

# 5. Exponer puerto
EXPOSE 8000

# 6. Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]