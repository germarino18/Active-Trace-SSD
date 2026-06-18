import { useEffect, useState, type ChangeEvent } from 'react';
import type { Usuario, CrearUsuarioData, EditarUsuarioData } from '../types';

type FormValues = CrearUsuarioData;

interface UsuarioFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CrearUsuarioData | EditarUsuarioData) => Promise<void>;
  selectedItem?: Usuario | null;
}

const ROLES = [
  { value: 'ALUMNO', label: 'Alumno' },
  { value: 'TUTOR', label: 'Tutor' },
  { value: 'PROFESOR', label: 'Profesor' },
  { value: 'COORDINADOR', label: 'Coordinador' },
  { value: 'NEXO', label: 'Nexo' },
  { value: 'ADMIN', label: 'Admin' },
  { value: 'FINANZAS', label: 'Finanzas' },
];

export function UsuarioFormModal({
  isOpen,
  onClose,
  onSave,
  selectedItem,
}: UsuarioFormModalProps) {
  const [formValues, setFormValues] = useState<FormValues>({
    nombre: '',
    apellido: '',
    email: '',
    rol: 'ALUMNO',
    activo: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        rol: 'ALUMNO',
        activo: true,
      });
    }
    setError(null);
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

  const handleSubmit = async () => {
    if (!formValues.nombre || !formValues.apellido || !formValues.email) {
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

  const updateField = (field: keyof FormValues, value: string | boolean) => {
    setFormValues((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
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
            >
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
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
