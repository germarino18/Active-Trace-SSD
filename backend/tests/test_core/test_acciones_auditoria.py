from app.core.acciones_auditoria import AccionAuditoria


def test_impersonacion_action_codes_resolve_to_expected_values():
    assert AccionAuditoria.IMPERSONACION_INICIAR == "IMPERSONACION_INICIAR"
    assert AccionAuditoria.IMPERSONACION_FINALIZAR == "IMPERSONACION_FINALIZAR"


def test_forward_declared_action_codes_exist():
    assert AccionAuditoria.CALIFICACIONES_IMPORTAR == "CALIFICACIONES_IMPORTAR"
    assert AccionAuditoria.PADRON_CARGAR == "PADRON_CARGAR"
    assert AccionAuditoria.COMUNICACION_ENVIAR == "COMUNICACION_ENVIAR"
    assert AccionAuditoria.ASIGNACION_MODIFICAR == "ASIGNACION_MODIFICAR"
    assert AccionAuditoria.LIQUIDACION_CERRAR == "LIQUIDACION_CERRAR"
