# Prueba Técnica — Backend

**Tiempo estimado:** 1 hora
**Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic v2, pytest, Docker

---

## Contexto

Construye un servicio HTTP que evalúe solicitudes de crédito. Una solicitud incluye:

| Campo               | Tipo  | Descripción                                       |
|---------------------|-------|---------------------------------------------------|
| `amount`            | int   | Monto solicitado en COP                           |
| `monthly_income`    | int   | Ingresos mensuales en COP                         |
| `employment_months` | int   | Antigüedad laboral en meses                       |
| `external_score`    | int   | Score externo (0–1000)                            |
| `product`           | str   | Tipo de producto: `PHONE`, `TWIST` o `CARD`       |

## Reglas de evaluación

Existen tres políticas que se aplican según el tipo de producto:

| Producto | Política     | Regla                                                                 |
|----------|--------------|-----------------------------------------------------------------------|
| PHONE    | Conservadora | `score ≥ 700` AND `employment_months ≥ 12` AND `cuota ≤ 25% ingreso` |
| TWIST    | Estándar     | `score ≥ 600` AND `cuota ≤ 35% ingreso`                              |
| CARD     | Agresiva     | `score ≥ 550` OR (`score ≥ 500` AND `monthly_income ≥ 3,000,000`)    |

> Asume plazo fijo de 12 meses: `cuota = amount / 12`

Cada solicitud debe persistirse con su decisión (`APPROVED` o `REJECTED`) y las razones del rechazo cuando aplique.

## Endpoints requeridos

1. **`POST /applications`** — recibe la solicitud, la evalúa y la persiste. Retorna la decisión.
2. **`GET /applications/{id}`** — retorna una solicitud por ID.
3. **`GET /applications?status=APPROVED&product=TWIST`** — lista con filtros opcionales.

## Restricciones de diseño

- La selección de política según producto **no** debe ser un `if/elif` dentro del endpoint.
- El acceso a la base de datos **no** debe estar acoplado al endpoint.
- Cubre con tests al menos: una aprobación, un rechazo por cada política, y el flujo end-to-end del endpoint.

## Bonus (solo si te sobra tiempo)

`POST /applications/{id}/reevaluate` que vuelva a correr la evaluación con la política actual (útil si cambian umbrales).

---

## Setup

**Requisitos:** Docker Desktop instalado. Nada más.

### Levantar el servicio

```bash
docker compose up --build
```

- API: http://localhost:8000
- Docs interactivos: http://localhost:8000/docs

### Correr los tests

```bash
docker compose run --rm app pytest -v
```

### Estructura sugerida (puedes modificarla si lo justificas)

```
app/
├── main.py              # FastAPI app + routers
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # engine + session
├── repositories/        # acceso a datos
├── services/            # orquestación
└── strategies/          # políticas de evaluación
tests/
```

## Entrega

Push a tu repo personal (público, o privado con acceso compartido) y envía el link.

¡Éxitos!

# Credit Evaluation Service - Documentación de la solución

Servicio HTTP en Python (FastAPI + SQLAlchemy) para evaluar solicitudes de credito segun politicas por producto (`PHONE`, `TWIST`, `CARD`).

El enunciado original de la prueba esta en `PROBLEM.md`.

## Estado actual

- Implementado:
  - `POST /applications`
  - `POST /applications/{id}/reevaluate`
  - `GET /applications/{id}`
  - `GET /applications?status=...&product=...`
  - `GET /health`
- Persistencia de solicitud, decision (`APPROVED`/`REJECTED`) y razones de rechazo.
- Arquitectura desacoplada por capas (`routers` -> `services` -> `repositories` -> `models`).
- Seleccion de politicas sin `if/elif` en endpoint (via `PolicyFactory`).
- Suite de tests unitaria + e2e en verde.

## Reglas de negocio

Asumiendo plazo fijo de 12 meses:

- `cuota = amount / 12`

Politicas:

- `PHONE` (Conservadora):
  - `external_score >= 700`
  - `employment_months >= 12`
  - `cuota <= 25% monthly_income`
- `TWIST` (Estandar):
  - `external_score >= 600`
  - `cuota <= 35% monthly_income`
- `CARD` (Agresiva):
  - `external_score >= 550`
  - o (`external_score >= 500` y `monthly_income >= 3_000_000`)

