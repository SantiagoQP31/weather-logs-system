# Guía de uso: API REST con FastAPI

Este documento explica detalladamente la creación, despliegue y uso de la API REST para consultar logs históricos y generar reportes estadísticos.

---

## 1. Estructura de la carpeta `/api`

```
/api
├── Dockerfile           # Define la imagen Docker de la API
├── main.py              # Lógica de FastAPI: endpoints y modelos
├── requirements.txt     # Dependencias del proyecto
└── .env.example         # Variables de entorno de configuración
```

---

## 2. Configuración local

1. **Clona y entra en la carpeta**
   ```bash
   cd weather-logs-system/api
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1   # PowerShell
   # source .venv/bin/activate      # Bash/WSL
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env # Linux/macOS
   ```
   Edita `.env` si usas Postgres o puertos distintos.

---

## 3. Variables de entorno

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=weather
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=weather_pass
API_HOST=0.0.0.0
API_PORT=8000
``` 

---

## 4. Endpoints disponibles

### 4.1 Obtener logs históricos

```
GET /logs
```
**Parámetros opcionales:**
- `station_id`  (string)
- `since`       (ISO 8601)
- `until`       (ISO 8601)

**Ejemplo:**
```bash
curl "http://localhost:8000/logs?station_id=ST-1234&since=2025-05-01T00:00Z"
```


### 4.2 Reporte estadístico JSON

```
GET /reports/summary
```
**Retorna:** objeto con promedio, mínimos, máximos y total de lecturas.

**Ejemplo:**
```bash
curl "http://localhost:8000/reports/summary?since=2025-05-01T00:00Z&until=2025-05-08T00:00Z"
```


### 4.3 Exportar reporte a CSV

```
GET /reports/summary/csv
```
**Ejemplo:**
```bash
curl -o resumen.csv "http://localhost:8000/reports/summary/csv"
```

### 4.4 Exportar reporte a PDF

```
GET /reports/summary/pdf
```
**Ejemplo:**
```bash
curl -o resumen.pdf "http://localhost:8000/reports/summary/pdf"
```

---

## 5. Despliegue con Docker Compose

1. Asegúrate de tener corriendo Postgres:
   ```bash
   docker-compose up -d postgres
   ```
2. Construye y arranca la API:
   ```bash
   docker-compose up --build -d api
   ```
3. Verifica estado:
   ```bash
   docker ps | grep api
   ```
4. Accede a la documentación Swagger UI en:
   ```
   http://localhost:8000/docs
   ```

---

## 6. Pruebas y ejemplos

- Navega a `/docs` para probar interactivamente.
- Usa `curl` o Postman para llamar a cada endpoint.

---

## 7. Archivos de ejemplo

Aquí puedes ver ejemplos reales de los archivos generados por la API:

- 📄 [Resumen en CSV](./examples/resumen.csv)
- 📄 [Resumen en PDF](./examples/resumen.pdf)

Estos archivos fueron generados usando los endpoints `/reports/summary/csv` y `/reports/summary/pdf`, respectivamente.

---

*Última actualización: 2025-05-08*

