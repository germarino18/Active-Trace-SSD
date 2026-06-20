-- Insertar nuevos permisos
INSERT INTO permiso (id, tenant_id, codigo, nombre, descripcion, modulo, created_at, updated_at)
SELECT gen_random_uuid(), 'e193e975-b2c4-495c-8566-45d045866ae8', cod, nom, nom, mod, NOW(), NOW()
FROM (VALUES
    ('equipos:asignar'::varchar, 'Asignar roles y contexto a usuarios'::varchar, 'equipos'::varchar),
    ('liquidaciones:ver', 'Ver liquidaciones del per\u00edodo', 'liquidaciones'),
    ('liquidaciones:calcular', 'Calcular liquidaciones del per\u00edodo', 'liquidaciones'),
    ('liquidaciones:configurar-salarios', 'Configurar grilla salarial', 'liquidaciones'),
    ('padron:importar', 'Importar padr\u00f3n de alumnos', 'padron'),
    ('padron:vaciar', 'Vaciar datos de dictado', 'padron'),
    ('padron:ver', 'Ver padr\u00f3n de alumnos', 'padron'),
    ('coloquios:gestionar', 'Gestionar convocatorias de coloquio', 'coloquios'),
    ('coloquios:reservar', 'Reservar turno de coloquio', 'coloquios'),
    ('coloquios:ver', 'Ver coloquios y resultados', 'coloquios'),
    ('inbox:acceder', 'Acceder a la bandeja de mensajes interna', 'inbox')
) AS p(cod, nom, mod)
WHERE NOT EXISTS (
    SELECT 1 FROM permiso WHERE tenant_id = 'e193e975-b2c4-495c-8566-45d045866ae8' AND codigo = p.cod AND deleted_at IS NULL
);

-- Insertar rol_permiso entries (solo los que faltan)
INSERT INTO rol_permiso (id, tenant_id, rol_id, permiso_id, es_propio, created_at, updated_at)
SELECT gen_random_uuid(), t.tid, r.id, p.id, ep, NOW(), NOW()
FROM (SELECT 'e193e975-b2c4-495c-8566-45d045866ae8'::uuid AS tid) t
CROSS JOIN (VALUES
    ('ALUMNO', 'inbox:acceder', false),
    ('ALUMNO', 'coloquios:reservar', false),
    ('TUTOR', 'inbox:acceder', false),
    ('PROFESOR', 'inbox:acceder', false),
    ('PROFESOR', 'coloquios:ver', true),
    ('COORDINADOR', 'equipos:asignar', false),
    ('COORDINADOR', 'inbox:acceder', false),
    ('COORDINADOR', 'coloquios:gestionar', false),
    ('COORDINADOR', 'coloquios:ver', false),
    ('NEXO', 'inbox:acceder', false),
    ('ADMIN', 'equipos:asignar', false),
    ('ADMIN', 'padron:importar', false),
    ('ADMIN', 'padron:vaciar', false),
    ('ADMIN', 'padron:ver', false),
    ('ADMIN', 'inbox:acceder', false),
    ('ADMIN', 'coloquios:gestionar', false),
    ('ADMIN', 'coloquios:ver', false),
    ('FINANZAS', 'liquidaciones:ver', false),
    ('FINANZAS', 'liquidaciones:calcular', false),
    ('FINANZAS', 'liquidaciones:configurar-salarios', false),
    ('FINANZAS', 'inbox:acceder', false)
) AS m(rc, pc, ep)
JOIN rol r ON r.tenant_id = t.tid AND r.codigo = m.rc AND r.deleted_at IS NULL
JOIN permiso p ON p.tenant_id = t.tid AND p.codigo = m.pc AND p.deleted_at IS NULL
WHERE NOT EXISTS (
    SELECT 1 FROM rol_permiso rp
    WHERE rp.tenant_id = t.tid AND rp.rol_id = r.id AND rp.permiso_id = p.id
    AND rp.deleted_at IS NULL
);
