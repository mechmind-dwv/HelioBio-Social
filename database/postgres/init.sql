-- Crear la extensión TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Crear la base de datos si no existe (esto se maneja generalmente por el entrypoint de Docker)
-- CREATE DATABASE heliobio_db;

-- Conectarse a la base de datos (asumiendo que ya estamos en heliobio_db)
\c heliobio_db

-- Crear la tabla para datos solares (ejemplo)
CREATE TABLE IF NOT EXISTS solar_data (
    time TIMESTAMPTZ NOT NULL,
    kp_index REAL,
    sunspot_number INTEGER,
    solar_wind_speed REAL,
    proton_density REAL
);

-- Convertir la tabla a una hypertable de TimescaleDB
SELECT create_hypertable('solar_data', 'time', if_not_exists => TRUE);

-- Crear la tabla para datos de salud mental (ejemplo)
CREATE TABLE IF NOT EXISTS mental_health_data (
    time TIMESTAMPTZ NOT NULL,
    region TEXT NOT NULL,
    psychiatric_admissions INTEGER,
    suicide_rate REAL,
    bipolar_episodes INTEGER,
    depression_index REAL
);

-- Convertir la tabla a una hypertable de TimescaleDB
SELECT create_hypertable('mental_health_data', 'time', if_not_exists => TRUE);

-- Crear la tabla para resultados de correlación
CREATE TABLE IF NOT EXISTS correlation_results (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_a TEXT NOT NULL,
    metric_b TEXT NOT NULL,
    correlation_type TEXT NOT NULL, -- e.g., 'pearson', 'granger'
    r_value REAL,
    p_value REAL,
    lag_days INTEGER,
    interpretation TEXT
);

-- Crear un índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_solar_time ON solar_data (time DESC);
CREATE INDEX IF NOT EXISTS idx_mental_time ON mental_health_data (time DESC);
