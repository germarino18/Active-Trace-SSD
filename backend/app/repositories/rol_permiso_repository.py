import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.repositories.base import BaseRepository


class RolPermisoRepository(BaseRepository[RolPermiso]):
    def __init__(self, session, tenant_id: uuid.UUID | None = None):
        super().__init__(model=RolPermiso, session=session, tenant_id=tenant_id)

    async def find_permisos_for_roles(
        self, tenant_id: uuid.UUID, role_codes: list[str]
    ) -> list[tuple[str, bool]]:
        query = (
            select(RolPermiso.es_propio, Permiso.codigo)
            .join(Rol, Rol.id == RolPermiso.rol_id)
            .join(Permiso, Permiso.id == RolPermiso.permiso_id)
            .where(
                RolPermiso.tenant_id == tenant_id,
                Rol.codigo.in_(role_codes),
                Rol.deleted_at.is_(None),
                Permiso.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return [(row.codigo, row.es_propio) for row in result]
