# 📦 Insight Monitor MVP (Visor de Base de Datos)

Este directorio contiene la configuración de Docker para visualizar la base de datos **MVP (SQLite)** que describe la documentación oficial (`docs/data-model/database-schema.md`).

Dado que la arquitectura MVP usa **SQLite** (un archivo local) en lugar de un servidor como MySQL, este Docker **no** levanta un servidor de base de datos, sino un **Visor Web** que lee en tiempo real el archivo generado por el código de tu rama `develop`.

## 🚀 Requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado.
- [Docker Compose](https://docs.docker.com/compose/install/) instalado.
- Puerto `8081` libre en tu máquina.
- Que el backend del proyecto haya sido ejecutado al menos una vez para generar el archivo `backend/data/insight_monitor.db` (nuestro código lo autogenera).

## 🛠️ Cómo levantar el Visor del MVP

Abre una terminal en esta carpeta (`infrastructure/db-mvp/`) y ejecuta:

```bash
sudo docker compose up -d
```

## 👁️ Visualizar las 3 Tablas del MVP

Una vez que el contenedor esté corriendo, abre tu navegador web y entra a:

- **URL:** [http://localhost:8081](http://localhost:8081)
- **Contraseña:** `mvppassword`

Una vez adentro, verás exactamente la lógica que describe la documentación:
- `raw_events`
- `sessions`
- `intent_records`

Podrás hacer consultas SQL, exportar datos y ver en tiempo real cómo se llenan las tablas mientras usas el agente de monitoreo.

## 🧹 Apagar el visor

Para detener el contenedor:
```bash
docker-compose down
```
