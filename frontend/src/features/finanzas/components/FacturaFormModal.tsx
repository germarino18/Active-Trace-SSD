import { useEffect, useState, useRef, type ChangeEvent } from 'react';
import type { Factura } from '../types/facturas';

interface FacturaFormValues {
  docente_id: string;
  periodo: string;
  detalle: string;
}

interface FacturaFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (formData: FormData) => Promise<void>;
  selectedItem?: Factura | null;
}

export function FacturaFormModal({
  isOpen,
  onClose,
  onSave,
  selectedItem,
}: FacturaFormModalProps) {
  const [formValues, setFormValues] = useState<FacturaFormValues>({
    docente_id: '',
    periodo: '',
    detalle: '',
  });
  const [archivo, setArchivo] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (selectedItem) {
      setFormValues({
        docente_id: selectedItem.docente_id,
        periodo: selectedItem.periodo,
        detalle: selectedItem.detalle,
      });
    } else {
      setFormValues({ docente_id: '', periodo: '', detalle: '' });
      setArchivo(null);
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
    if (!formValues.docente_id || !formValues.periodo || !formValues.detalle) {
      setError('Completá todos los campos obligatorios');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const fd = new FormData();
      fd.append('docente_id', formValues.docente_id);
      fd.append('periodo', formValues.periodo);
      fd.append('detalle', formValues.detalle);
      if (archivo) {
        fd.append('archivo', archivo);
      }

      await onSave(fd);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar la factura');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setArchivo(e.target.files?.[0] ?? null);
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
        aria-labelledby="factura-form-title"
      >
        <div className="mb-4 flex items-center justify-between">
          <h3
            id="factura-form-title"
            className="font-headline-lg text-headline-lg text-on-surface"
          >
            {selectedItem ? 'Editar factura' : 'Nueva factura'}
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
          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Docente <span className="text-error">*</span>
            </label>
            <input
              type="text"
              value={formValues.docente_id}
              onChange={(e) =>
                setFormValues((prev) => ({ ...prev, docente_id: e.target.value }))
              }
              placeholder="ID del docente"
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Período <span className="text-error">*</span>
            </label>
            <input
              type="text"
              value={formValues.periodo}
              onChange={(e) =>
                setFormValues((prev) => ({ ...prev, periodo: e.target.value }))
              }
              placeholder="Ej: 2025-01"
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Detalle <span className="text-error">*</span>
            </label>
            <textarea
              value={formValues.detalle}
              onChange={(e) =>
                setFormValues((prev) => ({ ...prev, detalle: e.target.value }))
              }
              placeholder="Descripción de la factura..."
              rows={3}
              className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Archivo adjunto
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-outline-variant bg-surface-container-lowest p-4 transition-colors hover:border-primary hover:bg-primary/5"
            >
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
                className="hidden"
                disabled={isSubmitting}
              />
              <span className="material-symbols-outlined text-[32px] text-outline mb-1">
                upload_file
              </span>
              <p className="text-body-sm font-medium text-on-surface">
                {archivo ? archivo.name : 'Hacé clic para seleccionar un archivo'}
              </p>
              <p className="text-label-xs text-outline mt-1">
                {archivo
                  ? `${(archivo.size / 1024).toFixed(1)} KB`
                  : 'PDF, Excel, Word, etc.'}
              </p>
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
