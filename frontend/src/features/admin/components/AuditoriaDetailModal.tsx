import type { RegistroAuditoria } from '../types/auditoria';

interface AuditoriaDetailModalProps {
  registro: RegistroAuditoria;
  onClose: () => void;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function AuditoriaDetailModal({ registro, onClose }: AuditoriaDetailModalProps) {
  const detalle = registro.detalle;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-xl border border-outline-variant bg-surface-container-lowest p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-headline-md text-headline-md text-on-surface">
            Detalle del registro
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full text-outline transition-colors hover:bg-surface-container-low hover:text-on-surface"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="Fecha" value={formatDate(registro.fecha)} />
            <Field label="Usuario" value={registro.usuario_nombre} />
            <Field label="Materia" value={registro.materia_nombre ?? '—'} />
            <Field label="Tipo de acción" value={registro.tipo_accion.replace(/_/g, ' ')} />
            <Field label="Registros afectados" value={registro.registros_afectados?.toString() ?? '—'} />
            <Field label="IP origen" value={registro.ip_origen ?? '—'} />
          </div>

          <div className="space-y-1">
            <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
              Agente de usuario
            </label>
            <p className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface break-all">
              {registro.agente_usuario ?? '—'}
            </p>
          </div>

          {detalle && Object.keys(detalle).length > 0 && (
            <div className="space-y-1">
              <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
                Detalle adicional
              </label>
              <pre className="max-h-48 overflow-auto rounded-lg border border-outline-variant bg-surface-container-lowest p-3 text-body-xs text-on-surface-variant font-mono whitespace-pre-wrap">
                {JSON.stringify(detalle, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-0.5">
      <label className="text-label-xs font-medium text-outline uppercase tracking-wider">
        {label}
      </label>
      <p className="text-body-sm text-on-surface font-medium">{value}</p>
    </div>
  );
}
