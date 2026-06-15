"""UmbralService — Configuración y consulta de umbral de aprobación (C-10 TASKS 24-26).

Permite obtener/establecer el umbral de aprobación por dictado, con
recalculo automático de calificaciones al cambiar.
"""

import uuid
from typing import Any

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository

_DEFAULT_UMBRAL_PCT = 60
_DEFAULT_VALORES_APROBATORIOS = ["Satisfactorio", "Supera lo esperado"]


class UmbralService:
    def __init__(self, db_session, tenant_id: uuid.UUID, current_user_id: uuid.UUID):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id
        self.umbral_repo = UmbralMateriaRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.calificacion_repo = CalificacionRepository(
            session=db_session, tenant_id=tenant_id
        )

    async def _get_asignacion_id(self, dictado_id: uuid.UUID) -> uuid.UUID | None:
        """Resolve current user's assignment for this dictado."""
        from app.models.asignacion import Asignacion
        from app.models.usuario import Usuario
        from app.repositories.base import BaseRepository

        from datetime import date

        usuario_repo = BaseRepository(
            model=Usuario, session=self.db_session, tenant_id=self.tenant_id
        )
        usuarios = await usuario_repo.find_by(user_id=self.current_user_id)
        if not usuarios:
            return None

        usuario_id = usuarios[0].id
        asignacion_repo = BaseRepository(
            model=Asignacion, session=self.db_session, tenant_id=self.tenant_id
        )
        asignaciones = await asignacion_repo.find_by(
            usuario_id=usuario_id,
            dictado_id=dictado_id,
        )
        if not asignaciones:
            return None

        hoy = date.today()
        for a in asignaciones:
            if a.desde <= hoy and (a.hasta is None or hoy <= a.hasta):
                return a.id

        return None

    async def obtener_umbral(self, dictado_id: uuid.UUID) -> dict[str, Any]:
        """Get current threshold, with fallback to defaults."""
        asignacion_id = await self._get_asignacion_id(dictado_id)
        if not asignacion_id:
            return {
                "umbral_pct": _DEFAULT_UMBRAL_PCT,
                "valores_aprobatorios": _DEFAULT_VALORES_APROBATORIOS,
                "es_default": True,
            }

        umbral = await self.umbral_repo.find_by_asignacion_dictado(
            asignacion_id, dictado_id
        )
        if not umbral:
            return {
                "umbral_pct": _DEFAULT_UMBRAL_PCT,
                "valores_aprobatorios": _DEFAULT_VALORES_APROBATORIOS,
                "es_default": True,
            }

        return {
            "umbral_pct": umbral.umbral_pct,
            "valores_aprobatorios": umbral.valores_aprobatorios,
            "es_default": False,
        }

    async def configurar_umbral(
        self,
        dictado_id: uuid.UUID,
        umbral_pct: int,
        valores_aprobatorios: list[str] | None = None,
    ) -> dict[str, Any]:
        """Configure threshold: upsert + recalculate + audit."""
        if umbral_pct < 0 or umbral_pct > 100:
            raise ValueError("umbral_pct debe estar entre 0 y 100")

        asignacion_id = await self._get_asignacion_id(dictado_id)
        if not asignacion_id:
            raise ValidationException(
                message="No tienes asignación para este dictado",
                details={"dictado_id": str(dictado_id)},
            )

        umbral = await self.umbral_repo.upsert(
            asignacion_id, dictado_id, umbral_pct, valores_aprobatorios
        )

        updated = await self.calificacion_repo.recalcular_aprobado_por_dictado(
            dictado_id, umbral_pct, valores_aprobatorios
        )

        return {
            "umbral_pct": umbral.umbral_pct,
            "valores_aprobatorios": umbral.valores_aprobatorios,
            "calificaciones_recalculadas": updated,
        }
