"""Add Comunicacion and hilo seed data for alumno.
Run inside the API container where the app packages are available."""
import asyncio
import hashlib
import os
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.security import encrypt_value, get_encryption_key


async def main() -> None:
    db_url = os.environ["DATABASE_URL"]
    tid = uuid.UUID("e193e975-b2c4-495c-8566-45d045866ae8")
    alumno_uid = uuid.UUID("99d13578-1482-445a-9755-36d0764604fc")
    coordinador_uid = uuid.UUID("1b0d02ae-97db-4b05-92fd-af78ec890e1d")
    tutor_uid = uuid.UUID("765f4574-4d8f-49b7-859c-7c07fa666f84")
    materia1_id = uuid.UUID("c122b4ab-71c8-4149-bccf-5ceab887ecb6")

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # ── Comunicaciones ──────────────────────────────────────────────────
        encryption_key = get_encryption_key()
        alumno_email_enc = encrypt_value("alumno@demo.com", encryption_key)
        alumno_hash = hashlib.sha256(b"alumno@demo.com").hexdigest()

        lote_id = uuid.uuid4()
        for com_asunto, com_cuerpo in [
            (
                "Bienvenida al cuatrimestre 2026 — Primer cuatrimestre",
                "Te damos la bienvenida al primer cuatrimestre de 2026. "
                "Record\u00e1 revisar el calendario acad\u00e9mico y las fechas de parciales en tu dashboard."
            ),
            (
                "Recordatorio: Inscripci\u00f3n a coloquios",
                "Las inscripciones para los coloquios de Programaci\u00f3n I y Bases de Datos "
                "cierran el 30 de junio. Si est\u00e1s en condiciones, no olvides reservar tu turno "
                "desde la secci\u00f3n de Coloquios."
            ),
        ]:
            await session.execute(
                text(
                    "INSERT INTO comunicacion (id, tenant_id, enviado_por, materia_id, asunto, cuerpo, "
                    "destinatario_hash, destinatario, lote_id, estado, created_at, updated_at) "
                    "VALUES (:id, :tid, :eid, :mid, :asunto, :cuerpo, :dhash, :denc, :lid, 'Enviado', NOW(), NOW())"
                ),
                {
                    "id": uuid.uuid4(), "tid": tid,
                    "eid": coordinador_uid,
                    "mid": materia1_id,
                    "asunto": com_asunto,
                    "cuerpo": com_cuerpo,
                    "dhash": alumno_hash,
                    "denc": alumno_email_enc,
                    "lid": lote_id,
                },
            )
            print(f"  + Comunicacion: {com_asunto}")

        # ── Hilo para alumno ─────────────────────────────────────────────────
        hilo_id = uuid.uuid4()
        await session.execute(
            text("INSERT INTO hilo_conversacion (id, tenant_id, asunto, created_at, updated_at) VALUES (:id, :tid, :asunto, NOW(), NOW())"),
            {"id": hilo_id, "tid": tid, "asunto": "Consulta sobre correlativas \u2014 Programaci\u00f3n I"},
        )
        for uid in [coordinador_uid, tutor_uid, alumno_uid]:
            await session.execute(
                text("INSERT INTO hilo_participante (hilo_id, usuario_id) VALUES (:hid, :uid)"),
                {"hid": hilo_id, "uid": uid},
            )
        for remitente_id, contenido in [
            (alumno_uid,
             "Buenos d\u00edas, quer\u00eda saber si con la regularidad de Programaci\u00f3n I "
             "puedo cursar Bases de Datos este cuatrimestre o necesito tenerla aprobada."),
            (tutor_uid,
             "Hola Mar\u00eda, con la regularidad es suficiente. "
             "La correlativa pide 'regularizada' para cursar, no aprobada."),
            (alumno_uid,
             "Perfecto, \u00a1muchas gracias!"),
        ]:
            await session.execute(
                text("INSERT INTO mensaje (id, tenant_id, hilo_id, remitente_id, contenido, created_at, updated_at) VALUES (:id, :tid, :hid, :rem, :cont, NOW(), NOW())"),
                {"id": uuid.uuid4(), "tid": tid, "hid": hilo_id, "rem": remitente_id, "cont": contenido},
            )
        print(f"  + Hilo: Consulta sobre correlativas (3 mensajes)")

        await session.commit()
        print("\nSeed complementario completado!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
