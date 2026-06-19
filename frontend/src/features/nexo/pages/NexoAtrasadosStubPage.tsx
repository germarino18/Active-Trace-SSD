import { useNavigate } from 'react-router-dom';

export function NexoAtrasadosStubPage() {
  const navigate = useNavigate();
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, color: 'var(--on-surface)' }}>
          Atrasados — NEXO
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Supervisión de alumnos atrasados por carrera
        </p>
      </div>
      <div style={{ padding: 48, textAlign: 'center', background: 'var(--surface-container)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}>
        <span className="material-symbols-outlined" style={{ fontSize: 48, display: 'block', marginBottom: 12, color: 'var(--on-surface-variant)' }}>construction</span>
        <p style={{ margin: '0 0 4px', fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>Esta vista está en desarrollo</p>
        <p style={{ margin: '0 0 20px', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Próximamente podrás consultar los alumnos atrasados de las carreras bajo tu supervisión.
        </p>
        <button
          onClick={() => navigate('/dashboard')}
          style={{ padding: '8px 20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)', background: 'var(--surface)', color: 'var(--on-surface)', cursor: 'pointer', fontSize: 14 }}
        >
          Volver al dashboard
        </button>
      </div>
    </div>
  );
}
