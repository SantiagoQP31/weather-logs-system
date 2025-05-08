# Pruebas End-to-End (E2E)

Este documento resume las pruebas que confirman el flujo completo **Producer → RabbitMQ → Consumer → PostgreSQL**.

---

## 1. Reinicio limpio del entorno

```bash
docker-compose down
docker-compose up --build -d
```

**Resultado Observado:**
```bash
$ docker ps
```
### Estado de contenedores (`docker ps`)

| CONTAINER ID | IMAGE                         | COMMAND                | CREATED         | STATUS                         | PORTS                                                                                                         | NAMES                          |
|--------------|-------------------------------|------------------------|------------------|----------------------------------|---------------------------------------------------------------------------------------------------------------|--------------------------------|
| b2a64164b946 | weather-logs-system-consumer  | "python consume.py"   | 20 seconds ago  | Up 6 seconds                    |                                                                                                               | weather_logs_system_consumer  |
| 63b7fa95d60f | weather-logs-system-producer  | "python send.py"      | 20 seconds ago  | Restarting (1) 6 seconds ago    |                                                                                                               | weather_logs_system_producer  |
| 98cbb74644ab | postgres:15                   | "docker-entrypoint…"  | 20 seconds ago  | Up 19 seconds                   | 0.0.0.0:5432->5432/tcp                                                                                        | weather_logs_system_postgres  |
| dc16b7fcd0a0 | rabbitmq:3.11-management      | "docker-entrypoint…"  | 20 seconds ago  | Up 19 seconds                   | 4369/tcp, 5671/tcp, 0.0.0.0:5672->5672/tcp, 15671/tcp, 15691-15692/tcp, 25672/tcp, 0.0.0.0:15672->15672/tcp | weather_logs_system_rabbitmq  |


