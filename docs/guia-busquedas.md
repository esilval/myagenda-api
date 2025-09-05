# Guía de búsqueda, filtros e índices

Esta guía documenta los modos de búsqueda, filtros, paginación e índices creados para `companies` y `clients`.

## Endpoints y parámetros

### Companies
- Listar (paginado y filtros):
  - `GET /companies?page=<n>&size=<m>&status=<ACTIVE|INACTIVE>&q=<texto>`
  - Filtros:
    - `status`: estado de la compañía
    - `q`: texto libre (aplica ILIKE/trigram sobre `business_name`, `city`, `nit`)
  - Respuesta: `{ total, items: CompanyDTO[] }`

- CRUD:
  - `POST /companies` – Crea (NIT único, validado con DV colombiano)
  - `GET /companies/<company_id>` – Detalle
  - `PUT /companies/<company_id>` – Actualiza (re-valida unicidad de NIT)
  - `DELETE /companies/<company_id>` – Elimina

### Clients
- Listar (paginado y filtros, con join opcional):
  - `GET /clients?page=<n>&size=<m>&status=<ACTIVE|INACTIVE>&q=<texto>&include_company=true|false`
  - Filtros:
    - `status`: estado del cliente
    - `q`: texto libre (aplica ILIKE/trigram sobre `contact_name`, `phone`, `email`)
    - `include_company`: si `true`, incluye datos mínimos de la compañía del cliente
  - Respuesta: `{ total, items: ClientDTO[] }`, y cada item podrá incluir `company` si se solicitó el join

- Mutaciones:
  - `POST /clients` – Crea (requiere `company_id`, `email` y `phone` únicos)
  - `PUT /clients/<client_id>` – Actualiza (valida `COMPANY_NOT_FOUND`, `EMAIL_TAKEN`, `PHONE_TAKEN` cuando aplique)
  - `POST /clients/<client_id>/deactivate` – Inactiva
  - `DELETE /clients/<client_id>` – Elimina

## Índices creados

### Companies
- Unicidad:
  - `ix_companies_nit` (único) sobre `nit`
- Compuestos:
  - `ix_companies_status_city (status, city)`
  - `ix_companies_name_city (business_name, city)`
- Texto (pg_trgm):
  - `ix_companies_name_trgm` GIN sobre `business_name`
  - `ix_companies_city_trgm` GIN sobre `city`

### Clients
- Unicidad:
  - `email` (único), `phone` (único)
- Compuestos:
  - `ix_clients_company_status (company_id, status)`
  - `ix_clients_status_created (status, created_at)`
  - `ix_clients_company_created (company_id, created_at)`
- Texto (pg_trgm):
  - `ix_clients_contact_name_trgm` GIN sobre `contact_name`
  - `ix_clients_email_trgm` GIN sobre `email`
  - `ix_clients_phone_trgm` GIN sobre `phone`

Notas:
- La extensión `pg_trgm` se habilita con la migración `enable pg_trgm and add trigram/functional indexes`.
- Los índices GIN con `gin_trgm_ops` aceleran búsquedas por ILIKE y similitud.

## Ejemplos de uso (curl)

Listar compañías activas, búsqueda por nombre o ciudad, página 2 de tamaño 20:

```bash
curl -s "http://localhost:5000/companies?status=ACTIVE&q=bogota&page=2&size=20"
```

Listar clientes de forma paginada, uniendo compañía y filtrando por texto:

```bash
curl -s "http://localhost:5000/clients?include_company=true&q=perez&page=1&size=10"
```

## Recomendaciones de consultas (SQL)

- Búsquedas por texto con ILIKE activan los índices trigram:

```sql
-- Companies: por nombre o ciudad
SELECT * FROM companies
WHERE business_name ILIKE '%mega%'
   OR city ILIKE '%medell%'
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;

-- Clients: por nombre de contacto, email o teléfono
SELECT * FROM clients
WHERE contact_name ILIKE '%perez%'
   OR email ILIKE '%@acme.%'
   OR phone ILIKE '%300%';
```

- Filtrado por estado y orden temporal apoyado por índices compuestos:

```sql
SELECT * FROM clients
WHERE status = 'ACTIVE'
ORDER BY created_at DESC
LIMIT 50;
```

- Segmentación por compañía + estado:

```sql
SELECT * FROM clients
WHERE company_id = :company_id AND status = 'ACTIVE'
ORDER BY created_at DESC
LIMIT 50;
```

## Mantenimiento y diagnósticos

- Reindexación/ANALYZE (como parte de operaciones regulares):

```sql
VACUUM (ANALYZE) companies;
VACUUM (ANALYZE) clients;
REINDEX TABLE companies;
REINDEX TABLE clients;
```

- Diagnóstico de planes de ejecución:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM clients WHERE contact_name ILIKE '%perez%' LIMIT 20;
```

## Consideraciones

- Si el dataset crece, considerar limitar longitud de campos de búsqueda y normalizar (ej. `email` y `phone`) en la aplicación.
- Para uso avanzado, se puede incorporar un endpoint de búsqueda con parámetros dedicados o un motor externo (p. ej. Elasticsearch), según necesidades.
