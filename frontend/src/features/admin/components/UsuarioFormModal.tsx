import { useEffect, useState, type ChangeEvent } from 'react';
import { useRoles } from '../hooks/useRoles';
import { useRolesAsignacion, useAsignarRolUsuario, useRemoverRolUsuario } from '../hooks/useRolesAsignacion';
import type { Usuario, CrearUsuarioData, EditarUsuarioData } from '../types';

type FormValues = {
  nombre: string;
  apellidos: string;
  estado: 'Activo' | 'Inactivo';
};

interface UsuarioFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CrearUsuarioData | EditarUsuarioData) => Promise<void>;
  selectedItem?: Usuario | null;
}

export function UsuarioFormModal({
  isOpen,
  onClose,
  onSave,
  selectedItem,
}: UsuarioFormModalProps) {
  const { data: rolesCatalogo, isLoading: rolesLoading } = useRoles();
  const { data: rolesAsignados, isLoading: rolesAsignadosLoading } = useRolesAsignacion(selectedItem?.id);
  const asignarRol = useAsignarRolUsuario();
  const removerRol = useRemoverRolUsuario();

  const [formValues, setFormValues] = useState<FormValues>({
    nombre: '',
    apellidos: '',
    estado: 'Activo',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nuevoRolId, setNuevoRolId] = useState('');

  useEffect(() => {
    if (selectedItem) {
      setFormValues({
        nombre: selectedItem.nombre,
        apellidos: selectedItem.apellidos,
        estado: selectedItem.estado,
      });
    } else {
      setFormValues({
        nombre: '',
        apellidos: '',
        estado: 'Activo',
      });
    }
    setError(null);
    setNuevoRolId('');
  }, [selectedItem, isOpen]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
    }
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose, isSubmitting]);

  if (!isOpen) return null;

  function buildPayload(): EditarUsuarioData {
    const payload: EditarUsuarioData = {
      nombre: formValues.nombre || undefined,
      apellidos: formValues.apellidos || undefined,
      estado: formValues.estado,
    };
    // Strip undefined values for PATCH
    return Object.fromEntries(
      Object.entries(payload).filter(([_, v]) => v !== undefined),
    ) as EditarUsuarioData;
  }

  const handleSubmit = async () => {
    if (!formValues.nombre || !formValues.apellidos) {
      setError('Completá todos los campos obligatorios');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSave(buildPayload());
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar el usuario');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAsignarRol = async () => {
    if (!selectedItem || !nuevoRolId) return;
    try {
      await asignarRol.mutateAsync({ usuarioId: selectedItem.id, rol_id: nuevoRolId });
      setNuevoRolId('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al asignar rol');
    }
  };

  const handleRemoverRol = async (rolId: string) => {
    if (!selectedItem) return;
    try {
      await removerRol.mutateAsync({ usuarioId: selectedItem.id, rolId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al remover rol');
    }
  };

  const updateField = (field: keyof FormValues, value: string) => {
    setFormValues((prev) => ({ ...prev, [field]: value }));
  };

  const rolesDisponibles = (rolesCatalogo ?? []).filter(
    (rc) => !(rolesAsignados ?? []).some((ra) => ra.rol_id === rc.id),
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8"
      onClick={isSubmitting ? undefined : onClose}
    >
      <div
        style={{
          width: 440,
          maxWidth: '100%',
          background: 'var(--surface-container)',
          border: '1px solid var(--outline-variant)',
          borderRadius: 'var(--radius-lg)',
          padding: 28,
        }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="usuario-form-title"
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
          <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
            {selectedItem ? 'Editar usuario' : 'Nuevo usuario'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--outline)', padding: 4, display: 'flex' }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 22 }}>close</span>
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--outline)' }}>
                Nombre <span style={{ color: 'var(--error)' }}>*</span>
              </label>
              <input
                type="text"
                value={formValues.nombre}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  updateField('nombre', e.target.value)
                }
                placeholder="Nombre"
                style={{
                  width: '100%', height: 40, padding: '0 12px', boxSizing: 'border-box',
                  borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)',
                  background: 'var(--surface-container-lowest)', color: 'var(--on-surface)',
                  fontSize: 14, outline: 'none',
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--outline-variant)'}
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--outline)' }}>
                Apellidos <span style={{ color: 'var(--error)' }}>*</span>
              </label>
              <input
                type="text"
                value={formValues.apellidos}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  updateField('apellidos', e.target.value)
                }
                placeholder="Apellidos"
                style={{
                  width: '100%', height: 40, padding: '0 12px', boxSizing: 'border-box',
                  borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)',
                  background: 'var(--surface-container-lowest)', color: 'var(--on-surface)',
                  fontSize: 14, outline: 'none',
                }}
                onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                onBlur={(e) => e.target.style.borderColor = 'var(--outline-variant)'}
              />
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--outline)' }}>
              Estado
            </label>
            <select
              value={formValues.estado}
              onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                updateField('estado', e.target.value)
              }
              style={{
                width: '100%', height: 40, padding: '0 12px', boxSizing: 'border-box',
                borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)',
                background: 'var(--surface-container-lowest)', color: 'var(--on-surface)',
                fontSize: 14, outline: 'none', cursor: 'pointer',
              }}
              onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
              onBlur={(e) => e.target.style.borderColor = 'var(--outline-variant)'}
            >
              <option value="Activo">Activo</option>
              <option value="Inactivo">Inactivo</option>
            </select>
          </div>

          {selectedItem && (
            <div style={{
              display: 'flex', flexDirection: 'column', gap: 12,
              padding: 16, borderRadius: 'var(--radius-md)',
              border: '1px solid var(--outline-variant)',
              background: 'var(--surface-container-lowest)',
            }}>
              <h4 style={{ margin: 0, fontSize: 11, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>
                Roles asignados
              </h4>

              {rolesAsignadosLoading ? (
                <p style={{ margin: 0, fontSize: 13, color: 'var(--outline)' }}>Cargando roles...</p>
              ) : rolesAsignados && rolesAsignados.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {rolesAsignados.map((ra) => (
                    <div key={ra.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)', background: 'var(--surface-container)' }}>
                      <div>
                        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface)' }}>{ra.rol_nombre}</span>
                        {ra.vigencia_desde && (
                          <span style={{ fontSize: 12, color: 'var(--outline)', marginLeft: 8 }}>
                            desde {new Date(ra.vigencia_desde).toLocaleDateString('es-AR')}
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoverRol(ra.id)}
                        disabled={removerRol.isPending}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--outline)', padding: 4, display: 'flex' }}
                        title="Remover rol"
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>remove_circle</span>
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ margin: 0, fontSize: 13, color: 'var(--outline)' }}>Sin roles asignados</p>
              )}

              {rolesDisponibles.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <select
                      value={nuevoRolId}
                      onChange={(e: ChangeEvent<HTMLSelectElement>) => setNuevoRolId(e.target.value)}
                      style={{
                        width: '100%', height: 36, padding: '0 12px', boxSizing: 'border-box',
                        borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)',
                        background: 'var(--surface-container-lowest)', color: 'var(--on-surface)',
                        fontSize: 13, outline: 'none', cursor: 'pointer',
                      }}
                    >
                      <option value="">Agregar rol...</option>
                      {rolesDisponibles.map((r) => (
                        <option key={r.id} value={r.id}>{r.nombre}</option>
                      ))}
                    </select>
                  </div>
                  <button
                    type="button"
                    onClick={handleAsignarRol}
                    disabled={asignarRol.isPending || !nuevoRolId}
                    style={{
                      height: 36, padding: '0 12px', display: 'flex', alignItems: 'center', gap: 4,
                      borderRadius: 'var(--radius-md)', border: 'none', cursor: 'pointer',
                      background: 'var(--primary)', color: 'var(--on-primary)',
                      fontSize: 13, fontWeight: 600, opacity: asignarRol.isPending || !nuevoRolId ? 0.5 : 1,
                    }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 16 }}>add</span>
                    Asignar
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div style={{
              background: 'var(--error-container)', border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)',
              borderRadius: 'var(--radius-md)', padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 6,
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--on-error-container)' }}>error</span>
              <span style={{ fontSize: 13, color: 'var(--on-error-container)' }}>{error}</span>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            style={{
              height: 36, padding: '0 16px', borderRadius: 'var(--radius-md)',
              border: '1px solid var(--outline-variant)', background: 'transparent',
              color: 'var(--on-surface)', fontSize: 13, fontWeight: 600, cursor: 'pointer',
            }}
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting}
            style={{
              height: 36, padding: '0 16px', borderRadius: 'var(--radius-md)',
              border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
              background: 'var(--primary)', color: 'var(--on-primary)',
              fontSize: 13, fontWeight: 600, opacity: isSubmitting ? 0.7 : 1,
            }}
          >
            {isSubmitting ? 'Guardando...' : selectedItem ? 'Guardar cambios' : 'Crear'}
          </button>
        </div>
      </div>
    </div>
  );
}
