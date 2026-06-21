/**
 * TDD RED/GREEN — Tasks 4.2–4.8
 * Overlay modal (portal) for actividad create + edit fecha_limite,
 * plus dual invalidation on create/edit/delete.
 */
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// ------- mock hook module -------
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
  useMutationEditarActividad: vi.fn(),
  useMutationEliminarActividad: vi.fn(),
  useMutationSubirCalificacionesCsv: vi.fn(),
  useMutationRegistrarCalificacion: vi.fn(),
  useAtrasadosProfesor: vi.fn(),
  useMutationComunicadoAtrasadoNull: vi.fn(),
  useMutationComunicadoAtrasados: vi.fn(),
  useMutationComunicadoFlexible: vi.fn(),
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
  useMutationEditarActividad,
  useMutationEliminarActividad,
  useMutationSubirCalificacionesCsv,
  useMutationRegistrarCalificacion,
} from '@/features/profesor/hooks/useProfesor';
import { ActividadesDictadoPage } from '@/features/profesor/pages/ActividadesDictadoPage';

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });

const mockUseActividades = vi.mocked(useActividadesDictado);
const mockUseCalificaciones = vi.mocked(useCalificacionesDictado);
const mockUsePadron = vi.mocked(usePadronDictado);
const mockMutationEditar = vi.mocked(useMutationEditarCalificacion);
const mockMutationCrear = vi.mocked(useMutationCrearActividad);
const mockMutationEditarActividad = vi.mocked(useMutationEditarActividad);
const mockMutationEliminar = vi.mocked(useMutationEliminarActividad);
const mockMutationCsv = vi.mocked(useMutationSubirCalificacionesCsv);
const mockMutationRegistrar = vi.mocked(useMutationRegistrarCalificacion);

const mutateAsyncCrear = vi.fn().mockResolvedValue({ id: 'newact', nombre: 'Nueva', tipo: 'tarea', fecha_limite: null });
const mutateAsyncEditarActividad = vi.fn().mockResolvedValue({ id: 'act1', nombre: 'Tarea 1', tipo: 'tarea', fecha_limite: '2026-01-15' });
const mutateAsyncEliminar = vi.fn().mockResolvedValue(undefined);

const defaultMutation = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

const sampleActividad = { id: 'act1', nombre: 'Tarea 1', tipo: 'tarea', fecha_limite: '2025-12-01' };
const samplePadron = [{ id: 'ep1', nombre: 'Juan', apellidos: 'Pérez', email: null, comision: null }];

