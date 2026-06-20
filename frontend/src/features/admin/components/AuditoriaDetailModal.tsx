import type { RegistroAuditoria } from '../types/auditoria';

interface AuditoriaDetailModalProps {
  registro: RegistroAuditoria;
  onClose: () => void;
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function ActionBadge({ accion }: { accion: string }) {
  const prefixColorMap: Record<string, string> = {
    IMPERSONACION: 'var(--primary)',
    CARRERA: 'var(--primary)',
    MATERIA: 'var(--secondary)',
    COHORTE: 'var(--warning)',
    DICTADO: 'var(--warning)',
    USUARIO: 'var(--success)',
    ASIGNACION: 'var(--primary)',
    ENCUENTRO: 'var(--info)',
    COLOQUIO: 'var(--secondary)',
    AVISO: 'var(--info)',
    TAREA: 'var(--on-surface-variant)',
    COMUNICACION: 'var(--success)',
    LIQUIDACION: 'var(--error)',
    PERFIL: 'var(--primary)',
  };
  const prefix = accion.split('_')[0] ?? '';
  const color = prefixColorMap[prefix] ?? 'var(--on-surface-variant)';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        padding: '2px 10px',
        borderRadius: 'var(--radius-full)',
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: '0.01em',
        background: `color-mix(in srgb, ${color} 12%, transparent)`,
        color,
      }}
    >
      {accion.replace(/_/g, ' ')}
    </span>
  );
}

export function AuditoriaDetailModal({ registro, onClose }: AuditoriaDetailModalProps) {
  const detalle = registro.detalle;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(0,0,0,0.6)',
        backdropFilter: 'blur(4px)',
        WebkitBackdropFilter: 'blur(4px)',
        overflowY: 'auto',
        padding: '32px 16px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 560,
          background: 'var(--surface-container)',
          border: '1px solid var(--outline-variant)',
          borderRadius: 'var(--radius-lg)',
          padding: 28,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span
              className="material-symbols-outlined"
              style={{ fontSize: 24, color: 'var(--primary)' }}
            >
              receipt_long
            </span>
            <h3 style={{ margin: 0, fontSize: 20, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
              Detalle del registro
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 32,
              height: 32,
              border: 'none',
              borderRadius: 'var(--radius-full)',
              background: 'transparent',
              color: 'var(--outline)',
              cursor: 'pointer',
              transition: 'background .15s ease, color .15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--surface-container-low)';
              e.currentTarget.style.color = 'var(--on-surface-variant)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--outline)';
            }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>close</span>
          </button>
        </div>

        {/* Fields grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <Field label="Fecha" value={formatDate(registro.fecha_hora)} />
          <Field label="Usuario" value={registro.actor_nombre ?? '—'} />
          <Field label="Materia" value={registro.materia_nombre ?? '—'} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Tipo de acción
            </span>
            <ActionBadge accion={registro.accion ?? '—'} />
          </div>
          <Field label="Registros afectados" value={registro.filas_afectadas?.toString() ?? '—'} />
          <Field label="IP origen" value={registro.ip ?? '—'} />
        </div>

        {/* Detail JSON */}
        {detalle && Object.keys(detalle).length > 0 && (
          <div style={{ marginTop: 20 }}>
            <span style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>
              Detalle adicional
            </span>
            <pre
              style={{
                maxHeight: 200,
                overflow: 'auto',
                padding: '12px 14px',
                background: 'var(--surface-container-low)',
                border: '1px solid var(--outline-variant)',
                borderRadius: 'var(--radius-md)',
                fontSize: 12,
                color: 'var(--on-surface-variant)',
                fontFamily: 'var(--font-mono)',
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
                margin: 0,
              }}
            >
              {JSON.stringify(detalle, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </span>
      <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--on-surface)' }}>
        {value}
      </span>
    </div>
  );
}
