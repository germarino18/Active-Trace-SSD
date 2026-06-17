"""Tests for liquidaciones and facturas schemas."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.liquidaciones import (
    ClavePlusCreate, ClavePlusRead, ClavePlusUpdate,
    LiquidacionCerrarResponse, LiquidacionHistorialParams, LiquidacionRead,
    MateriaClavePlusCreate, MateriaClavePlusRead,
    SalarioBaseCreate, SalarioBaseRead, SalarioBaseUpdate,
    SalarioPlusCreate, SalarioPlusRead, SalarioPlusUpdate,
)
from app.schemas.facturas import (
    FacturaAbonarResponse, FacturaCreate, FacturaListParams, FacturaRead, FacturaUpdate,
)

_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


# ── SalarioBase ─────────────────────────────────────────────────────

def test_salario_base_create_minimal():
    s = SalarioBaseCreate(rol="PROFESOR", monto=Decimal("150000.00"), desde=date(2026, 1, 1))
    assert s.rol == "PROFESOR"
    assert s.monto == Decimal("150000.00")
    assert s.hasta is None


def test_salario_base_create_all_fields():
    s = SalarioBaseCreate(rol="TUTOR", monto=Decimal("80000.00"), desde=date(2026, 1, 1), hasta=date(2026, 12, 31))
    assert s.hasta == date(2026, 12, 31)


def test_salario_base_create_extra_forbid():
    with pytest.raises(ValidationError):
        SalarioBaseCreate(rol="PROFESOR", monto=Decimal("1"), desde=date(2026, 1, 1), extra="bad")


def test_salario_base_update_partial():
    s = SalarioBaseUpdate(monto=Decimal("160000.00"))
    assert s.monto == Decimal("160000.00")
    assert s.rol is None


def test_salario_base_update_extra_forbid():
    with pytest.raises(ValidationError):
        SalarioBaseUpdate(rol="PROFESOR", extra="bad")


def test_salario_base_read():
    uid = uuid4()
    s = SalarioBaseRead.model_validate({
        "id": uid, "tenant_id": uid, "rol": "PROFESOR",
        "monto": Decimal("150000.00"), "desde": date(2026, 1, 1),
        "hasta": None, "created_at": _NOW, "updated_at": _NOW, "deleted_at": None,
    })
    assert s.id == uid
    assert s.rol == "PROFESOR"
    assert s.deleted_at is None


# ── SalarioPlus ─────────────────────────────────────────────────────

def test_salario_plus_create_minimal():
    s = SalarioPlusCreate(grupo="PROG", rol="PROFESOR", descripcion="Plus", monto=Decimal("25000.00"), desde=date(2026, 1, 1))
    assert s.grupo == "PROG"


def test_salario_plus_create_extra_forbid():
    with pytest.raises(ValidationError):
        SalarioPlusCreate(grupo="PROG", rol="PROFESOR", descripcion="X", monto=Decimal("1"), desde=date(2026, 1, 1), extra="bad")


def test_salario_plus_update_partial():
    s = SalarioPlusUpdate(descripcion="Updated")
    assert s.descripcion == "Updated"


def test_salario_plus_update_extra_forbid():
    with pytest.raises(ValidationError):
        SalarioPlusUpdate(descripcion="X", extra="bad")


def test_salario_plus_read():
    uid = uuid4()
    s = SalarioPlusRead.model_validate({
        "id": uid, "tenant_id": uid, "grupo": "PROG", "rol": "PROFESOR",
        "descripcion": "Plus", "monto": Decimal("25000.00"),
        "desde": date(2026, 1, 1), "hasta": None,
        "created_at": _NOW, "updated_at": _NOW, "deleted_at": None,
    })
    assert s.grupo == "PROG"


# ── ClavePlus ───────────────────────────────────────────────────────

def test_clave_plus_create_minimal():
    s = ClavePlusCreate(codigo="PROG", descripcion="Programacion", desde=date(2026, 1, 1))
    assert s.codigo == "PROG"


def test_clave_plus_create_extra_forbid():
    with pytest.raises(ValidationError):
        ClavePlusCreate(codigo="X", descripcion="X", desde=date(2026, 1, 1), extra="bad")


def test_clave_plus_update_partial():
    s = ClavePlusUpdate(descripcion="Updated")
    assert s.descripcion == "Updated"


def test_clave_plus_read():
    uid = uuid4()
    s = ClavePlusRead.model_validate({
        "id": uid, "tenant_id": uid, "codigo": "PROG", "descripcion": "Prog",
        "desde": date(2026, 1, 1), "hasta": None,
        "created_at": _NOW, "updated_at": _NOW, "deleted_at": None,
    })
    assert s.codigo == "PROG"


# ── MateriaClavePlus ────────────────────────────────────────────────

def test_materia_clave_plus_create_minimal():
    uid = uuid4()
    s = MateriaClavePlusCreate(materia_id=uid, clave_plus_id=uid, desde=date(2026, 1, 1))
    assert s.materia_id == uid


def test_materia_clave_plus_create_extra_forbid():
    with pytest.raises(ValidationError):
        MateriaClavePlusCreate(materia_id=uuid4(), clave_plus_id=uuid4(), desde=date(2026, 1, 1), extra="bad")


def test_materia_clave_plus_read():
    uid = uuid4()
    s = MateriaClavePlusRead.model_validate({
        "id": uid, "tenant_id": uid, "materia_id": uid, "clave_plus_id": uid,
        "desde": date(2026, 1, 1), "hasta": None,
        "created_at": _NOW, "updated_at": _NOW, "deleted_at": None,
    })
    assert s.materia_id == uid


def test_liquidacion_read():
    uid = uuid4()
    s = MateriaClavePlusRead.model_validate({
        "id": uid, "tenant_id": uid, "materia_id": uid, "clave_plus_id": uid,
        "desde": date(2026, 1, 1), "hasta": None,
        "created_at": _NOW, "updated_at": _NOW, "deleted_at": None,
    })
    assert s.materia_id == uid


# ── Liquidacion ──────────────────────────────────────────────────────

def test_liquidacion_read():
    uid = uuid4()
    s = LiquidacionRead.model_validate({
        "id": uid, "tenant_id": uid, "cohorte_id": uid,
        "periodo": "2026-06", "usuario_id": uid, "rol": "PROFESOR",
        "comisiones": None, "monto_base": Decimal("150000.00"),
        "monto_plus": Decimal("0"), "total": Decimal("150000.00"),
        "es_nexo": False, "excluido_por_factura": False,
        "estado": "Abierta", "created_at": _NOW, "updated_at": _NOW,
    })
    assert s.periodo == "2026-06"
    assert s.total == Decimal("150000.00")


def test_liquidacion_cerrar_response():
    uid = uuid4()
    s = LiquidacionCerrarResponse(id=uid, estado="Cerrada", mensaje="OK")
    assert s.estado == "Cerrada"


def test_liquidacion_historial_params_defaults():
    s = LiquidacionHistorialParams()
    assert s.skip == 0
    assert s.limit == 50
    assert s.cohorte_id is None


def test_liquidacion_historial_params_all():
    uid = uuid4()
    s = LiquidacionHistorialParams(cohorte_id=uid, desde="2026-01", hasta="2026-06", skip=10, limit=20)
    assert s.cohorte_id == uid
    assert s.desde == "2026-01"
    assert s.skip == 10


# ── Factura ──────────────────────────────────────────────────────────

def test_factura_create_minimal():
    uid = uuid4()
    s = FacturaCreate(usuario_id=uid, periodo="2026-06")
    assert s.periodo == "2026-06"
    assert s.detalle is None


def test_factura_create_all_fields():
    uid = uuid4()
    s = FacturaCreate(usuario_id=uid, periodo="2026-06", detalle="Test", referencia_archivo="file.pdf", tamano_kb=Decimal("100.50"))
    assert s.detalle == "Test"
    assert s.referencia_archivo == "file.pdf"
    assert s.tamano_kb == Decimal("100.50")


def test_factura_create_extra_forbid():
    with pytest.raises(ValidationError):
        FacturaCreate(usuario_id=uuid4(), periodo="2026-06", extra="bad")


def test_factura_create_invalid_periodo():
    with pytest.raises(ValidationError):
        FacturaCreate(usuario_id=uuid4(), periodo="invalid")


def test_factura_update_partial():
    s = FacturaUpdate(detalle="Updated")
    assert s.detalle == "Updated"
    assert s.referencia_archivo is None


def test_factura_update_extra_forbid():
    with pytest.raises(ValidationError):
        FacturaUpdate(detalle="X", extra="bad")


def test_factura_read():
    uid = uuid4()
    s = FacturaRead.model_validate({
        "id": uid, "tenant_id": uid, "usuario_id": uid,
        "periodo": "2026-06", "detalle": None,
        "referencia_archivo": None, "tamano_kb": None,
        "estado": "Pendiente", "cargada_at": _NOW, "abonada_at": None,
        "created_at": _NOW, "updated_at": _NOW, "deleted_at": None,
    })
    assert s.estado == "Pendiente"
    assert s.abonada_at is None


def test_factura_abonar_response():
    uid = uuid4()
    s = FacturaAbonarResponse(id=uid, estado="Abonada", abonada_at=_NOW, mensaje="Pagado")
    assert s.estado == "Abonada"


def test_factura_list_params_defaults():
    s = FacturaListParams()
    assert s.skip == 0
    assert s.limit == 50
    assert s.usuario_id is None


def test_factura_list_params_all():
    uid = uuid4()
    s = FacturaListParams(usuario_id=uid, periodo="2026-06", estado="Pendiente", skip=10, limit=20)
    assert s.usuario_id == uid
    assert s.periodo == "2026-06"
    assert s.estado == "Pendiente"
    assert s.skip == 10
