import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import FileResponse
from starlette.requests import Request

from app.core.acciones_auditoria import AccionAuditoria
from app.core.exceptions import NotFoundException, ValidationException
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.programas import ProgramaMateriaCreate, ProgramaMateriaRead, ProgramaMateriaUpdate
from app.services.audit.audit_logger import AuditLogger

_DEFAULT_UPLOAD_DIR = os.path.join("uploads", "programas")


class ProgramasService:
    def __init__(
        self,
        repo: ProgramaMateriaRepository,
        audit_repo: AuditLogRepository,
        upload_dir: str = _DEFAULT_UPLOAD_DIR,
    ):
        self._repo = repo
        self._audit = AuditLogger(repository=audit_repo)
        self._upload_dir = upload_dir

    @classmethod
    def create(cls, db, tenant_id: uuid.UUID, upload_dir: str | None = None) -> "ProgramasService":
        return cls(
            repo=ProgramaMateriaRepository(session=db, tenant_id=tenant_id),
            audit_repo=AuditLogRepository(session=db, tenant_id=tenant_id),
            upload_dir=upload_dir or _DEFAULT_UPLOAD_DIR,
        )

    async def upload_programa(
        self,
        dictado_id: uuid.UUID,
        titulo: str,
        archivo: UploadFile,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> ProgramaMateriaRead:
        if await self._repo.exists_by_dictado(dictado_id):
            raise ValidationException(
                message="Ya existe un programa para este dictado",
                details={"dictado_id": str(dictado_id)},
            )

        relative_path = await self._save_file(dictado_id, archivo)
        programa = await self._repo.create(
            ProgramaMateriaCreate(dictado_id=dictado_id, titulo=titulo).model_dump()
            | {"referencia_archivo": relative_path}
        )

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.PROGRAMA_CARGAR,
            detalle={
                "id": str(programa.id),
                "dictado_id": str(dictado_id),
                "titulo": titulo,
                "referencia_archivo": relative_path,
            },
            filas_afectadas=1,
            request=request,
        )
        return ProgramaMateriaRead(
            id=programa.id,
            dictado_id=programa.dictado_id,
            titulo=programa.titulo,
            referencia_archivo=programa.referencia_archivo,
            cargado_at=programa.cargado_at,
            created_at=programa.created_at,
            updated_at=programa.updated_at,
        )

    async def update_programa(
        self,
        id: uuid.UUID,
        data: ProgramaMateriaUpdate,
        archivo_opcional: UploadFile | None,
        *,
        current_user: CurrentUser,
        request: Request,
    ) -> ProgramaMateriaRead:
        programa = await self._repo.find_by_id(id)
        if programa is None:
            raise NotFoundException(resource="ProgramaMateria", id=id)

        update_data = {}
        if data.titulo is not None:
            update_data["titulo"] = data.titulo
        if archivo_opcional is not None:
            update_data["referencia_archivo"] = await self._save_file(programa.dictado_id, archivo_opcional)

        if update_data:
            programa = await self._repo.update(id, update_data)

        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.PROGRAMA_ACTUALIZAR,
            detalle={"id": str(id), "cambios": update_data},
            filas_afectadas=1,
            request=request,
        )
        return ProgramaMateriaRead(
            id=programa.id,
            dictado_id=programa.dictado_id,
            titulo=programa.titulo,
            referencia_archivo=programa.referencia_archivo,
            cargado_at=programa.cargado_at,
            created_at=programa.created_at,
            updated_at=programa.updated_at,
        )

    async def get_programa(self, id: uuid.UUID, current_user: CurrentUser) -> ProgramaMateriaRead:
        programa = await self._repo.find_by_id(id)
        if programa is None:
            raise NotFoundException(resource="ProgramaMateria", id=id)
        return ProgramaMateriaRead(
            id=programa.id,
            dictado_id=programa.dictado_id,
            titulo=programa.titulo,
            referencia_archivo=programa.referencia_archivo,
            cargado_at=programa.cargado_at,
            created_at=programa.created_at,
            updated_at=programa.updated_at,
        )

    async def get_by_dictado(self, dictado_id: uuid.UUID, current_user: CurrentUser) -> ProgramaMateriaRead:
        programa = await self._repo.find_by_dictado(dictado_id)
        if programa is None:
            raise NotFoundException(resource="ProgramaMateria", id=dictado_id)
        return ProgramaMateriaRead(
            id=programa.id,
            dictado_id=programa.dictado_id,
            titulo=programa.titulo,
            referencia_archivo=programa.referencia_archivo,
            cargado_at=programa.cargado_at,
            created_at=programa.created_at,
            updated_at=programa.updated_at,
        )

    async def delete_programa(
        self,
        id: uuid.UUID,
        *,
        current_user: CurrentUser,
        request: Request,
    ):
        programa = await self._repo.find_by_id(id)
        if programa is None:
            raise NotFoundException(resource="ProgramaMateria", id=id)

        await self._repo.soft_delete(id)
        await self._audit.log(
            current_user=current_user,
            accion=AccionAuditoria.PROGRAMA_ELIMINAR,
            detalle={"id": str(id)},
            filas_afectadas=1,
            request=request,
        )

    async def download_programa(self, id: uuid.UUID, current_user: CurrentUser) -> FileResponse:
        programa = await self._repo.find_by_id(id)
        if programa is None:
            raise NotFoundException(resource="ProgramaMateria", id=id)

        file_path = programa.referencia_archivo
        if not os.path.exists(file_path):
            raise NotFoundException(
                resource="Archivo",
                id=id,
                message="El archivo del programa no se encuentra en el servidor",
            )

        filename = Path(file_path).name
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=filename,
        )

    async def _save_file(self, dictado_id: uuid.UUID, archivo: UploadFile) -> str:
        upload_path = Path(self._upload_dir) / str(dictado_id)
        os.makedirs(upload_path, exist_ok=True)

        filename = archivo.filename or f"{uuid.uuid4().hex}"
        file_path = str(upload_path / filename)

        content = await archivo.read()
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path
