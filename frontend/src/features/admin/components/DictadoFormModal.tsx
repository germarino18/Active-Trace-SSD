import { useEffect, useState } from 'react';
import { Input, Select, Button } from '@/shared/components/ds';
import type { Dictado, CrearDictadoData, ActualizarDictadoData } from '../types/dictados';
import type { Carrera, Cohorte, Materia } from '../types';

interface DictadoFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CrearDictadoData | ActualizarDictadoData) => Promise<void>;
  selectedItem?: Dictado | null;
  carreras: Carrera[];
  cohortes: Cohorte[];
  materias: Materia[];
}

export function DictadoFormModal({
  isOpen,
  onClose,
  onSave,
  selectedItem,
  carreras,
  cohortes,
  materias,
}: DictadoFormModalProps) {
  const [formValues, setFormValues] = useState<CrearDictadoData>({
    materia_id: '',
    carrera_id: '',
    cohorte_id: '',
    vig_desde: '',
    vig_hasta: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedItem) {
      setFormValues({
        materia_id: selectedItem.materia_id,
        carrera_id: selectedItem.carrera_id,
        cohorte_id: selectedItem.cohorte_id,
        vig_desde: selectedItem.vig_desde ?? '',
        vig_hasta: selectedItem.vig_hasta ?? '',
      });
    } else {
      setFormValues({
        materia_id: '',
        carrera_id: '',
        cohorte_id: '',
        vig_desde: '',
        vig_hasta: '',
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
    if (!formValues.materia_id || !formValues.carrera_id || !formValues.cohorte_id) {
      setError('Completá todos los campos obligatorios');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const payload: CrearDictadoData = {
        ...formValues,
        vig_desde: formValues.vig_desde || undefined,
        vig_hasta: formValues.vig_hasta || undefined,
      };
      await onSave(payload);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar el dictado');
    } finally {
      setIsSubmitting(false);
    }
  };

  const updateField = (field: keyof CrearDictadoData, value: string) => {
    setFormValues((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={isSubmitting ? undefined : onClose}
    >
      <div
        style={{ width: 400, maxWidth: '100%' }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dictado-form-title"
      >
        <div style={{ background: 'var(--surface-container)', border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-lg)', padding: 28 }}>
          <h1
            id="dictado-form-title"
            style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}
          >
            {selectedItem ? 'Editar dictado' : 'Nuevo dictado'}
          </h1>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            {selectedItem ? 'Modificá los datos del dictado.' : 'Asigná una materia a una carrera y cohorte.'}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <Select
              label="Materia"
              value={formValues.materia_id}
              onChange={(e) => updateField('materia_id', e.target.value)}
              error={error && !formValues.materia_id ? 'Campo obligatorio' : undefined}
            >
              <option value="">Seleccionar materia</option>
              {materias.map((m) => (
                <option key={m.id} value={m.id}>{m.nombre}</option>
              ))}
            </Select>

            <Select
              label="Carrera"
              value={formValues.carrera_id}
              onChange={(e) => updateField('carrera_id', e.target.value)}
              error={error && !formValues.carrera_id ? 'Campo obligatorio' : undefined}
            >
              <option value="">Seleccionar carrera</option>
              {carreras.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </Select>

            <Select
              label="Cohorte"
              value={formValues.cohorte_id}
              onChange={(e) => updateField('cohorte_id', e.target.value)}
              error={error && !formValues.cohorte_id ? 'Campo obligatorio' : undefined}
            >
              <option value="">Seleccionar cohorte</option>
              {cohortes.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </Select>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <Input
                label="Vigencia desde"
                type="date"
                value={formValues.vig_desde}
                onChange={(e) => updateField('vig_desde', e.target.value)}
              />
              <Input
                label="Vigencia hasta"
                type="date"
                value={formValues.vig_hasta}
                onChange={(e) => updateField('vig_hasta', e.target.value)}
              />
            </div>

            {error && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 12px', borderRadius: 8, border: '1px solid rgba(244, 67, 54, 0.3)', background: 'rgba(244, 67, 54, 0.05)', fontSize: 13, color: 'rgb(244, 67, 54)' }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>error</span>
                {error}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 28 }}>
            <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button type="button" variant="primary" onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? (
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
                  Guardando...
                </span>
              ) : (
                selectedItem ? 'Guardar cambios' : 'Crear dictado'
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
