---
title: Database MVP Scope vs Complete DER
type: conceptual
domain: data-model
priority: high
status: accepted
version: 1.0.0
---

# 🎯 Database Architecture: MVP vs Full DER

Este documento define claramente las fronteras de arquitectura de datos entre el **MVP (Minimum Viable Product)** actualmente en desarrollo y la visión a largo plazo plasmada en el **Diagrama Entidad-Relación (DER) Completo**.

## 🚀 Fase 1: El MVP de Escritorio (Estado Actual)

El foco del MVP (Día 1 & 2) es probar el ciclo cerrado de **Captura Local → Inferencia IA Local**. Para evitar sobreingeniería y acelerar el desarrollo, se ha adoptado una arquitectura temporal simplificada.

**Características del esquema MVP:**
- **Motor:** SQLite local (`insight_monitor.db`).
- **Modo:** WAL (Write-Ahead Logging) para concurrencia segura entre hilos.
- **Alcance:** Monousuario estricto. La máquina local equivale a todo el contexto.

### Tablas Implementadas (El "Qué" del MVP)

1. **`raw_events`**: Unifica los conceptos de evento, ventana activa y registro de capturas en un solo registro atómico temporal.
2. **`sessions`**: Agrupa ventanas de tiempo de trabajo, omitiendo cualquier relación foránea hacia usuarios, empresas o agentes de la nube.
3. **`intent_records`**: Guarda el resultado de la inferencia IA local de forma denormalizada.

*(Referirse a `database-schema.md` para el esquema exacto de SQLite).*

---

## ☁️ Fase 2: Cloud Enterprise (El DER Completo)

El DER oficial documenta la **arquitectura objetivo en la nube**, la cual será necesaria una vez que el sistema se convierta en una plataforma SaaS Multi-Tenant.

**Características del esquema DER:**
- **Motor:** Base de datos relacional robusta (ej. MySQL/PostgreSQL).
- **Modo:** Servidor centralizado.
- **Alcance:** Multi-tenant (Empresas -> Usuarios -> Múltiples Agentes/Equipos).

### Módulos Posteriores al MVP

Los siguientes módulos documentados en el DER **NO formarán parte del MVP** y se construirán en fases posteriores:

1. **Módulo Organizacional**: Tablas de `empresa`, `usuario`, `rol` y `usuario_rol`.
2. **Módulo de Agentes**: Registro de clientes de captura por máquina (`agente`).
3. **Módulo de Privacidad**: Motor de redacción y reglas de censura (`regla_privacidad`, `deteccion_sensible`).
4. **Módulo de Reportes & Auditoría**: Históricos analíticos precalculados (`reporte`) y registro de accesos al sistema (`auditoria`).
5. **Normalización Estricta**: Separación de `evento` base de la metadata de `captura_pantalla`, `texto_ocr` y `ventana_activa`.

## 🔄 Estrategia de Migración Futura

El diseño actual de `raw_events` y `sessions` incluye identificadores UUID generados localmente. En la Fase 2, un servicio de sincronización (Sync Agent) tomará estos registros locales de SQLite y los insertará en el clúster MySQL central, inyectando los UUIDs foráneos del `id_usuario` e `id_agente` que correspondan al token de autenticación del dispositivo.
