"""Tests for `app/schemas/equipo.py` DTOs (C-08 task group 1).

All schemas use `model_config = ConfigDict(extra='forbid')` (regla dura #5):
unknown fields are rejected. Required fields raise `ValidationError` if
missing.
"""

import datetime
import uuid

import pytest
from pydantic import ValidationError

_HOY = datetime.date.today()


# ── 1.1 RED / 1.2 GREEN: AsignacionMasivaCreate ──────────────────────────


def test_asignacion_masiva_create_rejects_extra_fields():
    from app.schemas.equipo import AsignacionMasivaCreate

    with pytest.raises(ValidationError):
        AsignacionMasivaCreate(
            usuario_ids=[str(uuid.uuid4())],
            materia_id=str(uuid.uuid4()),
            carrera_id=str(uuid.uuid4()),
            cohorte_id=str(uuid.uuid4()),
            rol="PROFESOR",
            desde=str(_HOY),
            campo_extra="no_deberia_existir",
        )


def test_asignacion_masiva_create_requires_mandatory_fields():
    from app.schemas.equipo import AsignacionMasivaCreate

    # Missing usuario_ids, materia_id, carrera_id, cohorte_id, rol, desde.
    with pytest.raises(ValidationError):
        AsignacionMasivaCreate()


def test_asignacion_masiva_create_accepts_valid_payload():
    from app.schemas.equipo import AsignacionMasivaCreate

    usuario_id = uuid.uuid4()
    materia_id = uuid.uuid4()
    carrera_id = uuid.uuid4()
    cohorte_id = uuid.uuid4()

    dto = AsignacionMasivaCreate(
        usuario_ids=[usuario_id],
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        rol="PROFESOR",
        desde=_HOY,
    )

    assert dto.usuario_ids == [usuario_id]
    assert dto.materia_id == materia_id
    assert dto.carrera_id == carrera_id
    assert dto.cohorte_id == cohorte_id
    assert dto.rol == "PROFESOR"
    assert dto.desde == _HOY
    assert dto.hasta is None


# ── 1.3 RED+GREEN: ClonarEquipoCreate / VigenciaEquipoUpdate ─────────────


def test_clonar_equipo_create_rejects_extra_fields():
    from app.schemas.equipo import ClonarEquipoCreate

    with pytest.raises(ValidationError):
        ClonarEquipoCreate(
            materia_id=str(uuid.uuid4()),
            carrera_id=str(uuid.uuid4()),
            cohorte_origen_id=str(uuid.uuid4()),
            cohorte_destino_id=str(uuid.uuid4()),
            desde=str(_HOY),
            campo_extra="no_deberia_existir",
        )


def test_clonar_equipo_create_accepts_valid_payload():
    from app.schemas.equipo import ClonarEquipoCreate

    materia_id = uuid.uuid4()
    carrera_id = uuid.uuid4()
    cohorte_origen_id = uuid.uuid4()
    cohorte_destino_id = uuid.uuid4()

    dto = ClonarEquipoCreate(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_origen_id=cohorte_origen_id,
        cohorte_destino_id=cohorte_destino_id,
        desde=_HOY,
        hasta=_HOY + datetime.timedelta(days=180),
    )

    assert dto.materia_id == materia_id
    assert dto.carrera_id == carrera_id
    assert dto.cohorte_origen_id == cohorte_origen_id
    assert dto.cohorte_destino_id == cohorte_destino_id
    assert dto.desde == _HOY
    assert dto.hasta == _HOY + datetime.timedelta(days=180)


def test_vigencia_equipo_update_rejects_extra_fields():
    from app.schemas.equipo import VigenciaEquipoUpdate

    with pytest.raises(ValidationError):
        VigenciaEquipoUpdate(
            materia_id=str(uuid.uuid4()),
            carrera_id=str(uuid.uuid4()),
            cohorte_id=str(uuid.uuid4()),
            desde=str(_HOY),
            campo_extra="no_deberia_existir",
        )


def test_vigencia_equipo_update_accepts_optional_dates():
    from app.schemas.equipo import VigenciaEquipoUpdate

    materia_id = uuid.uuid4()
    carrera_id = uuid.uuid4()
    cohorte_id = uuid.uuid4()

    # Both desde and hasta are optional — only hasta provided.
    dto = VigenciaEquipoUpdate(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        hasta=_HOY + datetime.timedelta(days=365),
    )

    assert dto.materia_id == materia_id
    assert dto.carrera_id == carrera_id
    assert dto.cohorte_id == cohorte_id
    assert dto.desde is None
    assert dto.hasta == _HOY + datetime.timedelta(days=365)


