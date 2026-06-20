import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
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
  useAtrasadosProfesor,
  useActividadesDictado,
  useMutationComunicadoAtrasados,
} from '@/features/profesor/hooks/useProfesor';
import { AtrasadosDictadoPage } from '@/features/profesor/pages/AtrasadosDictadoPage';

const mockUseAtrasados = vi.mocked(useAtrasadosProfesor);
const mockUseActividades = vi.mocked(useActividadesDictado);
const mockMutationComunicado = vi.mocked(useMutationComunicadoAtrasados);

const defaultMutationReturn = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/profesor/dictados/d1/atrasados']}>
        <Routes>
          <Route path="/profesor/dictados/:dictadoId/atrasados" element={<AtrasadosDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

const sampleData = [
  { alumno_id: 'a1', nombre: 'Juan', apellido: 'Pérez', estado: 'aprobado' as const, subtipo: null, actividades_desaprobadas: 0, actividades_atrasado_null: 0 },
  { alumno_id: 'a2', nombre: 'Ana', apellido: 'García', estado: 'atrasado' as const, subtipo: 'desaprobado' as const, actividades_desaprobadas: 2, actividades_atrasado_null: 0 },
  { alumno_id: 'a3', nombre: 'Carlos', apellido: 'López', estado: 'atrasado' as const, subtipo: 'atrasado_null' as const, actividades_desaprobadas: 0, actividades_atrasado_null: 1 },
];

describe('AtrasadosDictadoPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationComunicado.mockReturnValue(defaultMutationReturn as ReturnType<typeof useMutationComunicadoAtrasados>);
    mockUseActividades.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
  });

  it('shows empty state when all alumnos are aprobados (aprobados hidden)', () => {
    mockUseAtrasados.mockReturnValue({
      data: [
        { alumno_id: 'a1', nombre: 'Juan', apellido: 'Pérez', estado: 'aprobado' as const, subtipo: null, actividades_desaprobadas: 0, actividades_atrasado_null: 0 },
      ],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosProfesor>);

    renderPage();
    // Aprobados are filtered out; only atrasados groups remain
    expect(screen.getByText(/Alumnos Atrasados \(0\)/)).toBeInTheDocument();
    expect(screen.getByText(/Todos los alumnos están al día/)).toBeInTheDocument();
  });

  it('shows empty state when no data at all', () => {
    mockUseAtrasados.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosProfesor>);

    renderPage();
    expect(screen.getByText(/Alumnos Atrasados \(0\)/)).toBeInTheDocument();
    expect(screen.getByText(/Todos los alumnos están al día/)).toBeInTheDocument();
  });

  it('shows only atrasado groups, not aprobados', () => {
    mockUseAtrasados.mockReturnValue({
      data: sampleData,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosProfesor>);

    renderPage();
    // Shows groups for atrasados only
    expect(screen.getByText('Desaprobados (1)')).toBeInTheDocument();
    expect(screen.getByText('Sin entregar (1)')).toBeInTheDocument();
    // Juan (aprobado) should NOT appear in any list
    expect(screen.queryByText('Juan')).not.toBeInTheDocument();
    // Ana (desaprobado) and Carlos (atrasado_null) should appear
    expect(screen.getByText('Ana')).toBeInTheDocument();
    expect(screen.getByText('Carlos')).toBeInTheDocument();
  });

  it('shows comunicado button for each atrasado group', () => {
    mockUseAtrasados.mockReturnValue({
      data: sampleData,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosProfesor>);

    renderPage();
    const comunicadoBtns = screen.getAllByText('Generar comunicado');
    expect(comunicadoBtns.length).toBe(2);
  });

  it('total atrasados count matches only atrasado items', () => {
    mockUseAtrasados.mockReturnValue({
      data: sampleData,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosProfesor>);

    renderPage();
    // 2 atrasados total (Ana + Carlos); Juan is aprobado and excluded
    expect(screen.getByText(/Alumnos Atrasados \(2\)/)).toBeInTheDocument();
  });
});
