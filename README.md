# Weather Logs System

**Proyecto completo de gestión de logs de estaciones meteorológicas**

## 📋 Contenido del repositorio

```
/producer              # Microservicio que genera y envía datos a RabbitMQ (metrics + persistencia)
/consumer              # Microservicio que consume datos de RabbitMQ y persiste en PostgreSQL (metrics)
/alerter               # Microservicio de alertas en tiempo real (simula envío de emails)
/api                   # API REST con FastAPI para consultar logs y generar reportes (JSON, CSV, PDF)
/rabbitmq              # Configuración de RabbitMQ (definitions.json)
/postgres              # Script de inicialización de PostgreSQL (init_db.sql)
/prometheus            # Configuración de Prometheus (prometheus.yml)
/docs                  # Documentación del proyecto
  ├── contract.md       # Contrato de mensajes JSON y validación
  ├── tests.md          # Pruebas End-to-End documentadas
  ├── architecture.md   # Diagrama ASCII de arquitectura
  ├── api_guide.md      # Guía de uso de la API REST
  ├── alerter.md        # Guía de uso del servicio de alertas
  ├── monitoring.md     # Monitorización con Prometheus y Grafana
  └── images/           # Capturas y diagramas exportados (Draw.io, dashboards, ejemplos CSV/PDF)

docker-compose.yml     # Orquestación Docker para todos los servicios
README.md              # Documentación principal y enlaces a secciones clave
```

---

## 🚀 Despliegue rápido

1. Clonar el repositorio:

   ```bash
   git clone git@github.com:TU_USUARIO/weather-logs-system.git
   cd weather-logs-system
   ```

2. Levantar todos los servicios con Docker Compose:

   ```bash
   docker-compose up --build -d
   ```

3. Verificar estado de contenedores:

   ```bash
   docker ps
   ```

4. Acceder a RabbitMQ:

   * URL: [http://localhost:15672](http://localhost:15672)
   * Usuario: `guest` / Contraseña: `guest`

5. Acceder a Grafana:

   * URL: [http://localhost:3000](http://localhost:3000)
   * Usuario: `admin` / Contraseña: `admin`

6. Acceder a Prometheus:

   * URL: [http://localhost:9090](http://localhost:9090)

---

## 🛠 Estructura de Microservicios

### Producer

* **Carpeta:** `/producer`
* **Función:** Genera datos aleatorios de estaciones y los envía al exchange de RabbitMQ. Exporta métricas en `/metrics` (puerto 8000).
* **Ejecutar localmente:**

  ```bash
  cd producer
  py -3 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  copy .env.example .env
  python send.py
  ```

### Consumer

* **Carpeta:** `/consumer`
* **Función:** Consume mensajes, valida rangos y persiste en PostgreSQL. Exporta métricas en `/metrics` (puerto 8001).
* **Ejecutar localmente:**

  ```bash
  cd consumer
  py -3 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  copy .env.example .env
  python consume.py
  ```

---

## 📖 Documentación adicional

* **Contrato de Mensajes**: Formato JSON, rangos de validación y reglas de error.
  ➡️ [docs/contract.md](docs/contract.md)

* **Pruebas End-to-End**: Pasos, comandos, resultados esperados y observados.
  ➡️ [docs/tests.md](docs/tests.md)

* **Diagrama de Arquitectura**: Flujo Producer → RabbitMQ → Consumer → PostgreSQL.
  ➡️ [docs/architecture.md](docs/architecture.md)

* **API REST**: Consulta logs y reportes (JSON, CSV, PDF).
  ➡️ [docs/api\_guide.md](docs/api_guide.md)

* **Servicio de Alertas**: Alerta en tiempo real por email simulado.
  ➡️ [docs/alerts\_guide.md](docs/alerts_guide.md)

* **Monitorización**: Métricas con Prometheus y dashboards en Grafana.
  ➡️ [docs/monitoring.md](docs/monitoring.md)

---

## 📂 Carpetas y Archivos Clave

| Elemento                    | Descripción                                                    |
| --------------------------- | -------------------------------------------------------------- |
| `docker-compose.yml`        | Orquestación de RabbitMQ, PostgreSQL, producer, consumer, etc. |
| `producer/`                 | Microservicio Producer (envío & métricas)                      |
| `consumer/`                 | Microservicio Consumer (consumo & métricas)                    |
| `alerter/`            | Microservicio de alertas en tiempo real                        |
| `api/`                      | API REST para consulta histórica y reportes                    |
| `postgres/init_db.sql`      | Script SQL para crear la tabla `weather_logs`                  |
| `rabbitmq/definitions.json` | Configuración de exchange y cola exportada                     |
| `prometheus/prometheus.yml` | Configuración de scrapes de métricas                           |

---

## 📌 Buenas prácticas

* Ramas: `develop` para desarrollo diario, `main` para releases estables.
* Usa `docker-compose down` para limpiar antes de reiniciar.
* Documenta cada funcionalidad nueva en la carpeta `docs/`.
* Mantén entornos virtuales aislados en cada microservicio.
* Revisa métricas y logs regularmente para detectar anomalías.

---

*Última actualización: 2025-05-09*
