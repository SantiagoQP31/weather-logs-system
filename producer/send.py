"""
producer/send.py
Microservicio Producer instrumentado con métricas Prometheus.
"""
import os
import json
import time
import logging
import random
from datetime import datetime, timezone
from dotenv import load_dotenv
from prometheus_client import Counter, Summary, start_http_server
import pika

# Configuración de logging
t_logging = logging.basicConfig
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

# Carga de .env
load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "weather_logs")
ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "weather.station")

# Métricas Prometheus
MSG_SENT = Counter(
    'weather_messages_sent_total', 'Total de mensajes enviados'
)
SEND_LATENCY = Summary(
    'weather_send_latency_seconds', 'Latencia de envío de mensajes'
)


def generar_datos_estacion():
    """
    Genera un diccionario con datos simulados de una estación meteorológica.

    Campos:
    
    station_id: Identificador aleatorio de estación ("ST-1234").
    timestamp: Fecha y hora actual en ISO 8601 UTC (ej. "2025-05-07T19:00:00Z").
    temperature: Temperatura en °C, rango [-30.00, 60.00].
    humidity: Humedad relativa en %, rango [0.00, 100.00].
    pressure: Presión atmosférica en hPa, rango [700.00, 1100.00].

    Retorna:
        dict: Datos de la estación listos para serializar a JSON.
    """
    return {
        "station_id": f"ST-{random.randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(random.uniform(-30.0, 60.0), 2),
        "humidity": round(random.uniform(0.0, 100.0), 2),
        "pressure": round(random.uniform(700.0, 1100.0), 2)
    }


def main():
    """
    Función principal: expone métricas, conecta a RabbitMQ y envía mensajes.
    """
    # Iniciar servidor de métricas en el puerto 8000
    start_http_server(8000)
    logging.info("Servidor de métricas de Producer iniciado en :8000/metrics")

    # Conexión a RabbitMQ
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    # Declarar exchange durable
    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="direct",
        durable=True
    )

    # Enviar mensajes de prueba
    for i in range(5):
        msg = generar_datos_estacion()
        body = json.dumps(msg)
        with SEND_LATENCY.time():
            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        MSG_SENT.inc()
        logging.info(f"[{i+1}] Mensaje enviado: {body}")
        time.sleep(1)

    conn.close()


if __name__ == "__main__":
    main()