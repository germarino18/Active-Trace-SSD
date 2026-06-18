import { useEffect, useState } from 'react';
import type { RolSalarial, SalarioBase, PlusSalarial, SalarioBaseFormData, PlusFormData } from '../types/grilla-salarial';

type ModalMode = 'salario-base' | 'plus';

interface SalaryFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: SalarioBaseFormData | PlusFormData) => Promise<void>;
  mode: ModalMode;
  selectedItem?: SalarioBase | PlusSalarial;
}

const roles: { value: RolSalarial; label: string }[] = [
  { value: 'PROFESOR', label: 'Profesor' },
  { value: 'TUTOR', label: 'Tutor' },
  { value: 'NEXO', label: 'Nexo' },
  { value: 'COORDINADOR', label: 'Coordinador' },
];

const modeConfig: Record<ModalMode, { titleCrear: string; titleEditar: string }> = {
  'salario-base': { titleCrear: 'Nuevo salario base', titleEditar: 'Editar salario base' },
  plus: { titleCrear: 'Nuevo plus', titleEditar: 'Editar plus' },
};

const initialSalarioBase: SalarioBaseFormData = {
  rol: 'PROFESOR',
  importe: 0,
  vigencia_desde: '',
  vigencia_hasta: '',
};

const initialPlus: PlusFormData = {
  clave: '',
  rol: 'PROFESOR',
  descripcion: '',
  importe: 0,
  vigencia_desde: '',
  vigencia_hasta: '',
};

function isPlusMode(mode: ModalMode, _item?: SalarioBase | PlusSalarial): _item is PlusSalarial {
  return mode === 'plus';
}

