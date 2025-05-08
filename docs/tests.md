# Pruebas End-to-End (E2E)

Este documento resume las pruebas que confirman el flujo completo **Producer → RabbitMQ → Consumer → PostgreSQL**.

---

## 1. Reinicio limpio del entorno

```bash
$ docker-compose down
$ docker-compose up --build -d
```

**Resultado Observado:**
```bash
$ docker ps
CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS                         PORTS                                                                                                            NAMES
b2a64164b946   weather-logs-system-consumer   "python consume.py"      20 seconds ago   Up 6 seconds                                                                                                      weather_logs_system_consumer
63b7fa95d60f   weather-logs-system-producer   "python send.py"         20 seconds ago   Restarting (1) 6 seconds ago                                                                                     weather_logs_system_producer
98cbb74644ab   postgres:15                    "docker-entrypoint.s…"   20 seconds ago   Up 19 seconds                  0.0.0.0:5432->5432/tcp                                                           weather_logs_system_postgres
dc16b7fcd0a0   rabbitmq:3.11-management       "docker-entrypoint.s…"   20 seconds ago   Up 19 seconds                  4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, 15671/tcp, 15691-15692/tcp, 25672/tcp, 0.0.0.0:15672->15672/tcp   weather_logs_system_rabbitmq
```

**Estado de contenedores (`docker ps`)**

| CONTAINER ID | IMAGE                         | COMMAND                | CREATED         | STATUS                         | PORTS                                                                                                         | NAMES                          |
|--------------|-------------------------------|------------------------|------------------|----------------------------------|---------------------------------------------------------------------------------------------------------------|--------------------------------|
| b2a64164b946 | weather-logs-system-consumer  | "python consume.py"   | 20 seconds ago  | Up 6 seconds                    |                                                                                                               | weather_logs_system_consumer  |
| 63b7fa95d60f | weather-logs-system-producer  | "python send.py"      | 20 seconds ago  | Restarting (1) 6 seconds ago    |                                                                                                               | weather_logs_system_producer  |
| 98cbb74644ab | postgres:15                   | "docker-entrypoint…"  | 20 seconds ago  | Up 19 seconds                   | 0.0.0.0:5432->5432/tcp                                                                                        | weather_logs_system_postgres  |
| dc16b7fcd0a0 | rabbitmq:3.11-management      | "docker-entrypoint…"  | 20 seconds ago  | Up 19 seconds                   | 4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, 15671/tcp, 15691-15692/tcp, 25672/tcp, 0.0.0.0:15672->15672/tcp | weather_logs_system_rabbitmq  |

---

## 2. Publicación de mensajes (Producer)

```bash
$ docker logs -f producer
```

**Resultado Observado:**
```bash
$  docker logs -f weahter_logs_system_consumer

2025-05-08 14:22:23,353 [INFO] Created channel=1
2025-05-08 14:22:23,354 [INFO] [1] Mensaje enviado: {"station_id": "ST-3446", "timestamp": "2025-05-08T19:22:23.354490+00:00", "temperature": 1000, "humidity": 26.25, "pressure": 729.92}
2025-05-08 14:22:24,355 [INFO] [2] Mensaje enviado: {"station_id": "ST-8887", "timestamp": "2025-05-08T19:22:24.354933+00:00", "temperature": 1000, "humidity": 81.79, "pressure": 883.13}
2025-05-08 14:22:25,356 [INFO] [3] Mensaje enviado: {"station_id": "ST-5866", "timestamp": "2025-05-08T19:22:25.355813+00:00", "temperature": 1000, "humidity": 15.24, "pressure": 951.3}
2025-05-08 14:22:26,357 [INFO] [4] Mensaje enviado: {"station_id": "ST-4023", "timestamp": "2025-05-08T19:22:26.356802+00:00", "temperature": 1000, "humidity": 83.61, "pressure": 965.04}
2025-05-08 14:22:27,357 [INFO] [5] Mensaje enviado: {"station_id": "ST-1515", "timestamp": "2025-05-08T19:22:27.357582+00:00", "temperature": 1000, "humidity": 96.46, "pressure": 952.27}
2025-05-08 14:22:28,358 [INFO] Closing connection (200): Normal shutdown
```

**Nota:** Se confirma el correcto funcionamiento de `producer`.
