from app.core.acciones_auditoria import AccionAuditoria
from app.core.permissions import Perm


def test_padron_importar_permission_exists():
    assert Perm.PADRON_IMPORTAR == "padron:importar"


def test_padron_vaciar_permission_exists():
    assert Perm.PADRON_VACIAR == "padron:vaciar"


def test_padron_ver_permission_exists():
    assert Perm.PADRON_VER == "padron:ver"


def test_padron_vaciar_audit_action_exists():
    assert AccionAuditoria.PADRON_VACIAR == "PADRON_VACIAR"


def test_padron_cargar_audit_action_exists():
    assert AccionAuditoria.PADRON_CARGAR == "PADRON_CARGAR"
