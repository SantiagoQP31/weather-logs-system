# Guía de uso: Servicio de Alertas en Tiempo Real

Este documento explica cómo configurar, desplegar y probar el **Servicio de Alertas** que simula el envío de emails cuando los datos meteorológicos superan umbrales críticos.

---

## 1. Estructura de la carpeta `/alerter`

```
/alerter
├── alert.py           # Lógica del microservicio de alertas
├── requirements.txt   # Dependencias de Python
├── .env.example       # Variables de entorno necesarias
└── Dockerfile         # Define la imagen Docker del servicio
```

---

## 2. Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores según tu entorno:

```env
# RabbitMQ
env RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
env RABBITMQ_EXCHANGE=weather_logs
RABBITMQ_ROUTING_KEY=weather.station

# Umbrales de alerta
env TEMP_THRESHOLD=50.0      # límite de temperatura (°C)
env HUM_THRESHOLD=90.0       # límite de humedad (%)
env PRES_THRESHOLD=1050.0    # límite de presión (hPa)

# Simulación de email
env EMAIL_FROM=alerts@weather.com
env EMAIL_TO=admin@weather.com
```

---

## 3. Ejecución local

1. Sitúate en la carpeta del servicio:
   ```bash
   cd alerter
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv .venv
   \.\.venv\Scripts\Activate.ps1   # PowerShell
   # source .venv/bin/activate          # Bash/WSL
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Asegúrate de que RabbitMQ esté funcionando (puede ser local o en Docker).
5. Ejecuta el servicio:
   ```bash
   python alert.py
   ```
6. Debes ver en consola mensajes indicando que espera datos:
   ```text
   Servicio de alertas iniciado. Esperando mensajes...
   ```

---

## 4. Despliegue con Docker Compose

1. Verifica que RabbitMQ esté corriendo:
   ```bash
   docker-compose up -d rabbitmq
   ```
2. Levanta el servicio de alertas:
   ```bash
   docker-compose up --build -d alerter
   ```
3. Comprueba que el contenedor esté en estado **Up**:
   ```bash
   docker ps | grep alerter
   ```

---

## 5. Prueba de alertas

Para generar una alerta, publica un mensaje con valores críticos. Por ejemplo, usando un script local `send_test_message.py` o manualmente:

```bash
curl.exe -X POST http://localhost:8000/publish -H "Content-Type: application/json" -d "{\"station_id\":\"ST-TEST\",\"temperature\":60,\"humidity\":95,\"pressure\":1060}"
```

Luego, observa los logs del servicio de alertas:

```bash
docker logs -f alert_service
```

Deberías ver algo como:

```text
2025-05-09 12:00:00 [INFO] Simulando envío de email:
Asunto: Alerta estación ST-TEST
Temperatura crítica: 60.0 °C
Humedad crítica: 95.0 %
Presión crítica: 1060.0 hPa
```

---

*Última actualización: 2025-05-09*

