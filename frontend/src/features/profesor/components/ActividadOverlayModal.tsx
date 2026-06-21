/**
 * ActividadOverlayModal — portal-based overlay modal for actividad forms.
 *
 * Renders via ReactDOM.createPortal to document.body so it floats above the
 * overflow-hidden activity cards and the tab scroll flow (D3 of design.md).
 * Closes on backdrop click or Escape key.
 */
import { useEffect, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface ActividadOverlayModalProps {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
}

export function ActividadOverlayModal({ open, onClose, children }: ActividadOverlayModalProps) {
  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div
      data-testid="modal-backdrop"
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0,0,0,0.45)' }}
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        className="relative w-full max-w-2xl rounded-2xl bg-surface-container-lowest p-6 shadow-2xl"
        style={{ maxHeight: '90vh', overflowY: 'auto' }}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>,
    document.body,
  );
}
