import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GuardiasListPage } from '@/features/tutor/pages/GuardiasListPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

let mockData: { items: unknown[]; total: number } = { items: [], total: 0 };
let mockIsLoading = false;
let mockIsError = false;
const mockMutateAsync = vi.fn();

vi.mock('@/features/tutor/hooks/useGuardias', () => ({
  useGuardias: () => ({
    data: mockData,
    isLoading: mockIsLoading,
    isError: mockIsError,
    refetch: vi.fn(),
  }),
  useRegistrarGuardia: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
    isError: false,
    error: null,
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
        <GuardiasListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('GuardiasListPage', () => {
  beforeEach(() => {
    mockData = { items: [], total: 0 };
    mockIsLoading = false;
    mockIsError = false;
    mockMutateAsync.mockReset();
  });

  it('renders page title', () => {
    renderPage();
    expect(screen.getByText('Guardias')).toBeInTheDocument();
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
  });

  it('shows empty state when no guardias', () => {
    renderPage();
    expect(screen.getByText('No hay guardias registradas')).toBeInTheDocument();
  });

  it('renders guardia list in table', () => {
    mockData = {
      items: [
        { id: 'g1', fecha: '2024-06-15', materia_nombre: 'Matemática', hora_inicio: '10:00', hora_fin: '12:00', estado: 'Pendiente' },
        { id: 'g2', fecha: '2024-06-16', materia_nombre: 'Física', hora_inicio: '14:00', hora_fin: '16:00', estado: 'Realizado' },
      ],
      total: 2,
    };
    renderPage();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
    expect(screen.getByText('Realizado')).toBeInTheDocument();
  });

  it('shows Nueva Guardia button', () => {
    renderPage();
    expect(screen.getByText('Nueva Guardia')).toBeInTheDocument();
  });

  it('shows registration form when clicking Nueva Guardia', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByText('Nueva Guardia'));
    expect(screen.getByText('Registrar Guardia')).toBeInTheDocument();
    expect(screen.getByLabelText('Fecha *')).toBeInTheDocument();
    expect(screen.getByLabelText('Hora Inicio *')).toBeInTheDocument();
    expect(screen.getByLabelText('Hora Fin *')).toBeInTheDocument();
  });
});
