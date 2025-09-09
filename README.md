# myagenda-api (Flask mínimo)

## Propósito del proyecto
Backend ligero para administrar usuarios, compañías y clientes, con autenticación JWT y control de acceso por usuario. Sirve como base de una agenda/CRM sencillo donde:

- **Usuarios**: se registran, inician sesión y operan con su propio contexto.
- **Compañías**: entidades a las que se pueden asociar clientes (NIT validado con DV de la DIAN).
- **Clientes**: contactos asociados a compañías; al crear un cliente, queda automáticamente vinculado al usuario autenticado y el listado se filtra por dicho usuario.

### Alcance y objetivos
- **Autenticación**: emisión y verificación de tokens JWT (30 min de vigencia).
- **Gestión**: CRUD de compañías y clientes (con paginación y filtros básicos).
- **Multiusuario**: relación muchos-a-muchos usuario–cliente para segmentar datos por usuario.
- **Validez de NIT**: utilitario para normalización/validación y generación de NITs válidos para pruebas.

No cubre: agenda/calendario, facturación, ni workflows avanzados. La guía de búsquedas e índices específicos se documenta aparte en `docs/guia-busquedas.md`.

## Arquitectura

```mermaid
graph TD
  A["Cliente (Postman / Frontend)"] -->|"HTTP JSON"| B["API Flask (Gunicorn)"]
  B -->|"SQLAlchemy\nDAO / Services"| C[("PostgreSQL")]
  B --> D["JWT (Auth)"]
```

- Autenticación con JWT: `POST /login` emite tokens; `GET /auth` valida.
- Capa de negocio: Services y DAOs separan lógica y acceso a datos.
- Persistencia: SQLAlchemy + Alembic para migraciones.
- Multiusuario: relación `user_clients` filtra `GET /clients` por el usuario autenticado y asocia clientes al crearlos.

## Modelo de datos

```mermaid
erDiagram
  USERS ||--o{ USER_CLIENTS : "has"
  CLIENTS ||--o{ USER_CLIENTS : "linked to"
  COMPANIES ||--o{ CLIENTS : "has"

  USERS {
    string id PK
    string name
    string email
    string nickname
    string password
    string company
    enum status
    datetime created_at
    datetime updated_at
  }

  COMPANIES {
    string id PK
    string nit
    string business_name
    string city
    enum status
    datetime created_at
    datetime updated_at
  }

  CLIENTS {
    string id PK
    string company_id FK
    string contact_name
    string phone
    string email
    enum status
    datetime created_at
    datetime updated_at
  }

  USER_CLIENTS {
    string id PK
    string user_id FK
    string client_id FK
    datetime created_at
  }
```


## Requisitos
- Python 3.11+ (recomendado)

## Configuración rápida
```bash
cd myagenda-api
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

## Ejecutar la app
```bash
.venv/bin/python -m src.app
```

La app expondrá `GET /` devolviendo `{ "status": "ok" }` en el puerto 5000.

## Variables de entorno
Duplica `.env.example` a `.env` en `myagenda-api/` y ajusta credenciales:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/myagenda
JWT_SECRET=dev-secret
# Lista de orígenes separados por coma o "*" para permitir todos
# Ejemplos:
# CORS_ORIGINS=*
# CORS_ORIGINS=http://localhost:3000
# CORS_ORIGINS=http://localhost:3000,https://mi-frontend.com
CORS_ORIGINS=*
```

Si `CORS_ORIGINS` no se establece, por defecto se permite `*`. En producción se recomienda configurar orígenes explícitos y cambiar `JWT_SECRET` por un valor fuerte/aleatorio.

## Migraciones con Alembic
Comandos básicos (usar siempre el intérprete del venv):
```bash
# inicial ya creado: alembic init migrations
.venv/bin/alembic revision --autogenerate -m "<mensaje>"
.venv/bin/alembic upgrade head
.venv/bin/alembic downgrade -1
```
Nota: para `--autogenerate` debe estar corriendo PostgreSQL y `DATABASE_URL` válido.

## Base de datos con Docker
Levantar PostgreSQL con Docker Compose:
```bash
docker compose up -d
```

La URL por defecto del proyecto:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/myagenda
```

Aplicar migraciones una vez la base esté arriba:
```bash
.venv/bin/alembic upgrade head
```

## Ejecutar API con Docker Compose
Servicio `api` incluido en `docker-compose.yml`:
```bash
docker compose build api
docker compose up -d api
```

La API corre en `http://localhost:5000/` con healthcheck en `GET /`.
Con hot-reload (flask --debug) al editar archivos.

## Producción local (Gunicorn)
Construir y levantar con `docker-compose.prod.yml`:
```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```
La API quedará expuesta en `http://localhost:5000/` usando Gunicorn.

## Autenticación (JWT)
- Inicio de sesión: `POST /login` con `{ identifier, password }` (identifier puede ser email o nickname).
- Validación: `GET /auth` con header `Authorization: Bearer <token>`.
- Expiración del token: 30 minutos.
- Sólo usuarios `ACTIVE` pueden autenticarse.

### Flujo de ejemplo (curl)
```bash
# 1) Crear usuario
curl -s -X POST http://localhost:5000/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Admin","email":"admin@example.com","password":"adminpass"}'

# 2) Login (obtener token)
TOKEN=$(curl -s -X POST http://localhost:5000/login \
  -H 'Content-Type: application/json' \
  -d '{"identifier":"admin@example.com","password":"adminpass"}' | jq -r .access_token)

# 3) Crear compañía protegida
curl -s -X POST http://localhost:5000/companies \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"nit":"800197268-4","business_name":"ACME S.A."}'

# 4) Listar compañías (paginado + filtros)
curl -s "http://localhost:5000/companies?status=ACTIVE&q=acme&page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"

# 5) Crear cliente para la compañía
COMPANY_ID=$(curl -s "http://localhost:5000/companies?q=acme" -H "Authorization: Bearer $TOKEN" | jq -r .items[0].id)
curl -s -X POST http://localhost:5000/clients \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"company_id":"'$COMPANY_ID'","contact_name":"Juan Pérez","email":"jperez@example.com","phone":"+57-3000000000"}'

# 6) Listar clientes incluyendo datos de compañía
curl -s "http://localhost:5000/clients?include_company=true&q=perez&page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"

# 7) Obtener detalle de un cliente por ID
CLIENT_ID=$(curl -s "http://localhost:5000/clients?page=1&size=1" -H "Authorization: Bearer $TOKEN" | jq -r .items[0].id)
curl -s "http://localhost:5000/clients/$CLIENT_ID" -H "Authorization: Bearer $TOKEN"
```

Para más detalles de filtros e índices, ver `docs/guia-busquedas.md`.

## Códigos de error
- 400: solicitud inválida (payload o parámetros con validación fallida).
- 401: no autorizado (token ausente o inválido).
- 404: recurso no encontrado.
- 409: conflicto (unicidad de NIT/email/nickname/teléfono).

Ejemplos de respuesta de error:
```json
{"error": "EMAIL_TAKEN"}
```
```json
{"error": ["email: value is not a valid email address"]}
```