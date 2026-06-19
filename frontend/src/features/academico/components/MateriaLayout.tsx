import { NavLink, Outlet, useParams } from 'react-router-dom';

const tabs = [
  { label: 'Importar', path: 'importar', icon: 'upload_file' },
  { label: 'Atrasados', path: 'atrasados', icon: 'warning' },
  { label: 'Comunicar', path: 'comunicar', icon: 'send' },
  { label: 'Entregas Pendientes', path: 'entregas-pendientes', icon: 'assignment_late' },
  { label: 'Monitor', path: 'monitor', icon: 'monitoring' },
];

export function MateriaLayout() {
  const { id } = useParams<{ id: string }>();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Materia</h2>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>ID: {id}</p>
        </div>
      </div>

      <div style={{ borderBottom: '1px solid var(--outline-variant)' }}>
        <nav style={{ display: 'flex', gap: 4, marginBottom: -1 }}>
          {tabs.map((tab) => (
            <NavLink
              key={tab.path}
              to={tab.path}
              style={({ isActive }) => ({
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '10px 16px',
                fontSize: 14,
                fontWeight: 500,
                fontFamily: 'var(--font-sans)',
                textDecoration: 'none',
                borderBottom: `2px solid ${isActive ? 'var(--primary)' : 'transparent'}`,
                color: isActive ? 'var(--primary)' : 'var(--on-surface-variant)',
                transition: 'color .15s ease, border-color .15s ease',
              })}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{tab.icon}</span>
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <Outlet />
    </div>
  );
}
