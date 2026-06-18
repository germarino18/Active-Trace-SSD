# activia-trace

Plataforma de gestión académica y trazabilidad multi-tenant con integración a Moodle.

**activia-trace** consolida calificaciones, detecta atrasos, gestiona comunicación saliente con aprobación, equipos docentes, encuentros, coloquios, liquidaciones de honorarios y auditoría completa. Cada institución es un tenant aislado.

---

## Stack

### Backend
| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.13 |
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| Migraciones | Alembic |
| Base de datos | PostgreSQL 16 |
| Validación | Pydantic v2 |
| Auth | JWT (access corto + refresh rotation) + Argon2id + TOTP 2FA |
| Cifrado en reposo | AES-256 para PII |
| Testing | pytest + coverage |
| Observabilidad | OpenTelemetry |

### Frontend
| Componente | Tecnología |
|------------|-----------|
| Framework | React 18 + TypeScript |
| Bundler | Vite 6 |
| Server state | TanStack Query v5 |
| Forms | React Hook Form + Zod |
| Estilos | Tailwind CSS v4 |
| HTTP | Axios |
| Testing | Vitest + React Testing Library |
| Diseño | **Obsidian** — High-Contrast Dark |

---

## Requisitos

- **Docker** + Docker Compose (recomendado)
- O alternativamente: Python 3.13, Node.js 20+, PostgreSQL 16

---

