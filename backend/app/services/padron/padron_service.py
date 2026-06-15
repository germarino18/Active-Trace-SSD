"""Reglas de negocio de operaciones de padrón (C-09, TASK GROUP 5).

Flujo Routers -> Services -> Repositories -> Models (regla dura #11).
Identidad y `tenant_id` SIEMPRE desde la sesión, nunca de un parámetro
(regla dura #8/#9).

NOTE: `current_user_id` es el User.id (auth identity, usado en audit_log.
actor_id que FK a users). Internamente se resuelve el Usuario.id
(business profile, usado en version_padron.cargado_por que FK a usuario).
"""

import time
import uuid
from typing import Any

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.models.entrada_padron import EntradaPadron
from app.models.usuario import Usuario
from app.models.version_padron import VersionPadron
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.base import BaseRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.services.padron.parse_padron import parse_padron_file

_TOKEN_TTL = 1800  # 30 minutes


class PadronService:
    """Operaciones de padrón (F5): preview, import, consulta, vaciado.

    Preview tokens son almacenados en un dict en memoria (class-level)
    con expiración de 30 minutos. Suficiente para un único request de
    confirmación; en producción migrar a Redis.
    """

    _preview_tokens: dict[str, dict[str, Any]] = {}

    def __init__(self, db_session, tenant_id: uuid.UUID, current_user_id: uuid.UUID):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id
        self._vp_repo = VersionPadronRepository(session=db_session, tenant_id=tenant_id)
        self._ep_repo = EntradaPadronRepository(session=db_session, tenant_id=tenant_id)
        self._audit_repo = AuditLogRepository(session=db_session, tenant_id=tenant_id)

    @classmethod
    def _clean_expired_tokens(cls) -> None:
        now = time.time()
        expired = [k for k, v in cls._preview_tokens.items() if v.get("expires_at", 0) < now]
        for k in expired:
            cls._preview_tokens.pop(k, None)

    async def _get_usuario_id(self) -> uuid.UUID:
        """Resolve Usuario.id from current_user_id (User.id) + tenant_id."""
        repo = BaseRepository(  # type: ignore[type-abstract]
            model=Usuario, session=self.db_session, tenant_id=self.tenant_id
        )
        usuarios = await repo.find_by(user_id=self.current_user_id)
        if not usuarios:
            raise ValidationException(
                message="Perfil de usuario no encontrado",
                details={"user_id": str(self.current_user_id)},
            )
        return usuarios[0].id

    async def preview_archivo(
        self, file_content: bytes, filename: str, dictado_id: uuid.UUID
    ) -> dict[str, Any]:
        """Parse uploaded file, detect columns, generate preview token.

        Returns: {columnas_encontradas, filas, total_filas, preview_token}
        """
        rows, column_names = parse_padron_file(file_content, filename)

        token = uuid.uuid4().hex
        self._preview_tokens[token] = {
            "dictado_id": str(dictado_id),
            "filas": rows,
            "expires_at": time.time() + _TOKEN_TTL,
        }
        self._clean_expired_tokens()

        return {
            "columnas_encontradas": column_names,
            "filas": rows,
            "total_filas": len(rows),
            "preview_token": token,
        }

    async def confirmar_importacion(
        self, dictado_id: uuid.UUID, preview_token: str
    ) -> dict[str, Any]:
        """Validate token, create VersionPadron + EntradaPadron, deactivate previous.

        Returns: {version_id, total_importados, mensaje}
        """
        cached = self._preview_tokens.pop(preview_token, None)
        if cached is None:
            raise ValidationException(
                message="Token de preview inválido o expirado",
                details={"preview_token": preview_token},
            )
        self._clean_expired_tokens()

        if cached["dictado_id"] != str(dictado_id):
            raise ValidationException(
                message="El token de preview no corresponde a este dictado",
                details={"expected_dictado": cached["dictado_id"], "received_dictado": str(dictado_id)},
            )

        filas = cached["filas"]
        if not filas:
            raise ValidationException(
                message="No hay filas para importar",
            )

        previous_active = await self._vp_repo.find_active_by_dictado(dictado_id)

        # Deactivate previous active version BEFORE creating the new one
        # to avoid unique constraint violation on ix_version_padron_dictado_activa.
        if previous_active is not None:
            await self._vp_repo.deactivate_version(previous_active.id)

        usuario_id = await self._get_usuario_id()

        version = await self._vp_repo.create({
            "dictado_id": dictado_id,
            "cargado_por": usuario_id,
            "activa": True,
        })

        entries_data = []
        for fila in filas:
            entry = {
                "version_id": version.id,
                "nombre": fila.get("nombre", ""),
                "apellidos": fila.get("apellidos", ""),
                "email": fila.get("email"),
                "comision": fila.get("comision"),
                "regional": fila.get("regional"),
            }
            entries_data.append(entry)

        await self._ep_repo.bulk_create(entries_data)

        await self._audit_repo.create({
            "tenant_id": self.tenant_id,
            "actor_id": self.current_user_id,
            "accion": AccionAuditoria.PADRON_CARGAR,
            "detalle": {
                "dictado_id": str(dictado_id),
                "version_id": str(version.id),
                "total_importados": len(filas),
            },
            "filas_afectadas": len(filas),
        })

        return {
            "version_id": version.id,
            "total_importados": len(filas),
            "mensaje": f"Se importaron {len(filas)} registros correctamente",
        }

    async def obtener_padron_activo(self, dictado_id: uuid.UUID) -> list[EntradaPadron]:
        """Return entries of the active version for this dictado."""
        active_version = await self._vp_repo.find_active_by_dictado(dictado_id)
        if active_version is None:
            return []
        return await self._ep_repo.find_by_version(active_version.id)

    async def listar_versiones(self, dictado_id: uuid.UUID) -> list[VersionPadron]:
        """Return history of versions for a dictado (most recent first)."""
        return await self._vp_repo.find_by_dictado(dictado_id)

    async def vaciar_dictado(
        self, dictado_id: uuid.UUID, current_user_id: uuid.UUID, es_coordinador: bool = False
    ) -> dict[str, Any]:
        """Scope-isolated delete per RN-04.

        - If es_coordinador: delete ALL versions for this dictado
        - If profesor: delete ONLY versions created by this user
        Returns: {dictado_id, entradas_eliminadas, mensaje}
        """
        if es_coordinador:
            entradas_eliminadas = await self._vp_repo.delete_all_by_dictado(dictado_id)
        else:
            usuario_id = await self._get_usuario_id()
            entradas_eliminadas = await self._vp_repo.delete_by_dictado_and_cargador(
                dictado_id, usuario_id
            )

        await self._audit_repo.create({
            "tenant_id": self.tenant_id,
            "actor_id": current_user_id,
            "accion": AccionAuditoria.PADRON_VACIAR,
            "detalle": {
                "dictado_id": str(dictado_id),
                "es_coordinador": es_coordinador,
            },
            "filas_afectadas": entradas_eliminadas,
        })

        return {
            "dictado_id": dictado_id,
            "entradas_eliminadas": entradas_eliminadas,
            "mensaje": f"Se eliminaron {entradas_eliminadas} versiones del padrón",
        }
