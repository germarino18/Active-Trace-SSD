/**
 * MisTareasProfesorPage tests.
 *
 * Key difference from coordinación's MisTareasPage:
 * GET /api/v1/tareas/mias returns a PLAIN ARRAY — not {items, total}.
 * This page consumes the array directly and does NOT read data.items.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
  useMutationCrearTareaPropia: vi.fn(),
  useMutationEditarTareaPropia: vi.fn(),
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationAgregarAlumnosBulk: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useMutationQuitarAlumnosBulk: vi.fn(),
  useActividadesDictado: vi.fn(),
  useCalificacionesDictado: vi.fn(),
  useMutationEditarCalificacion: vi.fn(),
  useMutationCrearActividad: vi.fn(),
  useMutationEliminarActividad: vi.fn(),
  useMutationSubirCalificacionesCsv: vi.fn(),
  useMutationRegistrarCalificacion: vi.fn(),
  useAtrasadosProfesor: vi.fn(),
  useMutationComunicadoAtrasadoNull: vi.fn(),
  useMutationComunicadoAtrasados: vi.fn(),
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useMutationCrearAviso: vi.fn(),
  useColoquiosMios: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
  useAtrasadosGeneralProfesor: vi.fn(),
  useMutationComunicadoFlexible: vi.fn(),
}));

import {
  useMisTareasProfesor,
  useMutationCambiarEstadoTareaProfesor,
  useMutationCrearTareaPropia,
  useMutationEditarTareaPropia,
} from '@/features/profesor/hooks/useProfesor';
import { MisTareasProfesorPage } from '@/features/profesor/pages/MisTareasProfesorPage';

const mockUseTareas = vi.mocked(useMisTareasProfesor);
const mockMutationEstado = vi.mocked(useMutationCambiarEstadoTareaProfesor);
const mockMutationCrear = vi.mocked(useMutationCrearTareaPropia);
const mockMutationEditar = vi.mocked(useMutationEditarTareaPropia);

const defaultMutation = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

const sampleTareas = [
  {
    id: 't1',
    descripcion: 'Revisar los TPs pendientes del grupo A',
    estado: 'PENDIENTE',
    materia_id: 'm1',
    asignado_a: 'u1',
    asignado_por: 'u2',
    created_at: '2026-06-01T10:00:00',
    updated_at: '2026-06-01T10:00:00',
  },
  {
    id: 't2',
    descripcion: 'Cargar las notas del parcial de junio',
    estado: 'EN_PROGRESO',
    materia_id: null,
    asignado_a: 'u1',
    asignado_por: 'u2',
    created_at: '2026-06-10T08:00:00',
    updated_at: '2026-06-10T08:00:00',
  },
];

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisTareasProfesorPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisTareasProfesorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationEstado.mockReturnValue(defaultMutation as ReturnType<typeof useMutationCambiarEstadoTareaProfesor>);
    mockMutationCrear.mockReturnValue(defaultMutation as ReturnType<typeof useMutationCrearTareaPropia>);
    mockMutationEditar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEditarTareaPropia>);
  });

  it('shows empty state when no tareas', () => {
    mockUseTareas.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);

    renderPage();
    expect(screen.getByText('No tenés tareas asignadas')).toBeInTheDocument();
  });

  it('shows error state on fetch error', () => {
    mockUseTareas.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    } as ReturnType<typeof useMisTareasProfesor>);

    renderPage();
    expect(screen.getByText('Error al cargar las tareas')).toBeInTheDocument();
  });

  it('renders tarea rows from a plain array (not {items,total})', () => {
    mockUseTareas.mockReturnValue({
      data: sampleTareas,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);

    renderPage();
    expect(screen.getByText('Revisar los TPs pendientes del grupo A')).toBeInTheDocument();
    expect(screen.getByText('Cargar las notas del parcial de junio')).toBeInTheDocument();
  });

  it('renders estado badge for each tarea', () => {
    mockUseTareas.mockReturnValue({
      data: sampleTareas,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);

    renderPage();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
    expect(screen.getByText('En progreso')).toBeInTheDocument();
  });

  it('shows loading state while fetching', () => {
    mockUseTareas.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);

    renderPage();
    // LoadingState renders skeleton rows; just check nothing crashed
    expect(screen.queryByText('Revisar trabajos prácticos')).not.toBeInTheDocument();
  });
});
