# 🏢 Insight Monitor Enterprise (Fase 2 DER Completo)

Este directorio contiene la infraestructura local en **Docker** para levantar el **Diagrama Entidad-Relación (DER) Completo** del proyecto, usando MySQL.

Aunque el MVP (Día 1 & 2) utiliza SQLite y 3 tablas, este contenedor permite **visualizar, validar y probar** toda la estructura final pensada para la nube (módulo organizacional, agentes, OCR, reportes, privacidad, etc).

## 🚀 Requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado.
- [Docker Compose](https://docs.docker.com/compose/install/) instalado.
- Puertos `3306` (MySQL) y `8080` (Visor) libres en tu máquina.

## 🛠️ Cómo levantar la base de datos

Abre una terminal en esta misma carpeta (`infrastructure/db-enterprise/`) y ejecuta:

```bash
docker-compose up -d
```

Este comando descargará las imágenes, creará los contenedores y ejecutará el archivo `init.sql` automáticamente para crear todas las tablas, relaciones (Foreign Keys) y enumeradores exactamente como indica el diagrama.

## 👁️ Visualizar la Base de Datos

Una vez que los contenedores estén corriendo, puedes entrar a la base de datos visualmente a través del navegador web usando phpMyAdmin:

- **URL:** [http://localhost:8080](http://localhost:8080)
- **Servidor:** `mysql-enterprise`
- **Usuario:** `root`
- **Contraseña:** `rootpassword`

Una vez dentro, haz clic en la base de datos llamada `insight_monitor_enterprise` a tu izquierda. Ahí verás los **8 Módulos** y sus correspondientes tablas ya creadas con todas las relaciones configuradas.

## 🗄️ Credenciales para Conexión desde Código (Opcional)

Si alguna vez decides conectar el backend en Python a esta base de datos en vez del SQLite, usa la siguiente URI de SQLAlchemy:

```
mysql+pymysql://insight_user:insight_password@localhost:3306/insight_monitor_enterprise
```

## 🧹 Apagar o reiniciar la BD

Para detener los contenedores (sin borrar los datos):
```bash
docker-compose stop
```

Para destruirlos y **borrar** la base de datos (por si quieres regenerarla o modificar el `init.sql`):
```bash
docker-compose down -v
```
