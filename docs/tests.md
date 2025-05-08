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
$ docker logs -f weather_logs_system_producer
```

**Resultado Observado:**
```bashs
$ docker logs -f weahter_logs_system_producer

2025-05-08 14:22:23,353 [INFO] Created channel=1
2025-05-08 14:22:23,354 [INFO] [1] Mensaje enviado: {"station_id": "ST-3446", "timestamp": "2025-05-08T19:22:23.354490+00:00", "temperature": 1000, "humidity": 26.25, "pressure": 729.92}
2025-05-08 14:22:24,355 [INFO] [2] Mensaje enviado: {"station_id": "ST-8887", "timestamp": "2025-05-08T19:22:24.354933+00:00", "temperature": 1000, "humidity": 81.79, "pressure": 883.13}
2025-05-08 14:22:25,356 [INFO] [3] Mensaje enviado: {"station_id": "ST-5866", "timestamp": "2025-05-08T19:22:25.355813+00:00", "temperature": 1000, "humidity": 15.24, "pressure": 951.3}
2025-05-08 14:22:26,357 [INFO] [4] Mensaje enviado: {"station_id": "ST-4023", "timestamp": "2025-05-08T19:22:26.356802+00:00", "temperature": 1000, "humidity": 83.61, "pressure": 965.04}
2025-05-08 14:22:27,357 [INFO] [5] Mensaje enviado: {"station_id": "ST-1515", "timestamp": "2025-05-08T19:22:27.357582+00:00", "temperature": 1000, "humidity": 96.46, "pressure": 952.27}
2025-05-08 14:22:28,358 [INFO] Closing connection (200): Normal shutdown
```

**Nota:** Se confirma el correcto funcionamiento de **`producer`**.

---

## 3. Consumo y Persistencia (Producer)
```bash
$ docker exec -it postgres \
  psql -U weather_user -d weather \
  -c "SELECT count(*) FROM weather_logs;"
```

**Resultado Observado:**
```bashs
$ docker logs -f weather_logs_system_consumer

2025-05-08 14:28:14,910 [INFO] Created channel=1
2025-05-08 14:28:14,973 [INFO] Conectado a PostgreSQL
2025-05-08 14:28:14,975 [INFO] Esperando mensajes. Para salir presiona CTRL+C
2025-05-08 14:28:21,044 [INFO] Insertado en DB: {'station_id': 'ST-1069', 'timestamp': '2025-05-08T19:28:21.017499+00:00', 'temperature': 35.99, 'humidity': 14.64, 'pressure': 967.2}
2025-05-08 14:28:22,023 [INFO] Insertado en DB: {'station_id': 'ST-8461', 'timestamp': '2025-05-08T19:28:22.018523+00:00', 'temperature': 11.78, 'humidity': 34.39, 'pressure': 809.62}
2025-05-08 14:28:23,027 [INFO] Insertado en DB: {'station_id': 'ST-5610', 'timestamp': '2025-05-08T19:28:23.019383+00:00', 'temperature': -16.04, 'humidity': 29.23, 'pressure': 764.48}
2025-05-08 14:28:24,027 [INFO] Insertado en DB: {'station_id': 'ST-5344', 'timestamp': '2025-05-08T19:28:24.020607+00:00', 'temperature': 30.3, 'humidity': 22.51, 'pressure': 716.99}
2025-05-08 14:28:25,025 [INFO] Insertado en DB: {'station_id': 'ST-4693', 'timestamp': '2025-05-08T19:28:25.021716+00:00', 'temperature': 41.05, 'humidity': 48.15, 'pressure': 1028.96}
2025-05-08 14:28:39,345 [INFO] Insertado en DB: {'station_id': 'ST-9115', 'timestamp': '2025-05-08T19:28:39.342003+00:00', 'temperature': -8.19, 'humidity': 38.49, 'pressure': 1018.36}
2025-05-08 14:28:40,349 [INFO] Insertado en DB: {'station_id': 'ST-5830', 'timestamp': '2025-05-08T19:28:40.342783+00:00', 'temperature': 11.27, 'humidity': 38.01, 'pressure': 882.65}
2025-05-08 14:28:41,346 [INFO] Insertado en DB: {'station_id': 'ST-8096', 'timestamp': '2025-05-08T19:28:41.343400+00:00', 'temperature': -12.0, 'humidity': 19.37, 'pressure': 950.3}
2025-05-08 14:28:42,374 [INFO] Insertado en DB: {'station_id': 'ST-3945', 'timestamp': '2025-05-08T19:28:42.343976+00:00', 'temperature': 56.17, 'humidity': 21.01, 'pressure': 959.99}
2025-05-08 14:28:43,348 [INFO] Insertado en DB: {'station_id': 'ST-3063', 'timestamp': '2025-05-08T19:28:43.345205+00:00', 'temperature': 37.55, 'humidity': 6.23, 'pressure': 1044.38}
context canceled
```

**Nota:** Se confirma el correcto funcionamiento de **`consumer`**.

---

## 4. Verificación en PostgreSQL

```bash
$ docker logs -f weather_logs_system_consumer
```

**Resultado Observado:**
```bashs
 count 
