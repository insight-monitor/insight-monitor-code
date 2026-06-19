CREATE DATABASE IF NOT EXISTS insight_monitor_enterprise;
USE insight_monitor_enterprise;

-- 1. MÓDULO ORGANIZACIONAL
CREATE TABLE empresa (
    id_empresa CHAR(36) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nit VARCHAR(50),
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuario (
    id_usuario CHAR(36) PRIMARY KEY,
    id_empresa CHAR(36),
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    cargo VARCHAR(100),
    estado BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa) ON DELETE CASCADE
);

CREATE TABLE rol (
    id_rol CHAR(36) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE usuario_rol (
    id_usuario_rol CHAR(36) PRIMARY KEY,
    id_usuario CHAR(36),
    id_rol CHAR(36),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol) ON DELETE CASCADE
);

-- 2. MÓDULO DE AGENTES
CREATE TABLE agente (
    id_agente CHAR(36) PRIMARY KEY,
    id_usuario CHAR(36),
    version VARCHAR(50),
    hostname VARCHAR(255),
    sistema_operativo VARCHAR(100),
    estado ENUM('ONLINE', 'OFFLINE', 'ERROR', 'PAUSED') DEFAULT 'OFFLINE',
    ultima_conexion DATETIME,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- 3. MÓDULO DE MONITOREO
CREATE TABLE sesion (
    id_sesion CHAR(36) PRIMARY KEY,
    id_usuario CHAR(36),
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME,
    duracion_segundos INT,
    score_productividad DECIMAL(5,2),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE evento (
    id_evento CHAR(36) PRIMARY KEY,
    id_sesion CHAR(36),
    tipo_evento ENUM('WINDOW_CHANGE', 'SCREENSHOT', 'WEB_VISIT', 'INPUT_ACTIVITY', 'APPLICATION_OPEN', 'APPLICATION_CLOSE') NOT NULL,
    timestamp_evento DATETIME NOT NULL,
    confianza DECIMAL(5,2),
    FOREIGN KEY (id_sesion) REFERENCES sesion(id_sesion) ON DELETE CASCADE
);

CREATE TABLE ventana_activa (
    id_ventana CHAR(36) PRIMARY KEY,
    id_evento CHAR(36),
    titulo VARCHAR(500),
    proceso VARCHAR(255),
    aplicacion VARCHAR(255),
    url TEXT,
    FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE CASCADE
);

-- 4. MÓDULO DE CAPTURA DE PANTALLA
CREATE TABLE captura_pantalla (
    id_captura CHAR(36) PRIMARY KEY,
    id_evento CHAR(36),
    ruta_archivo TEXT,
    hash_imagen VARCHAR(255),
    fecha_captura DATETIME,
    fue_redactada BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_evento) REFERENCES evento(id_evento) ON DELETE CASCADE
);

CREATE TABLE texto_ocr (
    id_ocr CHAR(36) PRIMARY KEY,
    id_captura CHAR(36),
    texto_extraido LONGTEXT,
    nivel_confianza DECIMAL(5,2),
    FOREIGN KEY (id_captura) REFERENCES captura_pantalla(id_captura) ON DELETE CASCADE
);

-- 5. MÓDULO DE PRIVACIDAD
CREATE TABLE regla_privacidad (
    id_regla CHAR(36) PRIMARY KEY,
    nombre VARCHAR(150),
    categoria ENUM('PASSWORD', 'FINANCIERO', 'SALUD', 'LEGAL', 'PERSONAL', 'IDENTIFICACION'),
    descripcion TEXT,
    activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE deteccion_sensible (
    id_deteccion CHAR(36) PRIMARY KEY,
    id_captura CHAR(36),
    id_regla CHAR(36),
    texto_detectado TEXT,
    accion ENUM('MASK', 'REMOVE', 'BLOCK', 'ALERT'),
    FOREIGN KEY (id_captura) REFERENCES captura_pantalla(id_captura) ON DELETE CASCADE,
    FOREIGN KEY (id_regla) REFERENCES regla_privacidad(id_regla) ON DELETE SET NULL
);

-- 6. MÓDULO DE INTELIGENCIA ARTIFICIAL
CREATE TABLE intencion (
    id_intencion CHAR(36) PRIMARY KEY,
    id_sesion CHAR(36),
    nombre VARCHAR(150),
    descripcion TEXT,
    confianza DECIMAL(5,2),
    FOREIGN KEY (id_sesion) REFERENCES sesion(id_sesion) ON DELETE CASCADE
);

CREATE TABLE inferencia_ia (
    id_inferencia CHAR(36) PRIMARY KEY,
    id_intencion CHAR(36),
    modelo VARCHAR(100),
    prompt LONGTEXT,
    respuesta LONGTEXT,
    tokens INT,
    fecha_proceso DATETIME,
    FOREIGN KEY (id_intencion) REFERENCES intencion(id_intencion) ON DELETE CASCADE
);

-- 7. MÓDULO DE REPORTES
CREATE TABLE reporte (
    id_reporte CHAR(36) PRIMARY KEY,
    id_usuario CHAR(36),
    fecha_inicio DATE,
    fecha_fin DATE,
    productividad DECIMAL(5,2),
    resumen LONGTEXT,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- 8. MÓDULO DE AUDITORÍA
CREATE TABLE auditoria (
    id_auditoria CHAR(36) PRIMARY KEY,
    id_usuario CHAR(36),
    accion VARCHAR(255),
    entidad VARCHAR(255),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    detalle LONGTEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE SET NULL
);
