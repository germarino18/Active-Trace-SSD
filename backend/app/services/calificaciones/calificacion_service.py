"""CalificacionService — Importación y consulta de calificaciones (C-10 TASKS 16-18).

Flujo: preview_archivo (parsing + token) → confirmar_importacion (persist + audit).
También: finalización preview/confirm, listar, recalcular por cambio de umbral.
"""

import time
import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import ValidationException
from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.entrada_padron_repository import EntradaPadronRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository
from app.repositories.version_padron_repository import VersionPadronRepository
from app.services.calificaciones.parse_calificaciones import (
    detectar_tps_sin_calificar,
    parse_calificaciones_file,
    parse_finalizacion_file,
)

_TOKEN_TTL = 1800  # 30 minutes

_DEFAULT_UMBRAL_PCT = 60
_DEFAULT_VALORES_APROBATORIOS = ["Satisfactorio", "Supera lo esperado"]


class CalificacionService:
    _preview_tokens: dict[str, dict[str, Any]] = {}

    def __init__(self, db_session, tenant_id: uuid.UUID, current_user_id: uuid.UUID):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id
        self.calificacion_repo = CalificacionRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.umbral_repo = UmbralMateriaRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.vp_repo = VersionPadronRepository(
            session=db_session, tenant_id=tenant_id
        )
        self.ep_repo = EntradaPadronRepository(
            session=db_session, tenant_id=tenant_id
        )

    @classmethod
    def _clean_expired_tokens(cls) -> None:
        now = time.time()
        expired = [
            k
            for k, v in cls._preview_tokens.items()
            if v.get("expires_at", 0) < now
        ]
        for k in expired:
            cls._preview_tokens.pop(k, None)

    async def _get_version_entradas(
        self, dictado_id: uuid.UUID
    ) -> list[dict]:
        """Get active version's entrada_padron records for student matching."""
        active_version = await self.vp_repo.find_active_by_dictado(dictado_id)
        if active_version is None:
            return []
        entradas = await self.ep_repo.find_by_version(active_version.id)
        return [
            {
                "id": e.id,
                "nombre": (e.nombre or "").strip().lower(),
                "apellidos": (e.apellidos or "").strip().lower(),
            }
            for e in entradas
        ]

    def _match_entrada(
        self, nombre: str, apellidos: str, entradas: list[dict]
    ) -> uuid.UUID | None:
        n = nombre.strip().lower()
        a = apellidos.strip().lower()
        for e in entradas:
            if e["nombre"] == n and e["apellidos"] == a:
                return e["id"]
        return None

    async def preview_archivo(
        self, file_content: bytes, filename: str, dictado_id: uuid.UUID
    ) -> dict[str, Any]:
        """Parse file, detect activities, match students, generate preview token."""
        parsed = parse_calificaciones_file(file_content, filename)
        entradas = await self._get_version_entradas(dictado_id)

        filas = parsed["filas"]
        for fila in filas:
            entrada_id = self._match_entrada(
                fila.get("alumno_nombre", ""),
                fila.get("alumno_apellidos", ""),
                entradas,
            )
            fila["entrada_padron_id"] = entrada_id

        token = uuid4().hex
        self._preview_tokens[token] = {
            "dictado_id": str(dictado_id),
            "filas": filas,
            "actividades": parsed["actividades"],
            "expires_at": time.time() + _TOKEN_TTL,
        }
        self._clean_expired_tokens()

        return {
            "actividades_detectadas": parsed["actividades"],
            "filas": filas[:10],
            "total_filas": parsed["total_filas"],
            "preview_token": token,
        }

    async def confirmar_importacion(
        self,
        dictado_id: uuid.UUID,
        preview_token: str,
        actividades_seleccionadas: list[str],
    ) -> dict[str, Any]:
        """Validate token, calculate aprobado, persist, audit."""
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
                details={
                    "expected": cached["dictado_id"],
                    "received": str(dictado_id),
                },
            )

        filas = cached["filas"]
        actividades_detectadas = cached["actividades"]

        actividades_filtradas = [
            a
            for a in actividades_detectadas
            if a["nombre"] in actividades_seleccionadas
        ]

        entries = []
        aprobados = 0

        for fila in filas:
            entrada_padron_id = fila.get("entrada_padron_id")
            for act in actividades_filtradas:
                act_name = act["nombre"]
                nota_num = fila.get(f"{act_name}_num")
                nota_txt = fila.get(f"{act_name}_txt")

                if nota_num is None and nota_txt is None:
                    continue

                aprobado = self._calcular_aprobado(nota_num, nota_txt)

                entries.append({
                    "entrada_padron_id": entrada_padron_id,
                    "dictado_id": dictado_id,
                    "actividad": act_name,
                    "nota_numerica": nota_num,
                    "nota_textual": nota_txt,
                    "aprobado": aprobado,
                    "origen": "Importado",
                })
                if aprobado:
                    aprobados += 1

        created = await self.calificacion_repo.bulk_create(entries)

        return {
            "total_importados": len(created),
            "aprobados": aprobados,
            "desaprobados": len(created) - aprobados,
            "mensaje": f"Importadas {len(created)} calificaciones",
        }

    def _calcular_aprobado(
        self, nota_num: float | None, nota_txt: str | None
    ) -> bool:
        """Calculate aprobado based on default threshold."""
        umbral_pct = _DEFAULT_UMBRAL_PCT
        valores_aprob = _DEFAULT_VALORES_APROBATORIOS

        if nota_num is not None and nota_txt is None:
            return float(nota_num) >= umbral_pct
        elif nota_num is None and nota_txt is not None:
            return nota_txt in valores_aprob
        elif nota_num is not None and nota_txt is not None:
            return (float(nota_num) >= umbral_pct) or (
                nota_txt in valores_aprob
            )
        return False

    async def importar_finalizacion_preview(
        self, file_content: bytes, filename: str, dictado_id: uuid.UUID
    ) -> dict[str, Any]:
        """Preview completion report. Detect TPs sin calificar."""
        parsed = parse_finalizacion_file(file_content, filename)
        entradas = await self._get_version_entradas(dictado_id)

        filas = parsed["filas"]
        for fila in filas:
            entrada_id = self._match_entrada(
                fila.get("alumno_nombre", ""),
                fila.get("alumno_apellidos", ""),
                entradas,
            )
            fila["entrada_padron_id"] = entrada_id

        actividades = parsed["actividades"]
        sin_calificar = detectar_tps_sin_calificar(filas, actividades)

        token = uuid4().hex
        self._preview_tokens[token] = {
            "dictado_id": str(dictado_id),
            "filas": filas,
            "actividades": actividades,
            "expires_at": time.time() + _TOKEN_TTL,
        }
        self._clean_expired_tokens()

        return {
            "actividades_detectadas": actividades,
            "filas": filas[:10],
            "total_filas": parsed["total_filas"],
            "tps_sin_calificar": sin_calificar,
            "preview_token": token,
        }

    async def importar_finalizacion_confirm(
        self, dictado_id: uuid.UUID, preview_token: str
    ) -> dict[str, Any]:
        """Confirm completion import. Creates calificaciones with null notas."""
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
            )

        filas = cached["filas"]
        actividades = cached["actividades"]

        entries = []
        for fila in filas:
            entrada_padron_id = fila.get("entrada_padron_id")
            for act in actividades:
                act_name = act["nombre"]
                valor = fila.get(act_name)
                entries.append({
                    "entrada_padron_id": entrada_padron_id,
                    "dictado_id": dictado_id,
                    "actividad": act_name,
                    "nota_numerica": None,
                    "nota_textual": valor,
                    "aprobado": valor == "Aprobado",
                    "origen": "Importado",
                })

        created = await self.calificacion_repo.bulk_create(entries)
        return {
            "total_importados": len(created),
            "mensaje": f"Importadas {len(created)} finalizaciones",
        }

    async def listar_calificaciones(
        self, dictado_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """List all calificaciones for a dictado.

        Includes ``actividad`` (string name) and ``actividad_id`` (UUID or None)
        so the frontend can match grades to Actividad entities by either field.
        """
        califs = await self.calificacion_repo.find_by_dictado(dictado_id)
        return [
            {
                "id": c.id,
                "entrada_padron_id": c.entrada_padron_id,
                "dictado_id": c.dictado_id,
                "actividad": c.actividad,
                "actividad_id": c.actividad_id,  # may be None for legacy/imported rows
                "nota_numerica": float(c.nota_numerica) if c.nota_numerica is not None else None,
                "nota_textual": c.nota_textual,
                "aprobado": c.aprobado,
                "origen": c.origen,
                "importado_at": c.importado_at,
            }
            for c in califs
        ]

    async def recalcular_por_cambio_umbral(
        self, dictado_id: uuid.UUID,
        umbral_pct: int | None = None,
        valores_aprobatorios: list[str] | None = None,
    ) -> int:
        """Recalculate all aprobado values when threshold changes."""
        if umbral_pct is None:
            umbral_pct = _DEFAULT_UMBRAL_PCT
        if valores_aprobatorios is None:
            valores_aprobatorios = _DEFAULT_VALORES_APROBATORIOS

        return await self.calificacion_repo.recalcular_aprobado_por_dictado(
            dictado_id, umbral_pct, valores_aprobatorios
        )
