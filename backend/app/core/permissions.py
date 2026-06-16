"""Permission constants — type-safe string constants for require_permission()."""


class Perm:
    ESTADO_ACADEMICO_VER = "estado-academico:ver"
    EVALUACION_RESERVAR = "evaluacion:reservar"
    AVISOS_CONFIRMAR = "avisos:confirmar"
    CALIFICACIONES_IMPORTAR = "calificaciones:importar"
    ATRASADOS_VER = "atrasados:ver"
    ENTREGAS_SIN_CORREGIR = "entregas:sin-corregir"
    COMUNICACION_ENVIAR = "comunicacion:enviar"
    COMUNICACION_APROBAR = "comunicacion:aprobar"
    ENCUENTROS_GESTIONAR = "encuentros:gestionar"
    GUARDIAS_REGISTRAR = "guardias:registrar"
    TAREAS_GESTIONAR = "tareas:gestionar"
    AVISOS_PUBLICAR = "avisos:publicar"
    EQUIPOS_GESTIONAR = "equipos:gestionar"
    EQUIPOS_ASIGNAR = "equipos:asignar"
    ESTRUCTURA_GESTIONAR = "estructura:gestionar"
    USUARIOS_GESTIONAR = "usuarios:gestionar"
    AUDITORIA_VER = "auditoria:ver"
    GRILLA_OPERAR = "grilla:operar"
    LIQUIDACIONES_CERRAR = "liquidaciones:cerrar"
    FACTURAS_GESTIONAR = "facturas:gestionar"
    CONFIGURAR_TENANT = "configurar:tenant"
    IMPERSONACION_USAR = "impersonacion:usar"

    # C-14 evaluaciones y coloquios
    COLOQUIOS_GESTIONAR = "coloquios:gestionar"
    COLOQUIOS_RESERVAR = "coloquios:reservar"
    COLOQUIOS_VER = "coloquios:ver"

    # C-09 padron ingesta
    PADRON_IMPORTAR = "padron:importar"
    PADRON_VACIAR = "padron:vaciar"
    PADRON_VER = "padron:ver"
