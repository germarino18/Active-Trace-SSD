"""Tests for perfil schemas."""
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.perfil import PerfilUpdate


class TestPerfilUpdate:
    def test_valid_update(self):
        data = PerfilUpdate(nombre="Nuevo", banco="Nación")
        assert data.nombre == "Nuevo"
        assert data.banco == "Nación"

    def test_cuil_rejected(self):
        with pytest.raises(ValidationError):
            PerfilUpdate(cuil="20-12345678-9")

    def test_empty_body_allowed(self):
        data = PerfilUpdate()
        assert data.model_dump(exclude_unset=True) == {}

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            PerfilUpdate(unknown_field="x")

    def test_facturador_optional(self):
        data = PerfilUpdate(facturador=True)
        assert data.facturador is True

        data2 = PerfilUpdate()
        assert data2.facturador is None
