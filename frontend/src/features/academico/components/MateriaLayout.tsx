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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Materia</h2>
          <p className="text-body-md text-on-surface-variant mt-1">ID: {id}</p>
        </div>
      </div>

      <div className="border-b border-outline-variant">
        <nav className="flex gap-4 -mb-px">
          {tabs.map((tab) => (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-3 text-label-md font-medium border-b-2 transition-colors ${
                  isActive
                    ? 'border-primary text-primary'
                    : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-outline-variant'
                }`
              }
            >
              <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <Outlet />
    </div>
  );
}
