CREATE DATABASE IF NOT EXISTS insight_monitor_enterprise;
USE insight_monitor_enterprise;

-- NOTE: This schema is intended for development and testing purposes only.
-- In production, the database should already be deployed and managed
-- outside of Docker init scripts.

-- 1. ORGANIZATIONAL MODULE
CREATE TABLE company (
    id_company CHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    tax_id VARCHAR(50),
    status BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user (
    id_user CHAR(36) PRIMARY KEY,
    id_company CHAR(36),
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    job_title VARCHAR(100),
    status BOOLEAN DEFAULT TRUE,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_company) REFERENCES company(id_company) ON DELETE CASCADE
);

CREATE TABLE role (
    id_role CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE user_role (
    id_user_role CHAR(36) PRIMARY KEY,
    id_user CHAR(36),
    id_role CHAR(36),
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_role) REFERENCES role(id_role) ON DELETE CASCADE
);

-- 2. AGENTS MODULE
CREATE TABLE agent (
    id_agent CHAR(36) PRIMARY KEY,
    id_user CHAR(36),
    version VARCHAR(50),
    hostname VARCHAR(255),
    operating_system VARCHAR(100),
    status ENUM('ONLINE', 'OFFLINE', 'ERROR', 'PAUSED') DEFAULT 'OFFLINE',
    last_connection DATETIME,
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE CASCADE
);

-- 3. MONITORING MODULE
CREATE TABLE session (
    id_session CHAR(36) PRIMARY KEY,
    id_user CHAR(36),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_seconds INT,
    productivity_score DECIMAL(5,2),
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE CASCADE
);

CREATE TABLE event (
    id_event CHAR(36) PRIMARY KEY,
    id_session CHAR(36),
    event_type ENUM('WINDOW_CHANGE', 'SCREENSHOT', 'WEB_VISIT', 'INPUT_ACTIVITY', 'APPLICATION_OPEN', 'APPLICATION_CLOSE') NOT NULL,
    event_timestamp DATETIME NOT NULL,
    confidence DECIMAL(5,2),
    FOREIGN KEY (id_session) REFERENCES session(id_session) ON DELETE CASCADE
);

CREATE TABLE active_window (
    id_window CHAR(36) PRIMARY KEY,
    id_event CHAR(36),
    title VARCHAR(500),
    process VARCHAR(255),
    application VARCHAR(255),
    url TEXT,
    FOREIGN KEY (id_event) REFERENCES event(id_event) ON DELETE CASCADE
);

-- 4. SCREENSHOT CAPTURE MODULE
CREATE TABLE screenshot (
    id_screenshot CHAR(36) PRIMARY KEY,
    id_event CHAR(36),
    file_path TEXT,
    image_hash VARCHAR(255),
    captured_at DATETIME,
    was_redacted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_event) REFERENCES event(id_event) ON DELETE CASCADE
);

CREATE TABLE ocr_text (
    id_ocr CHAR(36) PRIMARY KEY,
    id_screenshot CHAR(36),
    extracted_text LONGTEXT,
    confidence_level DECIMAL(5,2),
    FOREIGN KEY (id_screenshot) REFERENCES screenshot(id_screenshot) ON DELETE CASCADE
);

-- 5. PRIVACY MODULE
CREATE TABLE privacy_rule (
    id_rule CHAR(36) PRIMARY KEY,
    name VARCHAR(150),
    category ENUM('PASSWORD', 'FINANCIAL', 'HEALTH', 'LEGAL', 'PERSONAL', 'IDENTIFICATION'),
    description TEXT,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE sensitive_detection (
    id_detection CHAR(36) PRIMARY KEY,
    id_screenshot CHAR(36),
    id_rule CHAR(36),
    detected_text TEXT,
    action ENUM('MASK', 'REMOVE', 'BLOCK', 'ALERT'),
    FOREIGN KEY (id_screenshot) REFERENCES screenshot(id_screenshot) ON DELETE CASCADE,
    FOREIGN KEY (id_rule) REFERENCES privacy_rule(id_rule) ON DELETE SET NULL
);

-- 6. ARTIFICIAL INTELLIGENCE MODULE
CREATE TABLE intention (
    id_intention CHAR(36) PRIMARY KEY,
    id_session CHAR(36),
    name VARCHAR(150),
    description TEXT,
    confidence DECIMAL(5,2),
    FOREIGN KEY (id_session) REFERENCES session(id_session) ON DELETE CASCADE
);

CREATE TABLE ai_inference (
    id_inference CHAR(36) PRIMARY KEY,
    id_intention CHAR(36),
    model VARCHAR(100),
    prompt LONGTEXT,
    response LONGTEXT,
    tokens INT,
    processed_at DATETIME,
    FOREIGN KEY (id_intention) REFERENCES intention(id_intention) ON DELETE CASCADE
);

-- 7. REPORTS MODULE
CREATE TABLE report (
    id_report CHAR(36) PRIMARY KEY,
    id_user CHAR(36),
    start_date DATE,
    end_date DATE,
    productivity DECIMAL(5,2),
    summary LONGTEXT,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE CASCADE
);

-- 8. AUDIT MODULE
CREATE TABLE audit (
    id_audit CHAR(36) PRIMARY KEY,
    id_user CHAR(36),
    action VARCHAR(255),
    entity VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details LONGTEXT,
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE SET NULL
);