# ── 1.4 RED+GREEN: MisEquiposFiltros / EquipoFiltros / export & resultado ─


def test_mis_equipos_filtros_all_optional_and_rejects_extra():
    from app.schemas.equipo import MisEquiposFiltros

    dto = MisEquiposFiltros()
    assert dto.estado is None
    assert dto.materia_id is None
    assert dto.rol is None
    assert dto.carrera_id is None
    assert dto.cohorte_id is None

    with pytest.raises(ValidationError):
        MisEquiposFiltros(campo_extra="x")


def test_equipo_filtros_all_optional_and_rejects_extra():
    from app.schemas.equipo import EquipoFiltros

    dto = EquipoFiltros()
    assert dto.materia_id is None
    assert dto.carrera_id is None
    assert dto.cohorte_id is None
    assert dto.usuario_id is None
    assert dto.rol is None
    assert dto.responsable_id is None

    with pytest.raises(ValidationError):
        EquipoFiltros(campo_extra="x")


def test_equipo_export_item_includes_derived_estado_vigencia():
    from app.schemas.equipo import EquipoExportItem

    usuario_id = uuid.uuid4()
    materia_id = uuid.uuid4()
    carrera_id = uuid.uuid4()
    cohorte_id = uuid.uuid4()

    item = EquipoExportItem(
        usuario_id=usuario_id,
        docente="Juan Perez",
        rol="PROFESOR",
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        desde=_HOY,
        hasta=None,
        estado_vigencia="Vigente",
    )

    assert item.docente == "Juan Perez"
    assert item.estado_vigencia == "Vigente"

    with pytest.raises(ValidationError):
        EquipoExportItem(
            usuario_id=usuario_id,
            docente="Juan Perez",
            rol="PROFESOR",
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            desde=_HOY,
            hasta=None,
            estado_vigencia="Vigente",
            campo_extra="x",
        )


def test_equipo_asignacion_response_includes_derived_estado_vigencia_and_rejects_extra():
    from app.schemas.equipo import EquipoAsignacionResponse

    asignacion_id = uuid.uuid4()
    usuario_id = uuid.uuid4()
    materia_id = uuid.uuid4()
    carrera_id = uuid.uuid4()
    cohorte_id = uuid.uuid4()

    item = EquipoAsignacionResponse(
        id=asignacion_id,
        usuario_id=usuario_id,
        rol="PROFESOR",
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        dictado_id=None,
        comisiones=["A"],
        responsable_id=None,
        desde=_HOY,
        hasta=None,
        estado_vigencia="Vigente",
    )

    assert item.id == asignacion_id
    assert item.usuario_id == usuario_id
    assert item.estado_vigencia == "Vigente"

    with pytest.raises(ValidationError):
        EquipoAsignacionResponse(
            id=asignacion_id,
            usuario_id=usuario_id,
            rol="PROFESOR",
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            dictado_id=None,
            comisiones=["A"],
            responsable_id=None,
            desde=_HOY,
            hasta=None,
            estado_vigencia="Vigente",
            campo_extra="x",
        )


def test_docente_response_rejects_extra_fields():
    from app.schemas.equipo import DocenteResponse

    usuario_id = uuid.uuid4()
    docente = DocenteResponse(usuario_id=usuario_id, nombre="Ana", apellidos="Perez")
    assert docente.usuario_id == usuario_id
    assert docente.nombre == "Ana"
    assert docente.apellidos == "Perez"

    with pytest.raises(ValidationError):
        DocenteResponse(usuario_id=usuario_id, nombre="Ana", apellidos="Perez", campo_extra="x")


def test_asignacion_masiva_resultado_tracks_creadas_y_existentes():
    from app.schemas.equipo import AsignacionMasivaResultado

    creada_id = uuid.uuid4()
    existente_id = uuid.uuid4()

    resultado = AsignacionMasivaResultado(
        creadas=[creada_id],
        ya_existentes=[existente_id],
        filas_afectadas=1,
    )

    assert resultado.creadas == [creada_id]
    assert resultado.ya_existentes == [existente_id]
    assert resultado.filas_afectadas == 1

    with pytest.raises(ValidationError):
        AsignacionMasivaResultado(
            creadas=[creada_id],
            ya_existentes=[existente_id],
            filas_afectadas=1,
            campo_extra="x",
        )
