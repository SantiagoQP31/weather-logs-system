"""
producer/send.py

Microservicio Producer para el sistema de logs meteorológicos.
Genera datos simulados de estaciones y los publica en RabbitMQ.
"""

import os
import json
import random
import time
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
import pika

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

# Carga de variables de entorno desde .env
load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "weather_logs")
ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "weather.station")


def generar_datos_estacion():
    """
    Genera un diccionario con datos simulados de una estación meteorológica.

    Campos:
    - station_id: Identificador aleatorio de estación ("ST-1234").
    - timestamp: Fecha y hora actual en ISO 8601 UTC (ej. "2025-05-07T19:00:00Z").
    - temperature: Temperatura en °C, rango [-30.00, 60.00].
    - humidity: Humedad relativa en %, rango [0.00, 100.00].
    - pressure: Presión atmosférica en hPa, rango [700.00, 1100.00].

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
    Función principal del script.

    1. Se conecta a RabbitMQ usando parámetros de entorno.
    2. Declara un exchange durable de tipo 'direct'.
    3. Publica 5 mensajes de prueba, uno por segundo.
    4. Cierra la conexión al terminar.
    """
    # Establecer conexión y canal
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    # Declarar exchange durable
    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="direct",
        durable=True
    )

    # Envío de mensajes
    for i in range(5):
        msg = generar_datos_estacion()
        body = json.dumps(msg)

        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)  # mensaje persistente
        )
        logging.info(f"[{i+1}] Mensaje enviado: {body}")
        time.sleep(1)

    conn.close()


if __name__ == "__main__":
    main()
