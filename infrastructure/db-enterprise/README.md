# Insight Monitor Enterprise (Fase 2 DER Completo)

Este directorio contiene la infraestructura local en **Docker** para levantar el **Diagrama Entidad-Relación (DER) Completo** del proyecto, usando MySQL.

Aunque el MVP (Día 1 & 2) utiliza SQLite y 3 tablas, este contenedor permite **visualizar, validar y probar** toda la estructura final pensada para la nube (módulo organizacional, agentes, OCR, reportes, privacidad, etc).

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado.
- [Docker Compose](https://docs.docker.com/compose/install/) instalado.
- Puertos `3306` (MySQL) y `8080` (Visor) libres en tu máquina.

##  Cómo levantar la base de datos

Abre una terminal en esta misma carpeta (`infrastructure/db-enterprise/`) y ejecuta:

```bash
docker-compose up -d
```

## ⚙️ ¿Qué hace este Docker?

Cuando ejecutas el comando `docker compose up -d`, suceden dos cosas:
1. Se descarga y levanta la imagen oficial de **MySQL 8.0** en un contenedor aislado.
2. Automáticamente lee el archivo `init.sql` que acompaña a este directorio y **ejecuta todo el esquema del DER Completo**, creando la estructura de Módulos (Organizacional, Agentes, Monitoreo, etc.) con sus respectivas tablas, enumeradores (ENUM) y llaves foráneas. Todo esto lo expone en el puerto **3307**.

## 🔌 Cómo conectar tu IDE (DBeaver)

Como buena práctica profesional, se eliminó el visor web inseguro. Para interactuar con la base de datos debes conectarla a un gestor como **DBeaver** o **DataGrip**.

Sigue estos pasos en DBeaver:

1. Haz clic en **Nueva Conexión** (ícono de enchufe).
2. Selecciona **MySQL** y haz clic en Siguiente.
3. Rellena las credenciales con estos datos exactos:
   - **Server Host:** `localhost`
   - **Port:** `3307` *(¡Cuidado! No uses 3306 para evitar chocar con tu base local)*
   - **Database:** `insight_monitor_enterprise`
   - **Username:** `root`
   - **Password:** `rootpassword`
4. **¡Paso clave para MySQL 8!** Ve a la pestaña superior llamada **"Driver properties"**.
   - Busca la propiedad `allowPublicKeyRetrieval`.
   - Cámbiala de `false` a **`true`**.
5. Clic en **Test Connection** para validar y luego en **Finish**.

Ya podrás abrir la base de datos y ver todas las categorías de tablas construidas a partir de tu diagrama oficial.

## 🗄️ Credenciales para Conexión desde Código (Opcional)

Si alguna vez decides conectar el backend en Python a esta base de datos en vez del SQLite, usa la siguiente URI de SQLAlchemy:

```
mysql+pymysql://insight_user:insight_password@localhost:3306/insight_monitor_enterprise
```

## Apagar o reiniciar la BD

Para detener los contenedores (sin borrar los datos):
```bash
docker-compose stop
```

Para destruirlos y **borrar** la base de datos (por si quieres regenerarla o modificar el `init.sql`):
```bash
docker-compose down -v
```
