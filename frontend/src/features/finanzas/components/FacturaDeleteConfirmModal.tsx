import { useEffect, useState } from 'react';
import type { Factura } from '../types/facturas';

interface FacturaDeleteConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  factura: Factura | null;
}

export function FacturaDeleteConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  factura,
}: FacturaDeleteConfirmModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
    }
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose, isSubmitting]);

  if (!isOpen || !factura) return null;

  const handleConfirm = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await onConfirm();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error al eliminar la factura');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={isSubmitting ? undefined : onClose}
    >
      <div
        className="mx-4 w-full max-w-md rounded-xl border border-outline-variant bg-surface p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-factura-title"
      >
        <div className="mb-4 flex items-start gap-3">
          <span className="material-symbols-outlined text-[28px] text-error">warning</span>
          <div className="flex-1">
            <h3
              id="delete-factura-title"
              className="font-headline-lg text-headline-lg text-on-surface"
            >
              Eliminar factura
            </h3>
            <div className="mt-2 text-body-md text-on-surface-variant">
              <p>
                ¿Estás seguro de que querés eliminar la factura de{' '}
                <strong>{factura.docente_nombre}</strong> del período{' '}
                <strong>{factura.periodo}</strong>?
              </p>
              <p className="mt-1">Esta acción no se puede deshacer.</p>
            </div>

            {error && (
              <div className="mt-3 rounded-lg border border-error/30 bg-error/5 px-3 py-2 text-label-sm text-error">
                <span className="material-symbols-outlined mr-1 align-middle text-[16px]">error</span>
                {error}
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3">
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
            onClick={handleConfirm}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 rounded-lg bg-error px-4 py-2 text-label-sm font-medium text-white transition-colors hover:bg-error/90 disabled:opacity-50"
          >
            {isSubmitting && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            )}
            {isSubmitting ? 'Eliminando...' : 'Eliminar'}
          </button>
        </div>
      </div>
    </div>
  );
}
