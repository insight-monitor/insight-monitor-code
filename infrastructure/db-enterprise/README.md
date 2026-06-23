# Insight Monitor Enterprise (Phase 2 Full ERD)

This directory contains the local **Docker** infrastructure to spin up the **Complete Entity-Relationship Diagram (ERD)** of the project using MySQL.

Although the MVP (Day 1 & 2) uses SQLite with 3 tables, this container allows you to **visualize, validate, and test** the entire final architecture designed for the cloud (organizational module, agents, OCR, reports, privacy, etc.).

## Requirements

- [Docker](https://docs.docker.com/get-docker/) installed.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.
- Ports `3306` (MySQL) and `8080` (Viewer) must be free on your machine.

## How to Start the Database

Open a terminal in this directory (`infrastructure/db-enterprise/`) and run:

```bash
docker-compose up -d
```

## What Does This Docker Do?

When you execute `docker compose up -d`, two things happen:
1. It downloads and starts the official **MySQL 8.0** image in an isolated container.
2. It automatically reads the `init.sql` file in this directory and **executes the entire ERD schema**, creating all Module structures (Organizational, Agents, Monitoring, etc.) with their respective tables, ENUMs, and foreign keys. Everything is exposed on port **3307**.

## How to Connect Your IDE (DBeaver)

As a good professional practice, the insecure web viewer was removed. To interact with the database you must connect a manager like **DBeaver** or **DataGrip**.

Follow these steps in DBeaver:

1. Click **New Connection** (plug icon).
2. Select **MySQL** and click Next.
3. Fill in the credentials with these exact values:
   - **Server Host:** `localhost`
   - **Port:** `3307` *(Be careful! Do not use 3306 to avoid conflicting with your local database)*
   - **Database:** `insight_monitor_enterprise`
   - **Username:** `root`
   - **Password:** `rootpassword`
4. **Key step for MySQL 8!** Go to the **"Driver properties"** tab.
   - Find the `allowPublicKeyRetrieval` property.
   - Change it from `false` to **`true`**.
5. Click **Test Connection** to validate, then **Finish**.

You can now open the database and see all table categories built from your official diagram.

## Credentials for Code Connection (Optional)

If you ever decide to connect the Python backend to this database instead of SQLite, use the following SQLAlchemy URI:

```
mysql+pymysql://insight_user:insight_password@localhost:3306/insight_monitor_enterprise
```

## Stop or Restart the Database

To stop the containers (without deleting data):
```bash
docker-compose stop
```

To destroy them and **delete** the database (in case you want to regenerate it or modify `init.sql`):
```bash
docker-compose down -v
```
