"""Tests for Pydantic schemas in app/schemas/padron.py (TASK GROUP 4).

All schemas MUST enforce extra='forbid' (regla dura #5).
"""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.padron import (
    EntradaPadronResponse,
    PadronImportConfirm,
    PadronImportResponse,
    PadronPreviewRequest,
    PadronPreviewResponse,
    PadronVaciarResponse,
    VersionPadronHistoryResponse,
    VersionPadronResponse,
)


class TestVersionPadronResponse:
    def test_accepts_valid_data(self):
        id_ = uuid.uuid4()
        dictado_id = uuid.uuid4()
        cargado_por = uuid.uuid4()
        now = datetime.now(timezone.utc)
        obj = VersionPadronResponse(
            id=id_,
            dictado_id=dictado_id,
            cargado_por=cargado_por,
            cargado_at=now,
            activa=True,
        )
        assert obj.id == id_
        assert obj.dictado_id == dictado_id
        assert obj.cargado_por == cargado_por
        assert obj.cargado_at == now
        assert obj.activa is True

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            VersionPadronResponse(
                id=uuid.uuid4(),
                dictado_id=uuid.uuid4(),
                cargado_por=uuid.uuid4(),
                cargado_at=datetime.now(timezone.utc),
                activa=True,
                extra_field="should_fail",
            )

    def test_requires_all_fields(self):
        with pytest.raises(ValidationError):
            VersionPadronResponse(id=uuid.uuid4(), dictado_id=uuid.uuid4())


class TestEntradaPadronResponse:
    def test_accepts_valid_data_minimal(self):
        id_ = uuid.uuid4()
        version_id = uuid.uuid4()
        obj = EntradaPadronResponse(
            id=id_,
            version_id=version_id,
            usuario_id=None,
            nombre="Juan",
            apellidos="Pérez",
            email=None,
            comision=None,
            regional=None,
        )
        assert obj.id == id_
        assert obj.nombre == "Juan"
        assert obj.apellidos == "Pérez"
        assert obj.usuario_id is None
        assert obj.email is None

    def test_accepts_valid_data_all_fields(self):
        uid = uuid.uuid4()
        obj = EntradaPadronResponse(
            id=uuid.uuid4(),
            version_id=uuid.uuid4(),
            usuario_id=uid,
            nombre="María",
            apellidos="García",
            email="maria@test.com",
            comision="A",
            regional="CABA",
        )
        assert obj.usuario_id == uid
        assert obj.email == "maria@test.com"
        assert obj.comision == "A"
        assert obj.regional == "CABA"

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            EntradaPadronResponse(
                id=uuid.uuid4(),
                version_id=uuid.uuid4(),
                nombre="X",
                apellidos="Y",
                extra="boom",
            )


class TestPadronPreviewRequest:
    def test_accepts_valid_data(self):
        dictado_id = uuid.uuid4()
        obj = PadronPreviewRequest(dictado_id=dictado_id)
        assert obj.dictado_id == dictado_id

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PadronPreviewRequest(dictado_id=uuid.uuid4(), extra="nope")

    def test_requires_dictado_id(self):
        with pytest.raises(ValidationError):
            PadronPreviewRequest()


class TestPadronPreviewResponse:
    def test_accepts_valid_data(self):
        obj = PadronPreviewResponse(
            columnas_encontradas=["nombre", "apellidos"],
            filas=[{"nombre": "Juan", "apellidos": "Pérez"}],
            total_filas=1,
            preview_token="tok-123",
        )
        assert obj.total_filas == 1
        assert obj.preview_token == "tok-123"

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PadronPreviewResponse(
                columnas_encontradas=[],
                filas=[],
                total_filas=0,
                preview_token="x",
                extra="nope",
            )


class TestPadronImportConfirm:
    def test_accepts_valid_data(self):
        obj = PadronImportConfirm(dictado_id=uuid.uuid4(), preview_token="tok-abc")
        assert obj.preview_token == "tok-abc"

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PadronImportConfirm(dictado_id=uuid.uuid4(), preview_token="x", extra="fail")

    def test_requires_both_fields(self):
        with pytest.raises(ValidationError):
            PadronImportConfirm(dictado_id=uuid.uuid4())


class TestPadronImportResponse:
    def test_accepts_valid_data(self):
        version_id = uuid.uuid4()
        obj = PadronImportResponse(
            version_id=version_id, total_importados=42, mensaje="ok"
        )
        assert obj.version_id == version_id
        assert obj.total_importados == 42

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PadronImportResponse(
                version_id=uuid.uuid4(), total_importados=0, mensaje="", extra="nope"
            )


class TestPadronVaciarResponse:
    def test_accepts_valid_data(self):
        obj = PadronVaciarResponse(
            dictado_id=uuid.uuid4(), entradas_eliminadas=10, mensaje="ok"
        )
        assert obj.entradas_eliminadas == 10

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            PadronVaciarResponse(
                dictado_id=uuid.uuid4(), entradas_eliminadas=0, mensaje="", extra="nope"
            )


class TestVersionPadronHistoryResponse:
    def test_accepts_valid_data(self):
        version = VersionPadronResponse(
            id=uuid.uuid4(),
            dictado_id=uuid.uuid4(),
            cargado_por=uuid.uuid4(),
            cargado_at=datetime.now(timezone.utc),
            activa=True,
        )
        obj = VersionPadronHistoryResponse(versiones=[version])
        assert len(obj.versiones) == 1
        assert obj.versiones[0].activa is True

    def test_accepts_empty_list(self):
        obj = VersionPadronHistoryResponse(versiones=[])
        assert obj.versiones == []

    def test_rejects_extra_fields(self):
        with pytest.raises(ValidationError):
            VersionPadronHistoryResponse(versiones=[], extra="nope")
