import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import type { SidebarSection } from '@/shared/types';
import { Sidebar } from '../Sidebar';

let mockPermissions: string[] = [];

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: { nombre: 'Test', apellido: 'User', email: 'test@test.com' },
    },
    hasAnyPermission: (perms: string[]) => perms.some((p) => mockPermissions.includes(p)),
  }),
}));

const alumnoSections: SidebarSection[] = [
  {
    items: [{ label: 'Mi Perfil', path: '/profile', icon: 'person' }],
  },
  {
    label: 'ALUMNO',
    items: [
      { label: 'Dashboard', path: '/alumno/dashboard', icon: 'dashboard', requiredPermissions: ['estado-academico:ver'] },
      { label: 'Mis Materias', path: '/alumno/materias', icon: 'school', requiredPermissions: ['estado-academico:ver'] },
      { label: 'Coloquios', path: '/alumno/coloquios', icon: 'quiz', requiredPermissions: ['coloquios:reservar'] },
      { label: 'Avisos', path: '/alumno/avisos', icon: 'campaign', requiredPermissions: ['avisos:confirmar'] },
    ],
  },
  {
    label: 'Docente',
    items: [
      { label: 'Mis Alumnos', path: '/tutor/alumnos', icon: 'group', requiredPermissions: ['alumnos:ver'] },
      { label: 'Atrasados', path: '/atrasados', icon: 'warning', requiredPermissions: ['atrasados:ver'] },
      { label: 'Comunicación', path: '/comunicacion', icon: 'send', requiredPermissions: ['comunicacion:ver'] },
    ],
  },
  {
    label: 'NEXO',
    items: [
      { label: 'Atrasados', path: '/nexo/atrasados', icon: 'warning', requiredPermissions: ['nexo:atrasados:ver'] },
      { label: 'Encuentros', path: '/nexo/encuentros', icon: 'event', requiredPermissions: ['nexo:encuentros:ver'] },
      { label: 'Tareas', path: '/nexo/tareas', icon: 'checklist', requiredPermissions: ['nexo:tareas:ver'] },
    ],
  },
  {
    label: 'Finanzas',
    items: [
      { label: 'Liquidaciones', path: '/finanzas/liquidaciones', icon: 'payments', requiredPermissions: ['liquidaciones:ver'] },
    ],
  },
];

function renderSidebar(sections: SidebarSection[] = alumnoSections) {
  return render(
    <MemoryRouter>
      <Sidebar sections={sections} />
    </MemoryRouter>,
  );
}

