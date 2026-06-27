# Insight Monitor MVP (Database Viewer)

⚠️ **IMPORTANT: This is a DATABASE VIEWER (sqlite-web), NOT a database server.**

The MVP uses **SQLite** (a local file), not a server like MySQL/PostgreSQL. The database file `backend/data/insight_monitor.db` is **auto-created by the backend** on first run (via `Database._init_schema()`). This Docker container only provides a **web UI to browse the existing `.db` file** — it does not create or manage the database.

---

This directory contains the Docker configuration to visualize the **MVP (SQLite)** database described in the official documentation (`docs/data-model/database-schema.md`).

## Requirements

- [Docker](https://docs.docker.com/get-docker/) installed.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.
- Port `8081` must be free on your machine.
- The backend must have been executed at least once to generate the `backend/data/insight_monitor.db` file (our code auto-generates it).

## How to Start the MVP Viewer

Open a terminal in this folder (`infrastructure/db-mvp/`) and run:

```bash
docker compose up -d
```

## View the 3 MVP Tables

Once the container is running, open your web browser and go to:

- **URL:** [http://localhost:8081](http://localhost:8081)
- **Password:** Set via the `SQLITE_WEB_PASSWORD` environment variable (default: `mvppassword`)

Once inside, you will see exactly the logic described in the documentation:
- `raw_events`
- `sessions`
- `intent_records`

You can run SQL queries, export data, and see in real time how the tables are populated while you use the monitoring agent.

## Stop the Viewer

To stop the container:

```bash
docker compose down
```