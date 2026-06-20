import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useActividadesDictado: vi.fn(),
  useCalificacionesDictado: vi.fn(),
  useMutationEditarCalificacion: vi.fn(),
  useMutationCrearActividad: vi.fn(),
  useMutationEliminarActividad: vi.fn(),
  useMutationSubirCalificacionesCsv: vi.fn(),
  useAtrasadosProfesor: vi.fn(),
  useMutationComunicadoAtrasadoNull: vi.fn(),
  useMutationComunicadoAtrasados: vi.fn(),
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useMutationCrearAviso: vi.fn(),
  useColoquiosMios: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
}));

import {
  useAvisosMios,
  useMutationCrearAviso,
  useProfesorDashboard,
} from '@/features/profesor/hooks/useProfesor';
import { AvisosMiosPage } from '@/features/profesor/pages/AvisosMiosPage';

const mockUseAvisos = vi.mocked(useAvisosMios);
const mockMutationCrear = vi.mocked(useMutationCrearAviso);
const mockUseDashboard = vi.mocked(useProfesorDashboard);

const defaultMutation = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

const sampleAviso = {
  id: 'av1',
  tenant_id: 't1',
  alcance: 'POR_MATERIA',
  materia_id: 'm1',
  cohorte_id: null,
  rol_destino: null,
  severidad: 'INFO',
  titulo: 'Aviso de prueba',
  cuerpo: 'Cuerpo del aviso',
  inicio_en: new Date().toISOString(),
  fin_en: new Date(Date.now() + 86400000).toISOString(),
  orden: 0,
  activo: true,
  requiere_ack: false,
  acknowledged: false,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AvisosMiosPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AvisosMiosPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationCrear.mockReturnValue(defaultMutation as ReturnType<typeof useMutationCrearAviso>);
    mockUseDashboard.mockReturnValue({
      data: { materias_asignadas: [{ dictado_id: 'd1', materia_id: 'm1', materia_nombre: 'Matemáticas', n_alumnos: 5 }], total_alumnos: 5, total_encuentros: 0, total_atrasados: 0 },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);
  });

  it('shows empty state when no avisos', () => {
    mockUseAvisos.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAvisosMios>);
    renderPage();
    expect(screen.getByText('Mis Avisos')).toBeInTheDocument();
    expect(screen.getByText('No tenés avisos disponibles')).toBeInTheDocument();
  });

  it('renders aviso cards', () => {
    mockUseAvisos.mockReturnValue({ data: [sampleAviso], isLoading: false, isError: false } as ReturnType<typeof useAvisosMios>);
    renderPage();
    expect(screen.getByText('Aviso de prueba')).toBeInTheDocument();
    expect(screen.getByText('Cuerpo del aviso')).toBeInTheDocument();
    expect(screen.getByText('Info')).toBeInTheDocument();
  });

  it('shows "Crear aviso" button', () => {
    mockUseAvisos.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAvisosMios>);
    renderPage();
    expect(screen.getByText('Crear aviso')).toBeInTheDocument();
  });

  it('toggles crear aviso form on button click', () => {
    mockUseAvisos.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAvisosMios>);
    renderPage();
    // Initially the form is not shown
    expect(screen.queryByText('Nueva actividad')).not.toBeInTheDocument();
    // Click button to show form
    fireEvent.click(screen.getByText('Crear aviso'));
    // Form header should appear
    expect(screen.getByText('Crear aviso', { selector: 'h4' })).toBeInTheDocument();
  });

  it('form has alcance selector limited to POR_MATERIA/POR_COHORTE', () => {
    mockUseAvisos.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAvisosMios>);
    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /Crear aviso/i }));
    const alcanceSelect = screen.getByDisplayValue('Por materia');
    expect(alcanceSelect).toBeInTheDocument();
    // Should have exactly 2 options: por-materia and por-cohorte
    const options = alcanceSelect.querySelectorAll('option');
    expect(options.length).toBe(2);
    expect(options[0].value).toBe('POR_MATERIA');
    expect(options[1].value).toBe('POR_COHORTE');
  });

  it('shows materia selector with professor dictados when alcance is por-materia', () => {
    mockUseAvisos.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAvisosMios>);
    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /Crear aviso/i }));
    // Materia dropdown should be visible with the professor's materia
    expect(screen.getByText('Matemáticas')).toBeInTheDocument();
  });
});
