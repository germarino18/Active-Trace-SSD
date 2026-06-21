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
  danger: { icon: 'warning' },
  warning: { icon: 'error' },
  info: { icon: 'info' },
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
        style={{
          width: 400,
          maxWidth: '100%',
          background: 'var(--surface-container)',
          border: '1px solid var(--outline-variant)',
          borderRadius: 'var(--radius-lg)',
          padding: 28,
        }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <span
            className={`material-symbols-outlined`}
            style={{
              fontSize: 28,
              color: variant === 'danger'
                ? 'var(--error)'
                : variant === 'warning'
                  ? 'var(--warning)'
                  : 'var(--primary)',
            }}
          >
            {config.icon}
          </span>
          <div style={{ flex: 1 }}>
            <h3
              id="confirm-dialog-title"
              style={{ margin: 0, fontSize: 18, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}
            >
              {title}
            </h3>
            <div style={{ marginTop: 4, fontSize: 14, color: 'var(--on-surface-variant)', lineHeight: 1.5 }}>{message}</div>
            {cascadeWarning && (
              <div style={{
                marginTop: 12,
                padding: '8px 12px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid color-mix(in srgb, var(--warning) 30%, transparent)',
                background: 'color-mix(in srgb, var(--warning) 5%, transparent)',
                fontSize: 12,
                color: 'var(--warning)',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16, alignSelf: 'flex-start' }}>
                  warning_amber
                </span>
                {cascadeWarning}
              </div>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              height: 36,
              padding: '0 16px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--outline-variant)',
              background: 'transparent',
              color: 'var(--on-surface)',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background .15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--surface-container-low)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => {
              onConfirm();
              onClose();
            }}
            style={{
              height: 36,
              padding: '0 16px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid transparent',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background .15s ease, filter .15s ease',
              background: variant === 'danger' ? 'var(--error)' : variant === 'warning' ? 'var(--warning)' : 'var(--primary)',
              color: variant === 'danger' ? 'white' : variant === 'warning' ? 'black' : 'var(--on-primary)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.filter = 'brightness(1.1)')}
            onMouseLeave={(e) => (e.currentTarget.style.filter = 'none')}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
