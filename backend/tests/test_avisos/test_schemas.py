"""Tests for avisos schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.avisos import (
    AcknowledgmentRead,
    AcknowledgmentStats,
    AvisoCreate,
    AvisoListParams,
    AvisoRead,
    AvisoUpdate,
    AvisoVisibleRead,
    ConfirmResponse,
)


def test_aviso_create_minimal():
    data = {
        "alcance": "GLOBAL",
        "titulo": "Test",
        "cuerpo": "Cuerpo test",
        "inicio_en": datetime(2026, 1, 1, tzinfo=UTC),
        "fin_en": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
    }
    s = AvisoCreate(**data)
    assert s.alcance == "GLOBAL"
    assert s.severidad == "INFO"
    assert s.orden == 0
    assert s.activo is True
    assert s.requiere_ack is False


def test_aviso_create_all_fields():
    data = {
        "alcance": "POR_ROL",
        "materia_id": uuid4(),
        "cohorte_id": uuid4(),
        "rol_destino": "ALUMNO",
        "severidad": "CRITICO",
        "titulo": "Test",
        "cuerpo": "Cuerpo",
        "inicio_en": datetime(2026, 6, 1, tzinfo=UTC),
        "fin_en": datetime(2026, 6, 30, 23, 59, 59, tzinfo=UTC),
        "orden": 5,
        "activo": False,
        "requiere_ack": True,
    }
    s = AvisoCreate(**data)
    assert s.rol_destino == "ALUMNO"
    assert s.severidad == "CRITICO"
    assert s.orden == 5
    assert s.activo is False
    assert s.requiere_ack is True


def test_aviso_create_extra_forbid():
    with pytest.raises(ValidationError):
        AvisoCreate(**{
            "alcance": "GLOBAL",
            "titulo": "Test",
            "cuerpo": "Cuerpo",
            "inicio_en": datetime(2026, 1, 1, tzinfo=UTC),
            "fin_en": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
            "extra_field": "should_fail",
        })


def test_aviso_create_invalid_alcance():
    with pytest.raises(ValidationError):
        AvisoCreate(**{
            "alcance": "INVALIDO",
            "titulo": "Test",
            "cuerpo": "Cuerpo",
            "inicio_en": datetime(2026, 1, 1, tzinfo=UTC),
            "fin_en": datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        })


def test_aviso_update_partial():
    s = AvisoUpdate(titulo="Nuevo titulo")
    assert s.titulo == "Nuevo titulo"
    assert s.activo is None


def test_aviso_update_extra_forbid():
    with pytest.raises(ValidationError):
        AvisoUpdate(titulo="Test", extra="bad")


def test_aviso_read_from_attributes():
    uid = uuid4()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    s = AvisoRead.model_validate({
        "id": uid,
        "tenant_id": uid,
        "alcance": "GLOBAL",
        "materia_id": None,
        "cohorte_id": None,
        "rol_destino": None,
        "severidad": "INFO",
        "titulo": "Test",
        "cuerpo": "Body",
        "inicio_en": now,
        "fin_en": now,
        "orden": 0,
        "activo": True,
        "requiere_ack": False,
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    })
    assert s.id == uid
    assert s.alcance == "GLOBAL"


def test_aviso_visible_read():
    uid = uuid4()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    s = AvisoVisibleRead.model_validate({
        "id": uid,
        "tenant_id": uid,
        "alcance": "GLOBAL",
        "materia_id": None,
        "cohorte_id": None,
        "rol_destino": None,
        "severidad": "INFO",
        "titulo": "Test",
        "cuerpo": "Body",
        "inicio_en": now,
        "fin_en": now,
        "orden": 0,
        "activo": True,
        "requiere_ack": True,
        "acknowledged": False,
        "created_at": now,
        "updated_at": now,
    })
    assert s.acknowledged is False


def test_acknowledgment_read():
    uid = uuid4()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    s = AcknowledgmentRead.model_validate({
        "id": uid,
        "aviso_id": uuid4(),
        "usuario_id": uuid4(),
        "confirmado_at": now,
    })
    assert s.id == uid


def test_acknowledgment_stats():
    s = AcknowledgmentStats(total=10, confirmados=7, pendientes=3)
    assert s.total == 10
    assert s.confirmados == 7
    assert s.pendientes == 3


def test_confirm_response():
    s = ConfirmResponse(acknowledged=True)
    assert s.acknowledged is True


def test_aviso_list_params_defaults():
    s = AvisoListParams()
    assert s.skip == 0
    assert s.limit == 50
    assert s.activo is None
    assert s.alcance is None


def test_aviso_list_params_all():
    s = AvisoListParams(skip=10, limit=20, activo=True, alcance="GLOBAL")
    assert s.skip == 10
    assert s.limit == 20
    assert s.activo is True
    assert s.alcance == "GLOBAL"