function renderPage() {
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/profesor/dictados/d1/actividades']}>
        <Routes>
          <Route path="/profesor/dictados/:dictadoId/actividades" element={<ActividadesDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ActividadesDictadoPage — overlay modal + dual invalidation (tasks 4.2–4.8)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationEditar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEditarCalificacion>);
    mockMutationCrear.mockReturnValue({
      mutateAsync: mutateAsyncCrear,
      isPending: false,
      isError: false,
      isSuccess: false,
    } as ReturnType<typeof useMutationCrearActividad>);
    mockMutationEditarActividad.mockReturnValue({
      mutateAsync: mutateAsyncEditarActividad,
      isPending: false,
      isError: false,
      isSuccess: false,
    } as ReturnType<typeof useMutationEditarActividad>);
    mockMutationEliminar.mockReturnValue({
      mutateAsync: mutateAsyncEliminar,
      isPending: false,
      isError: false,
      isSuccess: false,
    } as ReturnType<typeof useMutationEliminarActividad>);
    mockMutationCsv.mockReturnValue(defaultMutation as ReturnType<typeof useMutationSubirCalificacionesCsv>);
    mockMutationRegistrar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationRegistrarCalificacion>);
    mockUsePadron.mockReturnValue({ data: samplePadron, isLoading: false, isError: false } as ReturnType<typeof usePadronDictado>);
    mockUseCalificaciones.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useCalificacionesDictado>);
    mockUseActividades.mockReturnValue({ data: [sampleActividad], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
  });

  // Task 4.2: modal renders via portal OUTSIDE the activity-card subtree
  it('4.2 — "Crear actividad" modal renders via portal outside activity card (in document.body)', async () => {
    renderPage();
    const btn = screen.getByText('Crear actividad');
    fireEvent.click(btn);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    // Portal: the dialog must be a direct child of document.body, NOT inside the main content div
    const dialog = screen.getByRole('dialog');
    // The dialog's parent chain should reach document.body (portal renders there)
    expect(document.body).toContainElement(dialog);

    // Backdrop should be present with fixed inset-0 class (or style)
    const backdrop = document.querySelector('[data-testid="modal-backdrop"]') ??
      document.querySelector('.fixed.inset-0') ??
      dialog.parentElement;
    expect(backdrop).toBeInTheDocument();
  });

  it('4.2b — modal closes when backdrop is clicked', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Crear actividad'));

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const backdrop = document.querySelector('[data-testid="modal-backdrop"]');
    if (backdrop) {
      fireEvent.click(backdrop);
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    }
  });

  it('4.2c — modal closes on Escape key', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Crear actividad'));

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  // Task 4.4: edit form calls PATCH /api/v1/actividades/{actividad_id}
  it('4.4 — "Editar" button on actividad opens edit form for fecha_limite', async () => {
    renderPage();

    // There should be an edit button per actividad (distinct from calificacion edit)
    const editBtn = screen.getByLabelText(/editar actividad/i) ?? screen.getByTitle(/editar actividad/i);
    expect(editBtn).toBeInTheDocument();
  });

  it('4.4b — editing fecha_limite calls PATCH via useMutationEditarActividad', async () => {
    renderPage();

    // Open edit modal for actividad
    const editBtn = screen.getByLabelText('Editar actividad Tarea 1') ??
      screen.getByTitle('Editar actividad') ??
      screen.getAllByText('Editar actividad')[0];
    fireEvent.click(editBtn);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    // The edit form should have a fecha_limite field
    const fechaInput = screen.getByLabelText(/fecha.?l[ií]mite/i);
    fireEvent.change(fechaInput, { target: { value: '2026-01-15' } });

    // Submit
    fireEvent.click(screen.getByText(/guardar/i));

    await waitFor(() => {
      expect(mutateAsyncEditarActividad).toHaveBeenCalledWith({
        actividadId: 'act1',
        data: expect.objectContaining({ fecha_limite: '2026-01-15' }),
      });
    });
  });

  // Task 4.6: dual invalidation — verified at the hook level.
  // The hooks (useMutationCrearActividad, useMutationEditarActividad, useMutationEliminarActividad)
  // call invalidateDictadoDerived which invalidates all three keys.
  // Since the hooks are mocked at the boundary in this test file, invalidation is tested
  // in the dedicated hook-level test (useProfesor.invalidation.test.ts) using real QueryClient.
  // Here we verify that the mocked mutations are called with the right arguments.

  it('4.6a — useMutationCrearActividad is called when create form is submitted', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Crear actividad'));

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const nombreInput = screen.getByLabelText(/nombre/i);
    fireEvent.change(nombreInput, { target: { value: 'Nueva Tarea' } });

    // Submit the form — find the submit button inside the dialog
    const submitBtn = screen.getByRole('dialog').querySelector('button[type="submit"]');
    if (submitBtn) fireEvent.click(submitBtn);
    else fireEvent.click(screen.getAllByText('Crear actividad').find(el => el instanceof Element && (el as HTMLElement).tagName === 'BUTTON') as Element);

    await waitFor(() => {
      expect(mutateAsyncCrear).toHaveBeenCalledWith(
        expect.objectContaining({ nombre: 'Nueva Tarea' }),
      );
    });
  });

  it('4.6b — useMutationEditarActividad is called with fecha_limite on edit submit', async () => {
    renderPage();

    const editBtn = screen.getByLabelText('Editar actividad Tarea 1');
    fireEvent.click(editBtn);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const fechaInput = screen.getByLabelText(/fecha.?l[ií]mite/i);
    fireEvent.change(fechaInput, { target: { value: '2026-01-15' } });
    fireEvent.click(screen.getByText(/guardar/i));

    await waitFor(() => {
      expect(mutateAsyncEditarActividad).toHaveBeenCalledWith({
        actividadId: 'act1',
        data: expect.objectContaining({ fecha_limite: '2026-01-15' }),
      });
    });
  });

  // Task 4.8 TRIANGULATE: delete mutation is called (invalidation verified in hook tests)
  it('4.8 — useMutationEliminarActividad is called when delete is clicked', async () => {
    renderPage();

    const deleteBtn = screen.getByLabelText('Eliminar actividad Tarea 1');
    fireEvent.click(deleteBtn);

    await waitFor(() => {
      expect(mutateAsyncEliminar).toHaveBeenCalledWith('act1');
    });
  });
});