-------
    87
(1 row)
```

**Nota:** El hecho de que el contador se muestre en 87, es otra evidencia de la persistencia en la BD, manteniendo lo generado en envíos de mensajes previos.

---

## 5. Prueba de datos inválidos

1. Modificar temporalmente **`producer/send.py`** para generar varios mensajes con **`tempature = 1000`** (Dato inválido porque esta fuera del rango permitido). 
2. Volver a levantar solo el producer:
```bash
$ docker-compose up --build -d weather_logs_system_producer
```
3. Revisar logs del consumer:
```bash
$ docker logs -f weather_logs_system_consumer
```
**Resultado Observado:**
```bashs
2025-05-08 14:21:53,815 [INFO] Created channel=1
2025-05-08 14:21:53,843 [INFO] Conectado a PostgreSQL
2025-05-08 14:21:53,844 [INFO] Esperando mensajes. Para salir presiona CTRL+C
2025-05-08 14:21:54,291 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-4680', 'timestamp': '2025-05-08T19:21:54.283503+00:00', 'temperature': 1000, 'humidity': 42.54, 'pressure': 780.33}
2025-05-08 14:21:55,286 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-1865', 'timestamp': '2025-05-08T19:21:55.284817+00:00', 'temperature': 1000, 'humidity': 65.22, 'pressure': 915.17}
2025-05-08 14:21:56,286 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-2561', 'timestamp': '2025-05-08T19:21:56.285759+00:00', 'temperature': 1000, 'humidity': 23.74, 'pressure': 962.25}
2025-05-08 14:21:57,288 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-3998', 'timestamp': '2025-05-08T19:21:57.286540+00:00', 'temperature': 1000, 'humidity': 81.67, 'pressure': 1080.14}
2025-05-08 14:22:05,126 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-8891', 'timestamp': '2025-05-08T19:22:05.125171+00:00', 'temperature': 1000, 'humidity': 98.72, 'pressure': 851.35}
2025-05-08 14:22:06,126 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-1659', 'timestamp': '2025-05-08T19:22:06.125736+00:00', 'temperature': 1000, 'humidity': 70.65, 'pressure': 990.46}
2025-05-08 14:22:07,127 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-9810', 'timestamp': '2025-05-08T19:22:07.126443+00:00', 'temperature': 1000, 'humidity': 76.56, 'pressure': 1038.79}
2025-05-08 14:22:08,128 [ERROR] Datos fuera de rango o mal formados: {'station_id': 'ST-1622', 'timestamp': '2025-05-08T19:22:08.127348+00:00', 'temperature': 1000, 'humidity': 55.51, 'pressure': 1028.8}
context canceled
```

**Nota:** La consulta en postgres sigue devolviendo la misma cantidad de mensajes que se habían almacenado antes de intentar integrar esos datos inválidos. Prueba superada.
