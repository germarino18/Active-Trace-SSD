"""Tests for §3.4 actividad_id/actividad invariant.

When a Calificacion is created referencing an actividad_id,
the string actividad field MUST equal Actividad.nombre (invariant).
"""

import datetime
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.user import User
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.actividad_repository import ActividadRepository
from app.repositories.base import BaseRepository
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.dictado_repository import DictadoRepository
from app.schemas.actividades import ActividadCreate
from app.services.actividad_service import ActividadService


async def _create_dictado_with_padron(
    db_session: AsyncSession, tenant_id: uuid.UUID
) -> dict:
    """Create a full dictado structure with one entrada_padron."""
    c_repo = BaseRepository(model=Carrera, session=db_session, tenant_id=tenant_id)
    carrera = await c_repo.create({"codigo": f"C-{uuid.uuid4().hex[:4]}", "nombre": "Carrera"})
    m_repo = BaseRepository(model=Materia, session=db_session, tenant_id=tenant_id)
    materia = await m_repo.create({"codigo": f"M-{uuid.uuid4().hex[:4]}", "nombre": "Materia"})
    co_repo = BaseRepository(model=Cohorte, session=db_session, tenant_id=tenant_id)
    cohorte = await co_repo.create({"carrera_id": carrera.id, "nombre": "2024", "anio": 2024})
    d_repo = DictadoRepository(session=db_session, tenant_id=tenant_id)
    dictado = await d_repo.create(
        {"materia_id": materia.id, "carrera_id": carrera.id, "cohorte_id": cohorte.id}
    )

    # Create a real usuario for cargado_por FK
    user_repo = BaseRepository(model=User, session=db_session, tenant_id=tenant_id)
    user = await user_repo.create(
        {
            "email": f"test-{uuid.uuid4().hex[:8]}@inv.com",
            "password_hash": "hash",
            "display_name": "Test",
            "is_active": True,
            "roles": [],
        }
    )
    u_repo = BaseRepository(model=Usuario, session=db_session, tenant_id=tenant_id)
    usuario = await u_repo.create(
        {"user_id": user.id, "nombre": "Test", "apellidos": "User", "estado": "Activo", "facturador": False}
    )

    vp_repo = BaseRepository(model=VersionPadron, session=db_session, tenant_id=tenant_id)
    version = await vp_repo.create(
        {"dictado_id": dictado.id, "cargado_por": usuario.id, "activa": True}
    )
    ep_repo = BaseRepository(model=EntradaPadron, session=db_session, tenant_id=tenant_id)
    entrada = await ep_repo.create(
        {"version_id": version.id, "nombre": "Juan", "apellidos": "Pérez", "email": "j@t.com"}
    )
    return {"dictado": dictado, "entrada": entrada}


class TestActividadCalificacionInvariant:
    """§3.4: Calificacion.actividad must equal Actividad.nombre when actividad_id is set."""

    async def test_calificacion_actividad_string_equals_nombre(
        self, db_session: AsyncSession, test_tenant
    ):
        """GREEN: cuando se crea Calificacion con actividad_id, actividad == nombre."""
        data = await _create_dictado_with_padron(db_session, test_tenant.id)
        dictado = data["dictado"]
        entrada = data["entrada"]

        # Create actividad
        svc = ActividadService.create(db_session, test_tenant.id)
        actividad = await svc.crear(
            dictado.id, ActividadCreate(nombre="TP1 Especial", tipo="TP")
        )

        # Create calificacion enforcing the invariant
        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        calificacion = await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": dictado.id,
                "actividad": actividad.nombre,  # ← invariant: same as Actividad.nombre
                "actividad_id": actividad.id,
                "nota_numerica": 8.0,
                "aprobado": True,
                "origen": "Manual",
            }
        )

        assert calificacion.actividad == actividad.nombre
        assert calificacion.actividad_id == actividad.id

    async def test_invariant_actividad_string_must_match_actividad_nombre(
        self, db_session: AsyncSession, test_tenant
    ):
        """TRIANGULATE: calificacion.actividad == calificacion.actividad_id's nombre."""
        data = await _create_dictado_with_padron(db_session, test_tenant.id)
        dictado = data["dictado"]
        entrada = data["entrada"]

        svc = ActividadService.create(db_session, test_tenant.id)
        actividad = await svc.crear(
            dictado.id, ActividadCreate(nombre="Parcial 2", tipo="Parcial")
        )

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        calificacion = await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": dictado.id,
                "actividad": actividad.nombre,
                "actividad_id": actividad.id,
                "aprobado": False,
                "origen": "Manual",
            }
        )

        # Reload actividad from DB and verify invariant
        act_repo = ActividadRepository(session=db_session, tenant_id=test_tenant.id)
        loaded_act = await act_repo.find_by_id(actividad.id)
        assert calificacion.actividad == loaded_act.nombre

    async def test_calificacion_without_actividad_id_still_works(
        self, db_session: AsyncSession, test_tenant
    ):
        """TRIANGULATE: Calificacion sin actividad_id (legacy) sigue funcionando."""
        data = await _create_dictado_with_padron(db_session, test_tenant.id)
        dictado = data["dictado"]
        entrada = data["entrada"]

        calif_repo = CalificacionRepository(session=db_session, tenant_id=test_tenant.id)
        calificacion = await calif_repo.create(
            {
                "entrada_padron_id": entrada.id,
                "dictado_id": dictado.id,
                "actividad": "TP Legacy",  # ← string-only, no actividad_id
                "nota_numerica": 7.5,
                "aprobado": True,
                "origen": "Importado",
            }
        )

        assert calificacion.actividad == "TP Legacy"
        assert calificacion.actividad_id is None
