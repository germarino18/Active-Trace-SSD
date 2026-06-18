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
| Auth | JWT + Argon2id + TOTP 2FA |
| Testing | pytest + coverage |

### Frontend
| Componente | Tecnología |
|------------|-----------|
| Framework | React 18 + TypeScript |
| Bundler | Vite 6 |
| Server state | TanStack Query v5 |
| Forms | React Hook Form + Zod |
| Estilos | Tailwind CSS v4 |
| HTTP | Axios |
| Diseño | **Obsidian** — High-Contrast Dark (por Stitch Google MCP) |

---

## Requisitos

- **Docker** + Docker Compose (recomendado)
- O alternativamente: Python 3.13, Node.js 20+, PostgreSQL 16

---

## Levantar el proyecto

### 1. Clonar y preparar configuración

```bash
git clone <repo-url>
cd activia-trace

# Crear .env del backend desde el template
cp backend/.env.example backend/.env
```

Editar `backend/.env` y al menos cambiar:
- `SECRET_KEY` — mínimo 32 caracteres (para firmar JWT)
- `ENCRYPTION_KEY` — hex string de 64 caracteres (para cifrado AES-256 de PII)

### 2. Opción A — Todo con Docker (recomendado)

```bash
docker compose up --build
```

Esto levanta 4 servicios:

| Servicio | Puerto | URL |
|----------|--------|-----|
| **Frontend** (Vite dev + HMR) | `5173` | http://localhost:5173 |
| **Backend** (FastAPI) | `8000` | http://localhost:8000/docs |
| **PostgreSQL** | `5434` | `localhost:5434` |
| **Worker** (cola de comunicaciones) | — | interno |

El frontend proxy automáticamente los `/api/*` al backend (sin CORS en dev).

### 3. Opción B — Frontend local + Backend en Docker

Para desarrollo frontend con hot reload más rápido:

```bash
# Terminal 1: Backend + DB en Docker
docker compose up api postgres

# Terminal 2: Frontend en local
cd frontend
npm install
npm run dev -- --host
```

### 4. Sembrar datos de prueba

Si la base de datos está vacía, ejecutá las migraciones de Alembic:

```bash
# Dentro del contenedor del backend
docker compose exec api alembic upgrade head
```

Luego podés crear un tenant y usuario vía API o esperar a que se agregue un script de seed.

---

## Probar la app

1. Abrí http://localhost:5173
2. Te va a pedir:
   - **Email** y **contraseña**
   - **X-Tenant-ID** (UUID del tenant al que pertenece el usuario)
3. Si el usuario tiene 2FA habilitado, pedirá el código TOTP
4. Una vez autenticado → **Dashboard** con el layout **Obsidian dark**

### Documentación de la API

http://localhost:8000/docs (Swagger UI, solo si el backend está corriendo)

---

## Estructura del proyecto

```
activia-trace/
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/   ← Endpoints por dominio
│   │   ├── core/             ← Config, seguridad, dependencias
│   │   ├── models/           ← SQLAlchemy (47 modelos)
│   │   ├── schemas/          ← Pydantic DTOs
│   │   ├── repositories/     ← Queries con scope de tenant
│   │   ├── services/         ← Lógica de negocio
│   │   ├── integrations/     ← Moodle WS, N8N
│   │   └── workers/          ← Cola de comunicaciones
│   ├── alembic/              ← Migraciones
│   └── tests/                ← Suite de pytest
├── frontend/
│   └── src/
│       ├── features/         ← Módulos por dominio (auth, layout, etc.)
│       ├── pages/            ← Páginas standalone
│       ├── shared/           ← HTTP client, componentes UI
│       └── test/             ← Tests con Vitest + RTL
├── docs/
│   ├── ARQUITECTURA.md       ← Documentación técnica
│   ├── PRD.md                ← Requerimientos de producto
│   └── design/stitch-obsidian/ ← Mockups visuales (Stitch)
├── knowledge-base/           ← Base de conocimiento del dominio
├── openspec/                 ← Changes y especificaciones
├── CHANGES.md                ← Roadmap de implementación
└── docker-compose.yml
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

| # | Change | Estado |
|---|--------|--------|
| C-01 → C-20 | Backend completo (infra, auth, RBAC, estructura académica, calificaciones, comunicaciones, liquidaciones, etc.) | ✅ |
| **C-21** | **Frontend shell + auth (login, layout, guards)** | **✅** |
| C-22 | Frontend académico-docente | 🔲 |
| C-23 | Frontend coordinación | 🔲 |
| C-24 | Frontend finanzas y admin | 🔲 |

Ver detalle completo en [`CHANGES.md`](CHANGES.md).

---

## Comandos útiles

```bash
# Backend — correr tests
docker compose exec api pytest -v

# Backend — ver logs
docker compose logs -f api

# Backend — shell dentro del contenedor
docker compose exec api bash

# Frontend — correr tests
cd frontend && npm run test -- --run

# Frontend — build producción
cd frontend && npm run build

# Detener todo
docker compose down

# Detener y borrar volúmenes (pierde datos de DB)
docker compose down -v
```
