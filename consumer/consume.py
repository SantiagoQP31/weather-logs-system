"""
consumer/consume.py

Microservicio Consumer para el sistema de logs meteorológicos.
Recibe mensajes de RabbitMQ, valida los datos y los persiste en PostgreSQL.
"""

import os
import json
import logging
import time
import psycopg2
from dotenv import load_dotenv
import pika

# Configurar logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

# Cargar variables de entorno
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

def validar_datos(msg: dict) -> bool:
    """
    Valida que cada campo del mensaje esté dentro de los rangos permitidos.
    Retorna True si es válido, False en caso contrario.
    """
    try:
        temp = float(msg["temperature"])
        hum = float(msg["humidity"])
        pres = float(msg["pressure"])
    except (KeyError, ValueError, TypeError):
        return False

    if not (-30.0 <= temp <= 60.0):
        return False
    if not (0.0 <= hum <= 100.0):
        return False
    if not (700.0 <= pres <= 1100.0):
        return False

    return True

def conectar_postgres():
    """
    Crea y retorna una conexión a PostgreSQL con reconexión automática simple.
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

def main():
    """
    1. Conecta a RabbitMQ y PostgreSQL.
    2. Declara exchange y cola, binding.
    3. Consume mensajes con prefetch_count=1 y ack manual.
    4. Valida y persiste o descarta y loguea error.
    """
    # 1) Conexión a RabbitMQ
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # 2) Declarar exchange y cola durable
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE, routing_key=ROUTING_KEY)

    # 3) Limitar a 1 mensaje sin ack
    channel.basic_qos(prefetch_count=1)

    # 4) Conectar a Postgres
    pg_conn = conectar_postgres()
    pg_cur = pg_conn.cursor()

    def callback(ch, method, properties, body):
        """
        Función que procesa cada mensaje recibido.
        """
        try:
            msg = json.loads(body)
        except json.JSONDecodeError:
            logging.error(f"JSON inválido: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if not validar_datos(msg):
            logging.error(f"Datos fuera de rango o mal formados: {msg}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Insertar en la base
        try:
            pg_cur.execute(
                """
                INSERT INTO weather_logs (timestamp, station_id, temperature, humidity, pressure)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (msg["timestamp"], msg["station_id"], msg["temperature"],
                 msg["humidity"], msg["pressure"])
            )
            pg_conn.commit()
            logging.info(f"Insertado en DB: {msg}")
        except Exception as e:
            pg_conn.rollback()
            logging.error(f"Error al insertar en DB: {e} | msg: {msg}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    # 5) Iniciar consumo
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    logging.info("Esperando mensajes. Para salir presiona CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()