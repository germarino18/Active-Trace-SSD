"""Tests for the TemplateEngine."""

import pytest

from app.core.template_engine import TemplateEngine, TemplateVariableError


@pytest.fixture
def engine() -> TemplateEngine:
    return TemplateEngine(
        allowed_variables={
            "alumno_nombre",
            "alumno_apellido",
            "materia",
            "docente_nombre",
        }
    )


@pytest.mark.asyncio
async def test_render_all_variables(engine: TemplateEngine):
    result = engine.render(
        template="Hola $alumno_nombre $alumno_apellido, su materia $materia con $docente_nombre",
        values={
            "alumno_nombre": "Juan",
            "alumno_apellido": "Pérez",
            "materia": "Matemática",
            "docente_nombre": "Prof. García",
        },
    )
    assert result == "Hola Juan Pérez, su materia Matemática con Prof. García"


@pytest.mark.asyncio
async def test_render_some_variables(engine: TemplateEngine):
    result = engine.render(
        template="Hola $alumno_nombre, tiene actividades pendientes",
        values={"alumno_nombre": "María"},
    )
    assert result == "Hola María, tiene actividades pendientes"


@pytest.mark.asyncio
async def test_render_no_variables(engine: TemplateEngine):
    result = engine.render(
        template="Mensaje sin variables",
        values={"alumno_nombre": "Juan"},
    )
    assert result == "Mensaje sin variables"


@pytest.mark.asyncio
async def test_unknown_variable_raises_error(engine: TemplateEngine):
    with pytest.raises(TemplateVariableError, match="Variable '\\$inexistente' is not allowed"):
        engine.render(
            template="Hola $inexistente",
            values={"alumno_nombre": "Juan"},
        )


@pytest.mark.asyncio
async def test_template_with_dollar_sign_no_variable(engine: TemplateEngine):
    """Literal $ sign (escaped as $$) should render as $."""
    result = engine.render(
        template="Costo total: $100",
        values={},
    )
    assert result == "Costo total: $100"
