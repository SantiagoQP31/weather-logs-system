# Contrato de Mensajes JSON

El productor (producer) enviará mensajes al exchange de RabbitMQ con el siguiente formato:

```json
{
  "station_id": "EST123",
  "timestamp": "2025-05-07T15:30:00Z",
  "temperature": 24.50,
  "humidity": 78.20,
  "pressure": 1013.40
}
```

## Descripción de campos

| Campo        | Tipo    | Descripción                                    | Rango válido          |
|--------------|---------|------------------------------------------------|-----------------------|
| station_id   | String  | Identificador único de la estación             | —                     |
| timestamp    | String  | Fecha y hora en formato ISO 8601 (UTC)         | —                     |
| temperature  | Decimal | Temperatura en °C                              | -30.00 a 60.00        |
| humidity     | Decimal | Humedad relativa en %                          | 0.00 a 100.00         |
| pressure     | Decimal | Presión atmosférica en hPa                     | 700.00 a 1100.00      |

## Notas de validación

Si algún campo está fuera de los rangos definidos, el consumer **no** debe insertarlo en la base de datos y debe registrar un **error** en su log con estos detalles:

| Campo        | Rango válido         | Condición de error                  | Acción del consumer                 |
|--------------|----------------------|-------------------------------------|-------------------------------------|
| temperature  | -30.00 a 60.00 °C    | `< -30.00` o `> 60.00`              | Loguear error y descartar mensaje   |
| humidity     | 0.00 a 100.00 %      | `< 0.00` o `> 100.00`               | Loguear error y descartar mensaje   |
| pressure     | 700.00 a 1100.00 hPa | `< 700.00` o `> 1100.00`            | Loguear error y descartar mensaje   |


