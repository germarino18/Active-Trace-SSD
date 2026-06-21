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
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
}));

vi.mock('@/features/profesor/services/profesor.service', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/profesor/services/profesor.service')>();
  return {
    ...actual,
    buildPlantillaCsvUrl: (id: string) => `/api/v1/actividades/${id}/plantilla-csv`,
    downloadPlantillaCsv: vi.fn().mockResolvedValue(undefined),
  };
});

import {
  useActividadesDictado,
  useCalificacionesDictado,
  usePadronDictado,
  useMutationEditarCalificacion,
  useMutationCrearActividad,
  useMutationSubirCalificacionesCsv,
  useMutationRegistrarCalificacion,
} from '@/features/profesor/hooks/useProfesor';
import { ActividadesDictadoPage } from '@/features/profesor/pages/ActividadesDictadoPage';

const mockUseActividades = vi.mocked(useActividadesDictado);
const mockUseCalificaciones = vi.mocked(useCalificacionesDictado);
const mockUsePadron = vi.mocked(usePadronDictado);
const mockMutationEditar = vi.mocked(useMutationEditarCalificacion);
const mockMutationCrear = vi.mocked(useMutationCrearActividad);
const mockMutationCsv = vi.mocked(useMutationSubirCalificacionesCsv);
const mockMutationRegistrar = vi.mocked(useMutationRegistrarCalificacion);

const defaultMutation = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

const sampleActividad = { id: 'act1', nombre: 'Tarea 1', tipo: 'tarea', fecha_limite: '2025-12-01' };
const sampleCalificacion = {
  id: 'cal1',
  entrada_padron_id: 'ep1',
  dictado_id: 'd1',
  actividad: 'Tarea 1',
  actividad_id: 'act1',
  nota_numerica: 8,
  nota_textual: null,
  aprobado: true,
  origen: 'manual',
};
const samplePadron = [{ id: 'ep1', nombre: 'Juan', apellidos: 'Pérez', email: null, comision: null }];

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/profesor/dictados/d1/actividades']}>
        <Routes>
          <Route path="/profesor/dictados/:dictadoId/actividades" element={<ActividadesDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ActividadesDictadoPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationEditar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEditarCalificacion>);
    mockMutationCrear.mockReturnValue(defaultMutation as ReturnType<typeof useMutationCrearActividad>);
    mockMutationCsv.mockReturnValue(defaultMutation as ReturnType<typeof useMutationSubirCalificacionesCsv>);
    mockMutationRegistrar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationRegistrarCalificacion>);
    mockUsePadron.mockReturnValue({ data: samplePadron, isLoading: false, isError: false } as ReturnType<typeof usePadronDictado>);
  });

  it('shows empty state when no actividades or calificaciones', () => {
    mockUseActividades.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    expect(screen.getByText('Actividades')).toBeInTheDocument();
    expect(screen.getByText(/No hay actividades/)).toBeInTheDocument();
  });

  it('renders actividad card with nombre and tipo', () => {
    mockUseActividades.mockReturnValue({ data: [sampleActividad], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [sampleCalificacion], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    expect(screen.getByText('Tarea 1')).toBeInTheDocument();
    expect(screen.getByText('(tarea)')).toBeInTheDocument();
  });

  it('shows plantilla CSV download button for actividad with id (authenticated download)', () => {
    // The CSV download is now a <button> that calls downloadPlantillaCsv() via axios+auth.
    // A plain <a href> would download a 401 JSON because the endpoint requires JWT auth.
    mockUseActividades.mockReturnValue({ data: [sampleActividad], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    // Should be a <button>, not an <a> (no plain href download)
    const btn = screen.getByText('Plantilla CSV').closest('button');
    expect(btn).toBeInTheDocument();
    // Should NOT be a plain anchor with href (that would bypass auth)
    const anchor = screen.queryByText('Plantilla CSV')?.closest('a');
    expect(anchor).not.toBeInTheDocument();
  });

  it('shows Subir CSV button for actividad with id', () => {
    mockUseActividades.mockReturnValue({ data: [sampleActividad], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    expect(screen.getByText('Subir CSV')).toBeInTheDocument();
  });

  it('shows "Crear actividad" button and toggles modal', () => {
    mockUseActividades.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    const btn = screen.getByText('Crear actividad');
    fireEvent.click(btn);
    expect(screen.getByText('Nueva actividad')).toBeInTheDocument();
  });

  it('matches grade to actividad by actividad_id', () => {
    mockUseActividades.mockReturnValue({ data: [sampleActividad], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [sampleCalificacion], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    // Grade row should appear under the Tarea 1 card
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
  });

  it('shows legacy actividad (null id) without CSV buttons', () => {
    const legacyCal = { ...sampleCalificacion, actividad_id: null, actividad: 'Trabajo Práctico Antiguo' };
    mockUseActividades.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [legacyCal], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);

    renderPage();
    expect(screen.getByText('Trabajo Práctico Antiguo')).toBeInTheDocument();
    expect(screen.getByText('importada')).toBeInTheDocument();
    expect(screen.queryByText('Plantilla CSV')).not.toBeInTheDocument();
    expect(screen.queryByText('Subir CSV')).not.toBeInTheDocument();
  });
});
