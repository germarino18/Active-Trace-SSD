import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TutorAlumnosPage } from '@/features/tutor/pages/TutorAlumnosPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

let mockData: unknown[] = [];
let mockIsLoading = false;
let mockIsError = false;

vi.mock('@/features/tutor/hooks/useTutorAlumnos', () => ({
  useTutorAlumnos: () => ({
    data: mockData,
    isLoading: mockIsLoading,
    isError: mockIsError,
    refetch: vi.fn(),
  }),
}));

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['TUTOR'], permissions: [] } },
    hasPermission: () => true,
    hasAnyPermission: () => true,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <TutorAlumnosPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('TutorAlumnosPage', () => {
  beforeEach(() => {
    mockData = [];
    mockIsLoading = false;
    mockIsError = false;
  });

  it('renders page title', () => {
    renderPage();
    expect(screen.getByText('Mis Alumnos')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockIsLoading = true;
    renderPage();
    const loadingRows = document.querySelectorAll('.animate-pulse');
    expect(loadingRows.length).toBeGreaterThan(0);
  });

  it('shows error state', () => {
    mockIsError = true;
    renderPage();
    expect(screen.getByText('Error al cargar datos')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    renderPage();
    expect(screen.getByText('No hay alumnos asignados')).toBeInTheDocument();
  });

  it('renders alumno data in table', () => {
    mockData = [
      { id: 'a1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', materia_nombre: 'Matemática', comision: 'A' },
      { id: 'a2', nombre: 'María', apellido: 'García', email: 'maria@test.com', materia_nombre: 'Física', comision: 'B' },
    ];
    renderPage();
    expect(screen.getByText('Juan')).toBeInTheDocument();
    expect(screen.getByText('Pérez')).toBeInTheDocument();
    expect(screen.getByText('María')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
  });

  it('shows Ver detalle buttons for each row', () => {
    mockData = [
      { id: 'a1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', materia_nombre: 'Matemática', comision: 'A' },
    ];
    renderPage();
    const buttons = screen.getAllByText('Ver detalle');
    expect(buttons.length).toBe(1);
  });
});
