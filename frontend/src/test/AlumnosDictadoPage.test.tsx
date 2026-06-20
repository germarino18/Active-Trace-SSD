/**
 * AlumnosDictadoPage — tests updated for multi-select add/baja.
 *
 * The page now uses:
 * - useMutationAgregarAlumnosBulk: POST {usuario_ids:[...]} to add multiple alumnos
 * - useMutationQuitarAlumnosBulk: POST {entrada_padron_ids:[...]} to baja multiple alumnos
 * Old single-add/single-remove are gone from this page.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationAgregarAlumnosBulk: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useMutationQuitarAlumnosBulk: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
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
  useAtrasadosGeneralProfesor: vi.fn(),
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
}));

import {
  usePadronDictado,
  useMutationAgregarAlumnosBulk,
  useMutationQuitarAlumnosBulk,
  useAlumnosDisponibles,
} from '@/features/profesor/hooks/useProfesor';
import { AlumnosDictadoPage } from '@/features/profesor/pages/AlumnosDictadoPage';

const mockUsePadron = vi.mocked(usePadronDictado);
const mockAgregarBulk = vi.mocked(useMutationAgregarAlumnosBulk);
const mockQuitarBulk = vi.mocked(useMutationQuitarAlumnosBulk);
const mockAlumnosDisponibles = vi.mocked(useAlumnosDisponibles);

const defaultMutationReturn = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
  reset: vi.fn(),
};

const defaultDisponiblesReturn = {
  data: [],
  isLoading: false,
  isError: false,
};

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/profesor/dictados/d1/alumnos']}>
        <Routes>
          <Route path="/profesor/dictados/:dictadoId/alumnos" element={<AlumnosDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AlumnosDictadoPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAgregarBulk.mockReturnValue(defaultMutationReturn as ReturnType<typeof useMutationAgregarAlumnosBulk>);
    mockQuitarBulk.mockReturnValue(defaultMutationReturn as ReturnType<typeof useMutationQuitarAlumnosBulk>);
    mockAlumnosDisponibles.mockReturnValue(defaultDisponiblesReturn as ReturnType<typeof useAlumnosDisponibles>);
  });

  it('renders empty state when no alumnos', () => {
    mockUsePadron.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof usePadronDictado>);

    renderPage();
    expect(screen.getByText('No hay alumnos en el padrón')).toBeInTheDocument();
  });

  it('renders alumno table when data is present', () => {
    mockUsePadron.mockReturnValue({
      data: [
        { id: 'e1', nombre: 'Juan', apellidos: 'Pérez', email: 'jp@test.com', comision: 'A' },
        { id: 'e2', nombre: 'Ana', apellidos: 'García', email: null, comision: null },
      ],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof usePadronDictado>);

    renderPage();
    expect(screen.getByText('Juan')).toBeInTheDocument();
    expect(screen.getByText('Pérez')).toBeInTheDocument();
    expect(screen.getByText('Ana')).toBeInTheDocument();
    expect(screen.getByText('jp@test.com')).toBeInTheDocument();
    expect(screen.getByText('A')).toBeInTheDocument();
  });

  it('renders error state on error', () => {
    mockUsePadron.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    } as ReturnType<typeof usePadronDictado>);

    renderPage();
    expect(screen.getByText('Error al cargar el padrón')).toBeInTheDocument();
  });

  it('shows agregar alumno button (CSV download removed — moved to per-actividad flow)', () => {
    mockUsePadron.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof usePadronDictado>);

    renderPage();
    expect(screen.getByText('Agregar alumno')).toBeInTheDocument();
    // CSV download was removed from alumnos tab; now lives per-actividad in ActividadesDictadoPage
    expect(screen.queryByText('Descargar CSV')).not.toBeInTheDocument();
  });

  it('shows checkboxes for multi-select when alumnos are present', () => {
    mockUsePadron.mockReturnValue({
      data: [
        { id: 'e1', nombre: 'Juan', apellidos: 'Pérez', email: null, comision: null },
        { id: 'e2', nombre: 'Ana', apellidos: 'García', email: null, comision: null },
      ],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof usePadronDictado>);

    renderPage();
    // Checkboxes: one per row + the select-all header checkbox
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBe(3); // 1 select-all + 2 rows
  });

  it('shows bulk-baja action bar after selecting alumnos', () => {
    mockUsePadron.mockReturnValue({
      data: [
        { id: 'e1', nombre: 'Juan', apellidos: 'Pérez', email: null, comision: null },
      ],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof usePadronDictado>);

    renderPage();

    const rowCheckbox = screen.getByLabelText('Seleccionar Juan Pérez');
    fireEvent.click(rowCheckbox);

    expect(screen.getByText('1 alumno seleccionado')).toBeInTheDocument();
    expect(screen.getByText('Dar de baja seleccionados')).toBeInTheDocument();
  });

  it('shows bulk-add form with checkboxes when alumnos disponibles', () => {
    mockUsePadron.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof usePadronDictado>);
    mockAlumnosDisponibles.mockReturnValue({
      data: [
        { usuario_id: 'u1', nombre: 'Pedro', apellidos: 'Martín', email: 'p@test.com' },
        { usuario_id: 'u2', nombre: 'Lucía', apellidos: 'Soto', email: null },
      ],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAlumnosDisponibles>);

    renderPage();

    // Open the add form
    fireEvent.click(screen.getByText('Agregar alumno'));

    expect(screen.getByText('Agregar alumnos al padrón')).toBeInTheDocument();
    expect(screen.getByText('Martín, Pedro')).toBeInTheDocument();
    expect(screen.getByText('Soto, Lucía')).toBeInTheDocument();
  });
});
