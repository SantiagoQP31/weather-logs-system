"""
alerter/alert.py
Microservicio que detecta valores críticos en datos meteorológicos
y simula el envío de emails cuando un umbral es superado.
"""
import os
import json
import logging
from email.message import EmailMessage
from dotenv import load_dotenv
import pika
import time

# Configuración de logging
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

# Carga de variables de entorno
load_dotenv()

# Parámetros de RabbitMQ
tmp = os.getenv
RABBITMQ_HOST = tmp("RABBITMQ_HOST")
RABBITMQ_PORT = int(tmp("RABBITMQ_PORT"))
EXCHANGE = tmp("RABBITMQ_EXCHANGE")
ROUTING_KEY = tmp("RABBITMQ_ROUTING_KEY")

# Umbrales de alerta (límites críticos)
TEMP_THRESHOLD = float(tmp("TEMP_THRESHOLD"))
HUM_THRESHOLD = float(tmp("HUM_THRESHOLD"))
PRES_THRESHOLD = float(tmp("PRES_THRESHOLD"))

# Parámetros de simulación de email
EMAIL_FROM = tmp("EMAIL_FROM")
EMAIL_TO = tmp("EMAIL_TO")
SMTP_SERVER = tmp("SMTP_SERVER", "localhost")
SMTP_PORT = int(tmp("SMTP_PORT", 25))

def connect_rabbit():
    """Intenta conectar a RabbitMQ hasta que funcione"""
    while True:
        try:
            params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
            return pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError:
            logging.warning("RabbitMQ no disponible, reintentando en 3 s…")
            time.sleep(3)

def send_email(subject: str, body: str):
    """
    Simula el envío de un email usando EmailMessage.
    Solo registra en el log el sujeto y el contenido.

    Args:
        subject (str): Asunto del email de alerta.
        body (str): Cuerpo del mensaje con detalles de la alerta.
    """
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    # Simulación: imprimir en log
    logging.info(f"Simulando envío de email: {subject}, {body}")


def callback(ch, method, properties, body):
    """
    Procesa cada mensaje recibido de RabbitMQ.
    Valida los valores de temperatura, humedad y presión,
    y envía una alerta si alguno excede su umbral.

    Args:
        ch: Canal de RabbitMQ.
        method: Métodos de entrega del mensaje.
        properties: Propiedades del mensaje.
        body (bytes): Contenido del mensaje JSON.
    """
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        logging.error(f"JSON inválido: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    station = data.get("station_id")
    temp = data.get("temperature")
    hum = data.get("humidity")
    pres = data.get("pressure")

    alerts = []
    if temp is not None and temp > TEMP_THRESHOLD:
        alerts.append(f"Temperatura crítica: {temp} °C")
    if hum is not None and hum > HUM_THRESHOLD:
        alerts.append(f"Humedad crítica: {hum} %")
    if pres is not None and pres > PRES_THRESHOLD:
        alerts.append(f"Presión crítica: {pres} hPa")

    if alerts:
        subject = f"Alerta estación {station}"
        body_msg = "Se ha reportado una alerta en la estación establecida. Es necesario su atención inmediata.".join(alerts)
        send_email(subject, body_msg)

    # Confirmar procesamiento del mensaje
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """
    Función principal del servicio de alertas.
    1. Conecta a RabbitMQ.
    2. Declara exchange y queue de alertas.
    3. Comienza a consumir mensajes con prefetch_count=1.
    """
    # Conexión a RabbitMQ\    
    params = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
    conn = pika.BlockingConnection(params)
    channel = conn.channel()

    # Declarar exchange y cola
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue="alerts_queue", durable=True)
    channel.queue_bind(queue="alerts_queue", exchange=EXCHANGE, routing_key=ROUTING_KEY)

    # Procesar un mensaje a la vez
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="alerts_queue", on_message_callback=callback)

    logging.info("Servicio de alertas iniciado. Esperando mensajes...")
    channel.start_consuming()


if __name__ == "__main__":
    main()