export function SalaryFormModal({ isOpen, onClose, onSubmit, mode, selectedItem }: SalaryFormModalProps) {
  const [formData, setFormData] = useState<SalarioBaseFormData | PlusFormData>(initialSalarioBase);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (selectedItem) {
      if (isPlusMode(mode, selectedItem)) {
        setFormData({
          clave: selectedItem.clave,
          rol: selectedItem.rol,
          descripcion: selectedItem.descripcion,
          importe: selectedItem.importe,
          vigencia_desde: selectedItem.vigencia_desde,
          vigencia_hasta: selectedItem.vigencia_hasta ?? '',
        });
      } else {
        setFormData({
          rol: selectedItem.rol,
          importe: selectedItem.importe,
          vigencia_desde: selectedItem.vigencia_desde,
          vigencia_hasta: selectedItem.vigencia_hasta ?? '',
        });
      }
    } else {
      setFormData(mode === 'salario-base' ? { ...initialSalarioBase } : { ...initialPlus });
    }
    setValidationErrors({});
    setError(null);
  }, [selectedItem, mode, isOpen]);

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

  const config = modeConfig[mode];

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.vigencia_desde) {
      errors.vigencia_desde = 'La fecha de inicio es obligatoria';
    }

    if (formData.vigencia_hasta && formData.vigencia_desde && formData.vigencia_hasta <= formData.vigencia_desde) {
      errors.vigencia_hasta = 'La fecha de fin debe ser posterior a la de inicio';
    }

    if (formData.importe <= 0) {
      errors.importe = 'El importe debe ser mayor a 0';
    }

    if (mode === 'plus') {
      const plusData = formData as PlusFormData;
      if (!plusData.clave.trim()) {
        errors.clave = 'La clave es obligatoria';
      }
      if (!plusData.descripcion.trim()) {
        errors.descripcion = 'La descripción es obligatoria';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const data = {
        ...formData,
        vigencia_hasta: formData.vigencia_hasta || undefined,
      };
      await onSubmit(data);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error al guardar');
    } finally {
      setIsSubmitting(false);
    }
  };

  const updateField = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
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
        aria-labelledby="salary-form-title"
      >
        <div className="mb-6 flex items-center justify-between">
          <h3
            id="salary-form-title"
            className="font-headline-lg text-headline-lg text-on-surface"
          >
            {selectedItem ? config.titleEditar : config.titleCrear}
          </h3>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-on-surface disabled:opacity-50"
            aria-label="Cerrar"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="space-y-4">
          {mode === 'plus' && (
            <div>
              <label
                htmlFor="clave"
                className="mb-1.5 block text-label-sm font-medium text-on-surface-variant"
              >
                Clave
              </label>
              <input
                id="clave"
                type="text"
                value={(formData as PlusFormData).clave}
                onChange={(e) => updateField('clave', e.target.value)}
                className={`w-full rounded-lg border bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary ${
                  validationErrors.clave ? 'border-error' : 'border-outline-variant'
                }`}
                placeholder="Ej: PLUS-001"
              />
              {validationErrors.clave && (
                <p className="mt-1 text-label-xs text-error">{validationErrors.clave}</p>
              )}
            </div>
          )}

          <div>
            <label
              htmlFor="rol"
              className="mb-1.5 block text-label-sm font-medium text-on-surface-variant"
            >
              Rol
            </label>
            <select
              id="rol"
              value={formData.rol}
              onChange={(e) => updateField('rol', e.target.value)}
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {roles.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          {mode === 'plus' && (
            <div>
              <label
                htmlFor="descripcion"
                className="mb-1.5 block text-label-sm font-medium text-on-surface-variant"
              >
                Descripción
              </label>
              <input
                id="descripcion"
                type="text"
                value={(formData as PlusFormData).descripcion}
                onChange={(e) => updateField('descripcion', e.target.value)}
                className={`w-full rounded-lg border bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary ${
                  validationErrors.descripcion ? 'border-error' : 'border-outline-variant'
                }`}
                placeholder="Descripción del plus"
              />
              {validationErrors.descripcion && (
                <p className="mt-1 text-label-xs text-error">{validationErrors.descripcion}</p>
              )}
            </div>
          )}

          <div>
            <label
              htmlFor="importe"
              className="mb-1.5 block text-label-sm font-medium text-on-surface-variant"
            >
              Importe ($)
            </label>
            <input
              id="importe"
              type="number"
              min={0}
              step={0.01}
              value={formData.importe || ''}
              onChange={(e) => updateField('importe', parseFloat(e.target.value) || 0)}
              className={`w-full rounded-lg border bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary ${
                validationErrors.importe ? 'border-error' : 'border-outline-variant'
              }`}
              placeholder="0.00"
            />
            {validationErrors.importe && (
              <p className="mt-1 text-label-xs text-error">{validationErrors.importe}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="vigencia_desde"
                className="mb-1.5 block text-label-sm font-medium text-on-surface-variant"
              >
                Vigencia desde
              </label>
              <input
                id="vigencia_desde"
                type="date"
                value={formData.vigencia_desde}
                onChange={(e) => updateField('vigencia_desde', e.target.value)}
                className={`w-full rounded-lg border bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary ${
                  validationErrors.vigencia_desde ? 'border-error' : 'border-outline-variant'
                }`}
              />
              {validationErrors.vigencia_desde && (
                <p className="mt-1 text-label-xs text-error">{validationErrors.vigencia_desde}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="vigencia_hasta"
                className="mb-1.5 block text-label-sm font-medium text-on-surface-variant"
              >
                Vigencia hasta
              </label>
              <input
                id="vigencia_hasta"
                type="date"
                value={formData.vigencia_hasta || ''}
                onChange={(e) => updateField('vigencia_hasta', e.target.value)}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {validationErrors.vigencia_hasta && (
                <p className="mt-1 text-label-xs text-error">{validationErrors.vigencia_hasta}</p>
              )}
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
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            )}
            {isSubmitting ? 'Guardando...' : selectedItem ? 'Guardar' : 'Crear'}
          </button>
        </div>
      </div>
    </div>
  );
}
