"""
api/main.py
Microservicio API REST para consultar logs meteorológicos y generar reportes.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

# Cargar .env
load_dotenv()

# Configuración de la base de datos
DB_PARAMS = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

# Inicializar FastAPI
app = FastAPI(title="Weather Logs API")

# Modelos Pydantic
class WeatherLog(BaseModel):
    id: int
    timestamp: str
    station_id: str
    temperature: float
    humidity: float
    pressure: float

class SummaryReport(BaseModel):
    station_id: Optional[str]
    from_ts: Optional[str]
    to_ts: Optional[str]
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    min_humidity: float
    max_humidity: float
    avg_pressure: float
    min_pressure: float
    max_pressure: float
    total_readings: int

# Utils: conectar a Postgres
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a la base de datos: {e}")

# Ruta para obtener logs históricos
@app.get("/logs", response_model=List[WeatherLog])
def get_logs(
    station_id: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    query = "SELECT id, timestamp, station_id, temperature, humidity, pressure FROM weather_logs"
    filters = []
    params = []

    if station_id:
        filters.append("station_id = %s")
        params.append(station_id)
    if since:
        filters.append("timestamp >= %s")
        params.append(since)
    if until:
        filters.append("timestamp <= %s")
        params.append(until)
    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY timestamp DESC LIMIT 1000"

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

# Ruta para generar reporte estadístico
@app.get("/reports/summary", response_model=SummaryReport)
def get_summary(
    station_id: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    filters = []
    params = []

    if station_id:
        filters.append("station_id = %s")
        params.append(station_id)
    if since:
        filters.append("timestamp >= %s")
        params.append(since)
    if until:
        filters.append("timestamp <= %s")
        params.append(until)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    summary_query = f"""
        SELECT
            AVG(temperature)   AS avg_temperature,
            MIN(temperature)   AS min_temperature,
            MAX(temperature)   AS max_temperature,
            AVG(humidity)      AS avg_humidity,
            MIN(humidity)      AS min_humidity,
            MAX(humidity)      AS max_humidity,
            AVG(pressure)      AS avg_pressure,
            MIN(pressure)      AS min_pressure,
            MAX(pressure)      AS max_pressure,
            COUNT(*)           AS total_readings
        FROM weather_logs
        {where_clause}
    """

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(summary_query, params)
    row = cur.fetchone()
    cur.close()
    conn.close()

    return SummaryReport(
        station_id=station_id,
        from_ts=since,
        to_ts=until,
        avg_temperature=row['avg_temperature'],
        min_temperature=row['min_temperature'],
        max_temperature=row['max_temperature'],
        avg_humidity=row['avg_humidity'],
        min_humidity=row['min_humidity'],
        max_humidity=row['max_humidity'],
        avg_pressure=row['avg_pressure'],
        min_pressure=row['min_pressure'],
        max_pressure=row['max_pressure'],
        total_readings=row['total_readings']
    )

# Exportación a CSV
@app.get("/reports/summary/csv")
def get_summary_csv(
    station_id: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    """
    Genera un CSV con los datos del reporte estadístico.
    """
    report = get_summary(station_id, since, until)
    import io, csv
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["station_id", "from_ts", "to_ts", "avg_temperature", "min_temperature", "max_temperature", "avg_humidity", "min_humidity", "max_humidity", "avg_pressure", "min_pressure", "max_pressure", "total_readings"])
    writer.writerow([
        report.station_id,
        report.from_ts,
        report.to_ts,
        report.avg_temperature,
        report.min_temperature,
        report.max_temperature,
        report.avg_humidity,
        report.min_humidity,
        report.max_humidity,
        report.avg_pressure,
        report.min_pressure,
        report.max_pressure,
        report.total_readings
    ])
    buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buffer, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=summary_report.csv"})

# Exportación a PDF
@app.get("/reports/summary/pdf")
def get_summary_pdf(
    station_id: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    """
    Genera un PDF con los datos del reporte estadístico.
    """
    report = get_summary(station_id, since, until)
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text = c.beginText(40, 750)
    text.textLine("Summary Report")
    for field, value in report.dict().items():
        text.textLine(f"{field}: {value}")
    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=summary_report.pdf"})