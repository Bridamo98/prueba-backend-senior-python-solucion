# PLAN - Implementacion de evaluacion de credito

## 1) Objetivo

Implementar un servicio HTTP con FastAPI + SQLAlchemy que:

- Evalue solicitudes de credito segun politicas por producto (`PHONE`, `TWIST`, `CARD`).
- Persista solicitud, decision (`APPROVED`/`REJECTED`) y razones de rechazo.
- Exponga endpoints:
  - `POST /applications`
  - `GET /applications/{id}`
  - `GET /applications?status=...&product=...`
- Cumpla la restriccion de diseno:
  - Sin `if/elif` de politicas dentro del endpoint.
  - DB desacoplada del endpoint mediante repositorio/servicio.
- Incluya tests minimos exigidos y e2e.

## 2) Estado actual (baseline)

- Existe `GET /health` en `app/main.py`.
- Config DB lista en `app/database.py`.
- `app/models.py`, `app/schemas.py` y capas `repositories/services/strategies` estan vacias o placeholder.
- Solo hay test de salud en `tests/test_health.py`.

## 3) Supuestos y decisiones de diseno

- **Cuota mensual**: `amount / 12` (float), comparada contra porcentaje de `monthly_income`.
- **Razones de rechazo**: lista de strings (`list[str]`) persistida en columna JSON.
- **Enums de dominio**:
  - `ProductType`: `PHONE`, `TWIST`, `CARD`
  - `ApplicationStatus`: `APPROVED`, `REJECTED`
- **HTTP codes**:
  - `POST /applications` -> `201`
  - `GET /applications/{id}` -> `200` o `404`
  - `GET /applications` -> `200`
- **Bonus** `reevaluate`: se deja planificado como opcional al final.

## 4) Arquitectura propuesta

- **Estrategias (`app/strategies/`)**
  - Una clase por politica (`PhonePolicy`, `TwistPolicy`, `CardPolicy`).
  - Metodo estandar: `evaluate(input) -> EvaluationResult`.
  - `PolicyFactory` (mapa producto->estrategia) para evitar `if/elif` en endpoint.
- **Repositorio (`app/repositories/`)**
  - Encapsula acceso SQLAlchemy (`create`, `get_by_id`, `list` con filtros, `update_decision`).
- **Servicio (`app/services/`)**
  - Orquesta evaluacion + persistencia.
  - Logica de aplicacion sin detalles HTTP.
- **Router (`app/routers/`)**
  - Parseo request/response y dependencia de DB.
  - Delega al servicio.

## 5) Cambios por archivo

### `app/models.py`

- Crear modelo `Application` con:
  - `id` (PK)
  - `amount` (int, not null)
  - `monthly_income` (int, not null)
  - `employment_months` (int, not null)
  - `external_score` (int, not null)
  - `product` (str/enum, not null)
  - `status` (str/enum, not null)
  - `rejection_reasons` (JSON, not null, default `[]`)
  - `created_at`, `updated_at` (timestamps)

### `app/schemas.py`

- Agregar schemas:
  - `ApplicationCreateRequest`
  - `ApplicationResponse`
  - `ApplicationListResponse` (o lista directa de `ApplicationResponse`)
  - `EvaluationResultSchema` (si se requiere intermedio)
- Validaciones:
  - `amount > 0`
  - `monthly_income > 0`
  - `employment_months >= 0`
  - `external_score` entre 0 y 1000
  - `product` enum

### `app/strategies/base.py` (nuevo)

- `EvaluationInput` y `EvaluationResult`.
- `BasePolicy` abstracta con `evaluate`.

### `app/strategies/phone.py` (nuevo)

- Reglas:
  - `score >= 700`
  - `employment_months >= 12`
  - `cuota <= 25% ingreso`
- Construir razones especificas cuando falla.

### `app/strategies/twist.py` (nuevo)

- Reglas:
  - `score >= 600`
  - `cuota <= 35% ingreso`

### `app/strategies/card.py` (nuevo)