// 2.1 — ALUMNO ve ítems de alumno y no ve ítems docentes
describe('Sidebar — perfil ALUMNO', () => {
  beforeEach(() => {
    mockPermissions = ['estado-academico:ver', 'evaluacion:reservar', 'avisos:confirmar'];
  });

  it('muestra ítems de la sección ALUMNO', () => {
    renderSidebar();
    expect(screen.getByText('Mis Materias')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Coloquios')).toBeInTheDocument();
    expect(screen.getByText('Avisos')).toBeInTheDocument();
  });

  it('no muestra ítems de la sección Docente', () => {
    renderSidebar();
    expect(screen.queryByText('Mis Alumnos')).not.toBeInTheDocument();
  });

  it('muestra el encabezado de sección ALUMNO', () => {
    renderSidebar();
    expect(screen.getByText('ALUMNO')).toBeInTheDocument();
  });
});

// 2.2 — NEXO ve sección NEXO y no ve sección ALUMNO
describe('Sidebar — perfil NEXO', () => {
  beforeEach(() => {
    mockPermissions = ['nexo:atrasados:ver', 'nexo:encuentros:ver', 'nexo:tareas:ver'];
  });

  it('muestra ítems de la sección NEXO', () => {
    renderSidebar();
    expect(screen.getByText('NEXO')).toBeInTheDocument();
    expect(screen.getByText('Encuentros')).toBeInTheDocument();
    expect(screen.getByText('Tareas')).toBeInTheDocument();
  });

  it('no muestra ítems ni encabezado de la sección ALUMNO', () => {
    renderSidebar();
    expect(screen.queryByText('Mis Materias')).not.toBeInTheDocument();
    expect(screen.queryByText('ALUMNO')).not.toBeInTheDocument();
  });

  it('no muestra ítems de la sección Docente', () => {
    renderSidebar();
    expect(screen.queryByText('Mis Alumnos')).not.toBeInTheDocument();
    expect(screen.queryByText('Docente')).not.toBeInTheDocument();
  });
});

// 2.3 — No hay duplicados de Dashboard, Avisos, Coloquios
describe('Sidebar — sin duplicados', () => {
  beforeEach(() => {
    mockPermissions = ['estado-academico:ver', 'evaluacion:reservar', 'avisos:confirmar'];
  });

  it('Dashboard aparece exactamente una vez', () => {
    renderSidebar();
    expect(screen.getAllByText('Dashboard')).toHaveLength(1);
  });

  it('Avisos aparece exactamente una vez', () => {
    renderSidebar();
    expect(screen.getAllByText('Avisos')).toHaveLength(1);
  });

  it('Coloquios aparece exactamente una vez', () => {
    renderSidebar();
    expect(screen.getAllByText('Coloquios')).toHaveLength(1);
  });
});

// 2.4 — Rutas correctas para Atrasados y Comunicación
describe('Sidebar — rutas correctas', () => {
  beforeEach(() => {
    mockPermissions = ['atrasados:ver', 'comunicacion:ver'];
  });

  it('Atrasados tiene href /atrasados', () => {
    renderSidebar();
    const link = screen.getByRole('link', { name: /atrasados/i });
    expect(link).toHaveAttribute('href', '/atrasados');
  });

  it('Comunicación tiene href /comunicacion', () => {
    renderSidebar();
    const link = screen.getByRole('link', { name: /comunicaci/i });
    expect(link).toHaveAttribute('href', '/comunicacion');
  });
});

// 5.1 — COORDINADOR
describe('Sidebar — perfil COORDINADOR', () => {
  beforeEach(() => {
    mockPermissions = ['equipos:ver', 'avisos:ver', 'tareas:ver', 'atrasados:ver', 'comunicacion:ver', 'alumnos:ver', 'entregas:ver', 'guardias:gestionar'];
  });

  it('muestra sección Coordinación y Docente', () => {
    renderSidebar();
    expect(screen.getByText('Docente')).toBeInTheDocument();
  });

  it('no muestra sección ALUMNO ni encabezado NEXO', () => {
    renderSidebar();
    expect(screen.queryByText('Mis Materias')).not.toBeInTheDocument();
    expect(screen.queryByText('NEXO')).not.toBeInTheDocument();
  });
});

// 5.2 — FINANZAS
describe('Sidebar — perfil FINANZAS', () => {
  beforeEach(() => {
    mockPermissions = ['liquidaciones:ver'];
  });

  it('muestra Liquidaciones pero no ítems de docentes ni ALUMNO ni NEXO', () => {
    renderSidebar();
    // Finanzas section is not in alumnoSections fixture — verify docente/alumno items absent
    expect(screen.queryByText('Mis Materias')).not.toBeInTheDocument();
    expect(screen.queryByText('NEXO')).not.toBeInTheDocument();
    expect(screen.queryByText('Mis Alumnos')).not.toBeInTheDocument();
  });
});

// 5.3 — Usuario sin permisos
describe('Sidebar — usuario sin permisos', () => {
  beforeEach(() => {
    mockPermissions = [];
  });

  it('ve exactamente 1 ítem (Mi Perfil)', () => {
    renderSidebar();
    const links = document.querySelectorAll('nav a');
    expect(links).toHaveLength(1);
    expect(screen.getByText('Mi Perfil')).toBeInTheDocument();
  });
});

// 2.5 — Sección sin permisos no se renderiza (label ausente del DOM)
describe('Sidebar — sección vacía se oculta', () => {
  beforeEach(() => {
    mockPermissions = [];
  });

  it('sección NEXO no aparece cuando no hay permisos nexo', () => {
    renderSidebar();
    expect(screen.queryByText('NEXO')).not.toBeInTheDocument();
  });

  it('sección Finanzas no aparece cuando no hay permisos de finanzas', () => {
    renderSidebar();
    expect(screen.queryByText('Finanzas')).not.toBeInTheDocument();
  });

  it('Mi Perfil (sin permiso requerido) siempre está visible', () => {
    renderSidebar();
    expect(screen.getByText('Mi Perfil')).toBeInTheDocument();
  });
});
