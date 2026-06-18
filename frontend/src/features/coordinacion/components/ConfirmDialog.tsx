import { useEffect, type ReactNode } from 'react';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string | ReactNode;
  confirmLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  cascadeWarning?: string;
}

const variantConfig = {
  danger: {
    icon: 'warning',
    confirmClass:
      'bg-error text-white hover:bg-error/90',
  },
  warning: {
    icon: 'error',
    confirmClass:
      'bg-warning text-black hover:bg-warning/90',
  },
  info: {
    icon: 'info',
    confirmClass:
      'bg-primary text-on-primary hover:bg-primary/90',
  },
};

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirmar',
  variant = 'danger',
  cascadeWarning,
}: ConfirmDialogProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
    }
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const config = variantConfig[variant];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="mx-4 w-full max-w-md rounded-xl border border-outline-variant bg-surface p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
      >
        <div className="mb-4 flex items-start gap-3">
          <span
            className={`material-symbols-outlined text-[28px] ${
              variant === 'danger'
                ? 'text-error'
                : variant === 'warning'
                  ? 'text-warning'
                  : 'text-primary'
            }`}
          >
            {config.icon}
          </span>
          <div className="flex-1">
            <h3
              id="confirm-dialog-title"
              className="font-headline-lg text-headline-lg text-on-surface"
            >
              {title}
            </h3>
            <div className="mt-2 text-body-md text-on-surface-variant">{message}</div>
            {cascadeWarning && (
              <div className="mt-3 rounded-lg border border-warning/30 bg-warning/5 px-3 py-2 text-label-sm text-warning">
                <span className="material-symbols-outlined mr-1 align-middle text-[16px]">
                  warning_amber
                </span>
                {cascadeWarning}
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`rounded-lg px-4 py-2 text-label-sm font-medium transition-colors ${config.confirmClass}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
