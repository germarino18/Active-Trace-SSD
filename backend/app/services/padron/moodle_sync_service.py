"""MoodleSyncService: integrate Moodle WS with PadronService (C-09 Task 6.2).

Converts Moodle users to CSV in-memory and passes through PadronService
flow to reuse token validation, version creation, and audit logic.
"""

import csv
import io
import uuid

from app.integrations.moodle_ws import MoodleClient
from app.services.padron.padron_service import PadronService


class MoodleSyncService:
    """Orchestrate Moodle sync, creating padron versions via PadronService."""

    def __init__(self, db_session, tenant_id: uuid.UUID, current_user_id: uuid.UUID):
        self.db_session = db_session
        self.tenant_id = tenant_id
        self.current_user_id = current_user_id

    async def sync_on_demand(self, dictado_id: uuid.UUID, moodle_config: dict) -> dict:
        """Sync users from Moodle for a dictado.

        Args:
            dictado_id: Target dictado UUID.
            moodle_config: {"base_url": ..., "token": ..., "course_id": ...}

        Returns:
            Result dict from PadronService.confirmar_importacion.
        """
        client = MoodleClient(
            base_url=moodle_config["base_url"],
            token=moodle_config["token"],
        )
        users = await client.sync_usuarios(moodle_config["course_id"])

        csv_bytes = self._users_to_csv(users)

        padron_service = PadronService(self.db_session, self.tenant_id, self.current_user_id)
        preview = await padron_service.preview_archivo(
            csv_bytes, "moodle-sync.csv", dictado_id,
        )
        result = await padron_service.confirmar_importacion(
            dictado_id, preview["preview_token"],
        )
        return result

    async def sync_nocturna(self, tenants_config: list[dict]) -> list[dict]:
        """Worker: iterate tenants with Moodle config, sync per dictado.

        Simplified version - actual worker implementation comes later.
        """
        _ = tenants_config
        return []

    @staticmethod
    def _users_to_csv(users: list[dict]) -> bytes:
        """Convert list of user dicts to CSV bytes for PadronService."""
        if not users:
            header = "nombre,apellidos,email,comision,regional\n"
            return header.encode("utf-8")

        output = io.StringIO()
        fieldnames = ["nombre", "apellidos", "email", "comision", "regional"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow({
                "nombre": user.get("nombre") or "",
                "apellidos": user.get("apellidos") or "",
                "email": user.get("email") or "",
                "comision": user.get("comision") or "",
                "regional": user.get("regional") or "",
            })
        return output.getvalue().encode("utf-8")
