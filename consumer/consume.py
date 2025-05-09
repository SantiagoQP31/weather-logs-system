"""
consumer/consume.py
Microservicio Consumer instrumentado con métricas Prometheus.
"""
import os
import json
import time
import logging
from dotenv import load_dotenv
from prometheus_client import Counter, start_http_server
import pika
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de logging
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

# Carga de .env
load_dotenv()

# RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "weather_logs")
ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "weather.station")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "weather_queue")

# PostgreSQL
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = int(os.getenv("POSTGRES_PORT", 5432))
PG_DB = os.getenv("POSTGRES_DB", "weather")
PG_USER = os.getenv("POSTGRES_USER", "weather_user")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "weather_pass")

# Métricas Prometheus
MSG_RECEIVED = Counter(
    'weather_messages_received_total', 'Total de mensajes recibidos'
)
MSG_ERRORS = Counter(
    'weather_messages_errors_total', 'Total de mensajes inválidos o con error'
)

def conectar_postgres():
    """
    Conecta a PostgreSQL con reintentos sencillos.
    """
    while True:
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                dbname=PG_DB,
                user=PG_USER,
                password=PG_PASS
            )
            conn.autocommit = False
            logging.info("Conectado a PostgreSQL")
            return conn
        except psycopg2.OperationalError as e:
            logging.error(f"Fallo al conectar a Postgres, reintentando en 3s: {e}")
            time.sleep(3)


def callback(ch, method, properties, body):
    """
    Procesa cada mensaje de RabbitMQ: valida, persiste y actualiza métricas.
    """
    try:
        data = json.loads(body)
        MSG_RECEIVED.inc()
    except json.JSONDecodeError:
        logging.error(f"JSON inválido: {body}")
        MSG_ERRORS.inc()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if not (
        -30.0 <= data.get("temperature", -1000) <= 60.0 and
        0.0 <= data.get("humidity", -1) <= 100.0 and
        700.0 <= data.get("pressure", 0) <= 1100.0
    ):
        logging.error(f"Datos fuera de rango: {data}")
        MSG_ERRORS.inc()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    conn = conectar_postgres()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO weather_logs (timestamp, station_id, temperature, humidity, pressure) VALUES (%s,%s,%s,%s,%s)",
            (data["timestamp"], data["station_id"], data["temperature"], data["humidity"], data["pressure"])
        )
        conn.commit()
        logging.info(f"Insertado en DB: {data}")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error al insertar en DB: {e}")
        MSG_ERRORS.inc()
    finally:
        cur.close()
        conn.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """
    Inicia el consumidor y servidor de métricas.
    """
    # Iniciar servidor de métricas en el puerto 8001
    start_http_server(8001)
    logging.info("Servidor de métricas del Consumer iniciado en :8001/metrics")

    # Conexión a RabbitMQ
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    # Declarar exchange y cola
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE, routing_key=ROUTING_KEY)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    logging.info("Consumer iniciado. Esperando mensajes...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
