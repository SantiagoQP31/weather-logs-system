-- init_db.sql
-- Tabla weather_logs para almacenar los datos de estaciones meteorológicas

CREATE TABLE IF NOT EXISTS weather_logs (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL,
  station_id VARCHAR(50) NOT NULL,
  temperature NUMERIC(5,2) NOT NULL,
  humidity NUMERIC(5,2) NOT NULL,
  pressure NUMERIC(7,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para acelerar consultas por tiempo y por estación
CREATE INDEX IF NOT EXISTS idx_weather_logs_timestamp ON weather_logs (timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_logs_station_id ON weather_logs (station_id);