- Regla:
  - `score >= 550` OR (`score >= 500` AND `monthly_income >= 3_000_000`)

### `app/strategies/factory.py` (nuevo)

- Registro estatico de politicas por producto.
- Retorna politica segun enum `ProductType`.

### `app/repositories/application_repository.py` (nuevo)

- Metodos:
  - `create(...)`
  - `get_by_id(application_id)`
  - `list(status=None, product=None)`
  - `update_decision(application, status, reasons)` (si aplica para bonus)

### `app/services/application_service.py` (nuevo)

- Metodos:
  - `create_application(request)`
    - arma `EvaluationInput`
    - evalua con factory
    - persiste y retorna entidad
  - `get_application(id)`
  - `list_applications(status, product)`
  - `reevaluate(id)` (opcional/bonus)

### `app/routers/applications.py` (nuevo)

- Endpoints:
  - `POST /applications`
  - `GET /applications/{id}`
  - `GET /applications`
  - `POST /applications/{id}/reevaluate` (bonus opcional)
- Manejo `404` cuando no exista la solicitud.

### `app/main.py`

- Incluir router de aplicaciones.
- Mantener `health`.
- `Base.metadata.create_all(bind=engine)` puede mantenerse para esta prueba.

### `tests/conftest.py` (nuevo)

- Configurar DB SQLite de test (aislada).
- Fixtures de `TestClient` y sesion.

### `tests/test_strategies.py` (nuevo)

- Unit tests de politicas:
  - Aprobacion y rechazo `PHONE`.
  - Aprobacion y rechazo `TWIST`.
  - Aprobacion y rechazo `CARD`.
  - Verificar razones de rechazo correctas.

### `tests/test_applications_endpoints.py` (nuevo)

- E2E:
  - `POST /applications` persiste y retorna decision.
  - `GET /applications/{id}` devuelve registro.
  - `GET /applications` sin filtros y con filtros (`status`, `product`).
  - `GET /applications/{id}` inexistente -> `404`.
  - Casos de rechazo por cada politica.

## 6) Secuencia de ejecucion sugerida

1. Definir enums/schemas de entrada y salida.
2. Implementar modelo `Application` y crear tablas.
3. Implementar estrategias + factory.
4. Implementar repositorio.
5. Implementar servicio.
6. Implementar router y registrar en `main.py`.
7. Escribir tests unitarios de estrategias.
8. Escribir tests e2e de endpoints.
9. Ejecutar test suite y corregir fallos.
10. Documentar supuestos en `README.md` (seccion breve).

## 7) Criterios de aceptacion (DoD)

- Endpoints requeridos funcionando con contratos claros.
- Persistencia completa de solicitud, estado y razones.
- Seleccion de politica desacoplada del endpoint.
- Acceso DB desacoplado del endpoint (repositorio/servicio).
- Tests cubren:
  - al menos una aprobacion
  - un rechazo por cada politica
  - flujo e2e
- `pytest` en verde.

## 8) Verificacion tecnica

- Local:
  - `pytest -v`
- Docker:
  - `docker compose up --build`
  - `docker compose run --rm app pytest -v`
- Verificacion manual:
  - `/docs`
  - probar casos aprobados/rechazados por producto
  - validar filtros en listado

## 9) Riesgos y mitigaciones

- **Riesgo**: logica dispersa entre endpoint y service.  
  **Mitigacion**: endpoint solo hace I/O HTTP; service concentra negocio.
- **Riesgo**: tests acoplados a DB real local.  
  **Mitigacion**: fixtures con DB de test aislada.
- **Riesgo**: inconsistencias en razones de rechazo.  
  **Mitigacion**: catalogo fijo de mensajes y asserts exactos en tests.

## 10) Bonus (opcional)

- Implementar `POST /applications/{id}/reevaluate`.
- Recalcular con politica actual y actualizar `status/rejection_reasons`.
- Agregar tests de reevaluacion (cambio de outcome si se modifica input o politica).
