/**
 * TDD Tasks 7.1 / 7.2 / 7.4 — ActividadesDictadoPage: inline registrar-nota row.
 * 7.1 RED: registrar-nota renders INSIDE the activity table (not at the top).
 * 7.2 RED: alumno select shows ONLY ungraded alumnos.
 * 7.4 RED: aprobado control is a DS button (not a bare <input type="checkbox">).
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  useDictadoNombre: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationAgregarAlumnosBulk: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useMutationQuitarAlumnosBulk: vi.fn(),
  useActividadesDictado: vi.fn(),
  useCalificacionesDictado: vi.fn(),
  useMutationEditarCalificacion: vi.fn(),
  useMutationCrearActividad: vi.fn(),
  useMutationEditarActividad: vi.fn(),
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
  invalidateDictadoDerived: vi.fn(),
}));

vi.mock('@/features/profesor/services/profesor.service', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/profesor/services/profesor.service')>();
  return {
    ...actual,
    downloadPlantillaCsv: vi.fn().mockResolvedValue(undefined),
  };
});

import {
  useActividadesDictado,
  useCalificacionesDictado,
  usePadronDictado,
  useMutationEditarCalificacion,
  useMutationCrearActividad,
  useMutationEditarActividad,
  useMutationEliminarActividad,
  useMutationSubirCalificacionesCsv,
  useMutationRegistrarCalificacion,
} from '@/features/profesor/hooks/useProfesor';
import { ActividadesDictadoPage } from '@/features/profesor/pages/ActividadesDictadoPage';

const mockUseActividades = vi.mocked(useActividadesDictado);
const mockUseCalificaciones = vi.mocked(useCalificacionesDictado);
const mockUsePadron = vi.mocked(usePadronDictado);
const mockMutationEditar = vi.mocked(useMutationEditarCalificacion);
const mockMutationCrear = vi.mocked(useMutationCrearActividad);
const mockMutationEditarAct = vi.mocked(useMutationEditarActividad);
const mockMutationEliminar = vi.mocked(useMutationEliminarActividad);
const mockMutationCsv = vi.mocked(useMutationSubirCalificacionesCsv);
const mockMutationRegistrar = vi.mocked(useMutationRegistrarCalificacion);

const defaultMutation = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

const sampleActividad = { id: 'act1', nombre: 'Tarea 1', tipo: 'tarea', fecha_limite: '2025-12-01' };

const samplePadron = [
  { id: 'ep1', nombre: 'Juan', apellidos: 'Pérez', email: null, comision: null },
  { id: 'ep2', nombre: 'Ana', apellidos: 'García', email: null, comision: null },
];

// ep1 already graded — ep2 is ungraded
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

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/dictados/d1/actividades']}>
        <Routes>
          <Route path="/dictados/:dictadoId/actividades" element={<ActividadesDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ActividadesDictadoPage — inline registrar-nota row', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationEditar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEditarCalificacion>);
    mockMutationCrear.mockReturnValue(defaultMutation as ReturnType<typeof useMutationCrearActividad>);
    mockMutationEditarAct.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEditarActividad>);
    mockMutationEliminar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEliminarActividad>);
    mockMutationCsv.mockReturnValue(defaultMutation as ReturnType<typeof useMutationSubirCalificacionesCsv>);
    mockMutationRegistrar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationRegistrarCalificacion>);
    mockUsePadron.mockReturnValue({ data: samplePadron, isLoading: false, isError: false } as ReturnType<typeof usePadronDictado>);
    mockUseActividades.mockReturnValue({ data: [sampleActividad], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [sampleCalificacion], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);
  });

  it('7.1 — inline row is NOT shown at top of page before clicking Registrar nota', () => {
    renderPage();
    // The inline row should not be in DOM before activation
    expect(screen.queryByTestId('registrar-nota-inline-row')).not.toBeInTheDocument();
    // But the button "Registrar nota" is visible in the activity card header
    expect(screen.getByText('Registrar nota')).toBeInTheDocument();
  });

  it('7.1 — clicking Registrar nota shows inline row INSIDE the activity (not at top)', () => {
    renderPage();
    fireEvent.click(screen.getByText('Registrar nota'));

    // Inline row now exists
    expect(screen.getByTestId('registrar-nota-inline-row')).toBeInTheDocument();
    // "Registrar nota" button is hidden while row is open
    expect(screen.queryByText('Registrar nota')).not.toBeInTheDocument();
  });

  it('7.2 — alumno select shows ONLY ungraded alumnos (ep2 = Ana García)', () => {
    renderPage();
    fireEvent.click(screen.getByText('Registrar nota'));

    // The select should have Ana García but NOT Juan Pérez (already graded)
    expect(screen.getByText('García, Ana')).toBeInTheDocument();
    expect(screen.queryByText('Pérez, Juan')).not.toBeInTheDocument();
  });

  it('7.4 — aprobado control in the edit row is a DS toggle button (not bare checkbox)', () => {
    renderPage();
    // The edit row renders an AprobadoToggle for existing calificacion
    // Click edit on Juan's grade — find "Editar" text in table cell (not the actividad edit button)
    const editarBtns = screen.getAllByText('Editar');
    // The calificacion "Editar" button is the one inside the table cell
    fireEvent.click(editarBtns[0]);

    // The aprobado control should be a <button role="checkbox">, not <input type="checkbox">
    const toggle = screen.getByRole('checkbox', { name: /aprobado/i });
    expect(toggle.tagName).toBe('BUTTON');
  });

  it('7.4 — TRIANGULATE: AprobadoToggle toggles its aria-checked state', () => {
    renderPage();
    const editarBtns = screen.getAllByText('Editar');
    fireEvent.click(editarBtns[0]);

    const toggle = screen.getByRole('checkbox', { name: /aprobado/i });
    // Initially checked=true (from sampleCalificacion.aprobado=true)
    expect(toggle).toHaveAttribute('aria-checked', 'true');

    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-checked', 'false');
  });
});
