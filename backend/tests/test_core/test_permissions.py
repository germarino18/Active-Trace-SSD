from app.core.permissions import Perm


def test_impersonacion_usar_permission_constant():
    assert Perm.IMPERSONACION_USAR == "impersonacion:usar"


def test_existing_permission_constant_unchanged():
    assert Perm.AUDITORIA_VER == "auditoria:ver"
