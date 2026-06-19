import { useEffect, useState, type ChangeEvent } from 'react';
import { useRoles } from '../hooks/useRoles';
import { useRolesAsignacion, useAsignarRolUsuario, useRemoverRolUsuario } from '../hooks/useRolesAsignacion';
import type { Usuario, CrearUsuarioData, EditarUsuarioData } from '../types';

type FormValues = CrearUsuarioData;

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
    apellido: '',
    email: '',
    rol: '',
    activo: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nuevoRolId, setNuevoRolId] = useState('');

  useEffect(() => {
    if (selectedItem) {
      setFormValues({
        nombre: selectedItem.nombre,
        apellido: selectedItem.apellido,
        email: selectedItem.email,
        rol: selectedItem.rol,
        activo: selectedItem.activo,
      });
    } else {
      setFormValues({
        nombre: '',
        apellido: '',
        email: '',
        rol: rolesCatalogo?.[0]?.nombre ?? '',
        activo: true,
      });
    }
    setError(null);
    setNuevoRolId('');
  }, [selectedItem, isOpen, rolesCatalogo]);

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

  const handleSubmit = async () => {
    if (!formValues.nombre || !formValues.apellido || !formValues.email || !formValues.rol) {
      setError('Completá todos los campos obligatorios');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onSave(formValues);
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

  const updateField = (field: keyof FormValues, value: string | boolean) => {
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
        className="mx-4 w-full max-w-lg rounded-xl border border-outline-variant bg-surface p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="usuario-form-title"
      >
        <div className="mb-4 flex items-center justify-between">
          <h3
            id="usuario-form-title"
            className="font-headline-lg text-headline-lg text-on-surface"
          >
            {selectedItem ? 'Editar usuario' : 'Nuevo usuario'}
          </h3>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="text-outline hover:text-on-surface"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                Nombre <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={formValues.nombre}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  updateField('nombre', e.target.value)
                }
                placeholder="Nombre"
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="space-y-1">
              <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                Apellido <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={formValues.apellido}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  updateField('apellido', e.target.value)
                }
                placeholder="Apellido"
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Email <span className="text-error">*</span>
            </label>
            <input
              type="email"
              value={formValues.email}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                updateField('email', e.target.value)
              }
              placeholder="usuario@ejemplo.com"
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Rol <span className="text-error">*</span>
            </label>
            <select
              value={formValues.rol}
              onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                updateField('rol', e.target.value)
              }
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={rolesLoading}
            >
              {rolesLoading ? (
                <option value="">Cargando roles...</option>
              ) : (
                <>
                  <option value="">Seleccionar rol</option>
                  {(rolesCatalogo ?? []).map((r) => (
                    <option key={r.id} value={r.nombre}>
                      {r.nombre}
                    </option>
                  ))}
                </>
              )}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Estado
            </label>
            <div className="flex items-center gap-3">
              <label className="flex cursor-pointer items-center gap-2 text-label-md text-on-surface">
                <input
                  type="checkbox"
                  checked={formValues.activo ?? true}
                  onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    updateField('activo', e.target.checked)
                  }
                  className="h-4 w-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary"
                />
                Activo
              </label>
            </div>
          </div>

          {selectedItem && (
            <div className="space-y-3 rounded-lg border border-outline-variant bg-surface-container-lowest p-4">
              <h4 className="text-label-sm font-medium text-on-surface uppercase tracking-wider">
                Roles asignados
              </h4>

              {rolesAsignadosLoading ? (
                <p className="text-label-sm text-outline">Cargando roles...</p>
              ) : rolesAsignados && rolesAsignados.length > 0 ? (
                <div className="space-y-2">
                  {rolesAsignados.map((ra) => (
                    <div key={ra.id} className="flex items-center justify-between rounded-lg border border-outline-variant bg-surface px-3 py-2">
                      <div>
                        <span className="text-label-sm text-on-surface font-medium">{ra.rol_nombre}</span>
                        {ra.vigencia_desde && (
                          <span className="text-label-xs text-outline ml-2">
                            desde {new Date(ra.vigencia_desde).toLocaleDateString('es-AR')}
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoverRol(ra.id)}
                        disabled={removerRol.isPending}
                        className="rounded-lg p-1 text-outline hover:text-error transition-colors"
                        title="Remover rol"
                      >
                        <span className="material-symbols-outlined text-[16px]">remove_circle</span>
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-label-sm text-outline">Sin roles asignados</p>
              )}

              {rolesDisponibles.length > 0 && (
                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <select
                      value={nuevoRolId}
                      onChange={(e: ChangeEvent<HTMLSelectElement>) => setNuevoRolId(e.target.value)}
                      className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
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
                    className="flex items-center gap-1 rounded-lg bg-primary px-3 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-[16px]">add</span>
                    Asignar
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-error/30 bg-error/5 px-3 py-2 text-label-sm text-error">
              <span className="material-symbols-outlined mr-1 align-middle text-[16px]">error</span>
              {error}
            </div>
          )}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
            )}
            {isSubmitting ? 'Guardando...' : selectedItem ? 'Guardar' : 'Crear'}
          </button>
        </div>
      </div>
    </div>
  );
}
