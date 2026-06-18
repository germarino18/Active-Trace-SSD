import type { ComunicacionDestinatario } from '../types';

interface PreviewComunicacionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  asunto: string;
  cuerpo: string;
  destinatarios: ComunicacionDestinatario[];
  isSending?: boolean;
}

export function PreviewComunicacionModal({
  isOpen,
  onClose,
  onConfirm,
  asunto,
  cuerpo,
  destinatarios,
  isSending,
}: PreviewComunicacionModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="mx-4 w-full max-w-2xl rounded-xl bg-surface-container-lowest p-lg shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-headline-md font-semibold text-on-surface">Vista Previa</h3>
          <button
            type="button"
            onClick={onClose}
            disabled={isSending}
            className="text-outline hover:text-on-surface"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-label-xs uppercase tracking-wider text-outline mb-1">Asunto</p>
            <p className="text-body-md font-medium text-on-surface">{asunto}</p>
          </div>

          <div>
            <p className="text-label-xs uppercase tracking-wider text-outline mb-1">Cuerpo</p>
            <p className="text-body-md text-on-surface-variant whitespace-pre-wrap">{cuerpo}</p>
          </div>

          <div>
            <p className="text-label-xs uppercase tracking-wider text-outline mb-2">
              Destinatarios ({destinatarios.length})
            </p>
            <div className="max-h-48 space-y-2 overflow-y-auto">
              {destinatarios.map((d) => (
                <div
                  key={d.alumno.id}
                  className="rounded-lg border border-outline-variant p-3"
                >
                  <p className="text-label-sm font-medium text-on-surface">
                    {d.alumno.apellido}, {d.alumno.nombre}
                  </p>
                  <p className="text-label-xs text-on-surface-variant mt-1">{d.asunto}</p>
                  <p className="text-label-xs text-on-surface-variant mt-1">{d.cuerpo}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={isSending}
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-md font-medium text-on-surface transition-colors hover:bg-surface-container-low disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isSending}
            className="rounded-lg bg-primary px-6 py-2 text-label-md font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {isSending ? 'Enviando...' : 'Confirmar envío'}
          </button>
        </div>
      </div>
    </div>
  );
}
