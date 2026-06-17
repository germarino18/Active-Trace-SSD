"""Tests for mensajeria schemas."""
import pytest
from pydantic import ValidationError

from app.schemas.mensajeria import ResponderRequest


class TestResponderRequest:
    def test_valid(self):
        data = ResponderRequest(contenido="Gracias por la info")
        assert data.contenido == "Gracias por la info"

    def test_empty_rejected(self):
        with pytest.raises(ValidationError):
            ResponderRequest(contenido="")

    def test_too_long_rejected(self):
        with pytest.raises(ValidationError):
            ResponderRequest(contenido="x" * 2001)

    def test_max_length_accepted(self):
        data = ResponderRequest(contenido="x" * 2000)
        assert len(data.contenido) == 2000

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            ResponderRequest(contenido="hola", extra="nope")
