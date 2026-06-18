import { useEffect, useState } from 'react';

interface CerrarLiquidacionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  periodo: string;
  totalDocentes: number;
  montoTotal: number;
}

export function CerrarLiquidacionModal({
  isOpen,
  onClose,
  onConfirm,
  periodo,
  totalDocentes,
  montoTotal,
}: CerrarLiquidacionModalProps) {
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

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await onConfirm();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error al cerrar la liquidación');
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
        aria-labelledby="cerrar-liquidacion-title"
      >
        <div className="mb-4 flex items-start gap-3">
          <span className="material-symbols-outlined text-[28px] text-warning">warning</span>
          <div className="flex-1">
            <h3
              id="cerrar-liquidacion-title"
              className="font-headline-lg text-headline-lg text-on-surface"
            >
              Cerrar liquidación
            </h3>
            <div className="mt-2 space-y-1 text-body-md text-on-surface-variant">
              <p>Estás por cerrar la liquidación del período <strong>{periodo}</strong>.</p>
              <p>Esta acción es irreversible y generará las facturas correspondientes.</p>
            </div>

            <div className="mt-3 rounded-lg border border-outline-variant bg-surface-container-low px-4 py-3">
              <div className="flex justify-between text-body-sm">
                <span className="text-on-surface-variant">Docentes</span>
                <span className="text-on-surface font-medium">{totalDocentes}</span>
              </div>
              <div className="flex justify-between text-body-sm mt-1">
                <span className="text-on-surface-variant">Monto total</span>
                <span className="text-on-surface font-semibold">${montoTotal.toLocaleString('es-AR')}</span>
              </div>
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
            className="flex items-center gap-1.5 rounded-lg bg-warning px-4 py-2 text-label-sm font-medium text-black transition-colors hover:bg-warning/90 disabled:opacity-50"
          >
            {isSubmitting && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/30 border-t-black" />
            )}
            {isSubmitting ? 'Cerrando...' : 'Cerrar liquidación'}
          </button>
        </div>
      </div>
    </div>
  );
}