## Endpoints

Base URL: `http://localhost:8000`

### Health

- `GET /health`

```bash
curl -X GET "http://localhost:8000/health"
```

### Crear solicitud

- `POST /applications`

```bash
curl -X POST "http://localhost:8000/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1200000,
    "monthly_income": 4000000,
    "employment_months": 18,
    "external_score": 720,
    "product": "PHONE"
  }'
```

### Obtener por ID

- `GET /applications/{id}`

```bash
curl -X GET "http://localhost:8000/applications/1"
```

### Re-evaluar solicitud

- `POST /applications/{id}/reevaluate`

```bash
curl -X POST "http://localhost:8000/applications/1/reevaluate"
```

### Listar con filtros opcionales

- `GET /applications`
- `GET /applications?status=REJECTED`
- `GET /applications?product=TWIST`
- `GET /applications?status=APPROVED&product=TWIST`

```bash
curl -X GET "http://localhost:8000/applications?status=APPROVED&product=TWIST"
```

Valores validos:

- `product`: `PHONE`, `TWIST`, `CARD`
- `status`: `APPROVED`, `REJECTED`

## Arquitectura implementada

Estructura principal:

```text
app/
  main.py
  database.py
  enums.py
  models.py
  schemas.py
  routers/
    applications.py
  services/
    application_service.py
  repositories/
    application_repository.py
  strategies/
    base.py
    phone.py
    twist.py
    card.py
    factory.py
tests/
  conftest.py
  test_health.py
  test_strategies.py
  test_applications_endpoints.py
```

Flujo de una solicitud:

1. `app/routers/applications.py` recibe request HTTP.
2. `app/services/application_service.py` orquesta evaluacion.
3. `app/strategies/factory.py` resuelve politica segun producto.
4. `app/strategies/*.py` aplica reglas y construye resultado.
5. `app/repositories/application_repository.py` persiste/consulta en DB.

## Supuestos y decisiones tecnicas

- Persistencia de `rejection_reasons` en JSON (`list[str]`).
- Criterio de rechazo por regla con codigos estables (ejemplo: `EXTERNAL_SCORE_BELOW_700`).
- `POST /applications` responde `201`.
- `POST /applications/{id}/reevaluate` responde `200` y retorna la entidad actualizada.
- `GET /applications/{id}` responde `404` con `{"detail": "Application not found"}` cuando no existe.
- Se utiliza `Base.metadata.create_all(...)` en arranque para simplicidad de prueba.
- El bonus `reevaluate` queda expuesto en router y cubierto con tests e2e.

## Ejecucion del proyecto

### Requisitos

- Docker Desktop (o Docker Engine + plugin Compose).

### Levantar API

```bash
docker compose up --build
```

Recursos:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Detener

```bash
docker compose down
```

### Reinicio limpio (opcional)

Si quieres empezar sin `credit_eval.db` local:

```bash
docker compose down
rm -f credit_eval.db
docker compose up --build
```

## Ejecucion de tests

### Recomendado (Docker)

Todos los tests:

```bash
docker compose run --rm app pytest -v
```

Solo unitarios de politicas:

```bash
docker compose run --rm app pytest -v tests/test_strategies.py
```

Solo e2e de endpoints:

```bash
docker compose run --rm app pytest -v tests/test_applications_endpoints.py
```

### Local (opcional)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## Estrategia de desarrollo incremental y trazabilidad

Se trabajo con base en el enunciado original `PROBLEM.md` y un plan por fases en `PLAN.md`.

Estrategia aplicada:

1. Analizar enunciado y estructura del repo.
2. Definir `PLAN.md` con fases claras (1 a 10).
3. Implementar cada fase de forma incremental y verificable.
4. Al cerrar cada fase:
   - ejecutar validaciones (tests o smoke checks),
   - crear commit dedicado de la fase,
   - hacer push inmediato para trazabilidad.

Beneficios de este enfoque:

- Control de alcance por fase.
- Facil rollback selectivo.
- Mejor revision de codigo (diffs pequenos y enfocados).
- Evidencia clara de avance tecnico para evaluacion.

## Bonus implementado

- Endpoint `POST /applications/{id}/reevaluate`.
- Cobertura e2e para reevaluacion exitosa y `404` cuando la solicitud no existe.