## Paso a paso — levantar el proyecto desde 0

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd activia-trace
```

### 2. Crear archivo de configuración del backend

```bash
cp backend/.env.example backend/.env
```

Editar `backend/.env` y cambiar las claves por valores seguros:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Firma JWT (mín. 32 caracteres) | `cambiar-por-una-clave-muy-segura-de-al-menos-32` |
| `ENCRYPTION_KEY` | Cifrado AES-256 para PII (hex 64 chars = 32 bytes) | `0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef` |

El resto de las variables ya vienen con defaults funcionales para desarrollo local.

### 3. Opción A — Todo con Docker (recomendado)

```bash
docker compose up --build
```

Esto levanta 4 servicios:

| Servicio | Puerto | URL |
|----------|--------|-----|
| **Frontend** (Vite dev + HMR) | `5173` | http://localhost:5173 |
| **Backend** (FastAPI + Swagger) | `8000` | http://localhost:8000/docs |
| **PostgreSQL 16** | `5434` | `localhost:5434` |
| **Worker** (cola de comunicaciones async) | — | interno |

El frontend proxy automáticamente los `/api/*` al backend (sin CORS en dev).

> ⏳ La primera vez Docker descarga las imágenes y builda todo. Puede llevar varios minutos.

### 4. Opción B — Frontend local + Backend en Docker

Para desarrollo frontend con hot reload más rápido (sin pasar por el Dockerfile del frontend):

```bash
# Terminal 1: Backend + DB + Worker en Docker
docker compose up api postgres worker

# Terminal 2: Frontend en local
cd frontend
npm install
npm run dev
```

### 5. Correr migraciones de base de datos

Con los servicios ya levantados, ejecutá las migraciones de Alembic:

```bash
docker compose exec api alembic upgrade head
```

Esto crea todas las tablas del sistema (~47 modelos).

### 6. Sembrar datos de prueba

```bash
docker compose exec api python /app/seed_dev.py
```

Esto crea:
- **Tenant**: Universidad Tecnológica Nacional (slug: `utn`)
- **Usuarios** (password: `admin123`):

| Email | Rol |
|-------|-----|
| admin@utn.edu.ar | ADMIN |
| coordinador@utn.edu.ar | COORDINADOR |
| profesor@utn.edu.ar | PROFESOR |

- **Estructura académica**: Carrera ING-SIS, 2 materias (MAT-101, PROG-101), cohorte 2025
- **Alumnos**: 5 alumnos en MAT-101 con calificaciones (promocionado, regular, desaprobado, faltante, textual)
- **Roles, permisos y matriz** de autorización completa

> ⚠️ Si corrés el seed varias veces, es **idempotente**: hace upsert en lugar de duplicar.

### 7. Ingresar a la app

1. Abrí http://localhost:5173
2. Iniciá sesión con:
   - **Email**: `admin@utn.edu.ar`
   - **Contraseña**: `admin123`
   - **X-Tenant-ID**: dejalo vacío (el backend resuelve el tenant automáticamente si hay un solo tenant)

3. Una vez autenticado → **Dashboard** con layout **Obsidian dark**

---

## Tests

### Backend (pytest)

```bash
# Tests con la DB de desarrollo (requiere postgres corriendo)
docker compose exec api pytest -v

# O contra una DB de test dedicada (puerto 5433)
docker compose -f docker-compose.test.yml up -d postgres-test
cd backend
pip install -e ".[dev]"
pytest -v --asyncio-mode=auto
```

**Cobertura esperada**: ≥80% líneas, ≥90% reglas de negocio.

### Frontend (Vitest)

```bash
cd frontend
npm run test:run        # una sola ejecución
npm run test            # modo watch
npm run test -- --ui    # UI interactiva

# Conteo actual:
# 43 test files, 243 tests, 0 failures
```

---

## Estructura del proyecto

```
activia-trace/
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/     ← 25 routers por dominio
│   │   ├── core/               ← Config, database, seguridad, logging
│   │   ├── models/             ← SQLAlchemy (47 modelos)
│   │   ├── schemas/            ← Pydantic DTOs (extra='forbid')
│   │   ├── repositories/       ← Queries con scope de tenant
│   │   ├── services/           ← Lógica de negocio
│   │   ├── integrations/       ← Moodle WS, N8N
│   │   └── workers/            ← Cola de comunicaciones
│   ├── alembic/                ← Migraciones (una por cambio de schema)
│   ├── tests/                  ← Suite de pytest (35 módulos)
│   └── seed_dev.py             ← Seed de datos de desarrollo
├── frontend/
│   └── src/
│       ├── features/
│       │   ├── auth/           ← Login, 2FA, reset password, guards
│       │   ├── layout/         ← AppLayout, sidebar, theme
│       │   ├── academico/      ← Docente: atrasados, calificaciones, programas
│       │   ├── coordinacion/   ← Equipos, encuentros, convocatorias, monitores
│       │   ├── finanzas/       ← Liquidaciones, grilla salarial, facturas
│       │   └── admin/          ← Estructura académica, usuarios, auditoría, métricas
│       ├── shared/             ← HTTP client, componentes UI, tipos comunes
│       └── test/               ← Tests con Vitest + RTL (43 archivos)
├── docs/
│   ├── ARQUITECTURA.md         ← Documentación técnica
│   ├── PRD.md                  ← Requerimientos de producto
│   └── design/                 ← Mockups visuales (Stitch)
├── knowledge-base/             ← Base de conocimiento del dominio (10 archivos)
├── openspec/                   ← Especificaciones y changes
│   ├── specs/                  ← Specs canónicos por capacidad
│   └── changes/                ← Changes activos y archivados
├── CHANGES.md                  ← Roadmap de implementación
├── docker-compose.yml          ← Servicios: api, frontend, postgres, worker
└── docker-compose.test.yml     ← PostgreSQL para tests
```

### Feature modules (frontend)

Cada feature sigue la misma estructura interna:

```
features/{nombre}/
├── components/    ← Componentes UI (tablas, formularios, modales, charts)
├── hooks/         ← Hooks con TanStack Query (queries + mutations)
├── services/      ← Llamadas HTTP a la API con Axios
├── types/         ← TypeScript interfaces y tipos
└── pages/         ← Página principal del feature (ruteable)
```

---

## Design System: Obsidian

El diseño visual sigue el tema **Obsidian — High-Contrast Dark** (generado con Stitch Google MCP).

| Token | Valor |
|-------|-------|
| Fondo | `#09090b` (near-black) |
| Primary | `#a78bfa` (violeta) |
| Tertiary (éxito) | `#34d399` (esmeralda) |
| Error | `#ef4444` |
| Tipografía | Geist |
| Íconos | Material Symbols Outlined |

Los mockups de referencia están en `docs/design/stitch-obsidian/`.

---

## Changes (roadmap)

Estado actual — todos completos:

| # | Change | Estado |
|---|--------|--------|
| C-01 → C-20 | Backend completo (infra, auth, RBAC, estructura académica, calificaciones, comunicaciones, liquidaciones, etc.) | ✅ |
| C-21 | Frontend shell + auth (login, layout, guards) | ✅ |
| C-22 | Frontend académico-docente | ✅ |
| C-23 | Frontend coordinación | ✅ |
| C-24 | Frontend finanzas y admin | ✅ |

Ver detalle completo en [`CHANGES.md`](CHANGES.md) (24 changes, 6 fases).

---

## Comandos útiles

```bash
# ── Backend ──

# Migraciones
docker compose exec api alembic upgrade head        # aplicar migraciones
docker compose exec api alembic downgrade -1        # revertir última
docker compose exec api alembic revision --autogenerate -m "desc"  # crear migración

# Tests
docker compose exec api pytest -v                   # correr tests
docker compose exec api pytest -v -k "test_name"    # filtrar por nombre

# Seed de datos
docker compose exec api python /app/seed_dev.py

# Logs
docker compose logs -f api
docker compose logs -f frontend

# Shell
docker compose exec api bash

# ── Frontend ──

cd frontend
npm run dev                  # servidor de desarrollo
npm run test:run             # tests (una vez)
npm run test -- --ui         # tests con UI interactiva
npm run build                # build de producción
npm run typecheck            # type-check sin emitir

# ── Docker ──

docker compose up --build     # levantar todo
docker compose down           # detener
docker compose down -v        # detener + borrar volúmenes (pierde datos)
docker compose ps             # estado de servicios
```

---

## Documentación de la API

Con el backend corriendo: http://localhost:8000/docs (Swagger UI, autogenerado desde FastAPI).

También: http://localhost:8000/redoc (ReDoc, alternativa más legible).

---

## Licencia

Uso interno. Código propietario.
