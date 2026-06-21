/**
 * MisTareasProfesorPage — group 7b tests
 *
 * TDD: Covers task 7b.2 (crear tarea modal) and 7b.3 (editar tarea modal via portal).
 * All modals must render via createPortal (not clipped by overflow-x-auto).
 * Mocks at the hook boundary per project convention.
 */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// ──────────────────────────────────────────────────────────────────────────────
// Mocks — must be declared BEFORE the dynamic import of the module under test
// ──────────────────────────────────────────────────────────────────────────────

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
  useMutationCrearTareaPropia: vi.fn(),
  useMutationEditarTareaPropia: vi.fn(),
  // Stubs for other hooks (used in full hook module)
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
  useMutationCrearTareaPropia,
  useMutationEditarTareaPropia,
} from '@/features/profesor/hooks/useProfesor';
import { MisTareasProfesorPage } from '@/features/profesor/pages/MisTareasProfesorPage';

// ──────────────────────────────────────────────────────────────────────────────
// Typed mocks
// ──────────────────────────────────────────────────────────────────────────────
const mockUseTareas = vi.mocked(useMisTareasProfesor);
const mockMutationCrear = vi.mocked(useMutationCrearTareaPropia);
const mockMutationEditar = vi.mocked(useMutationEditarTareaPropia);

const defaultMutation = {
  mutateAsync: vi.fn().mockResolvedValue({}),
  isPending: false,
  isError: false,
  isSuccess: false,
};

const sampleTareas = [
  {
    id: 't1',
    descripcion: 'Revisar TPs del grupo A',
    estado: 'PENDIENTE',
    materia_id: 'm1',
    asignado_a: 'u1',
    asignado_por: 'u2',
    created_at: '2026-06-01T10:00:00',
    updated_at: '2026-06-01T10:00:00',
  },
  {
    id: 't2',
    descripcion: 'Cargar notas del parcial',
    estado: 'EN_PROGRESO',
    materia_id: null,
    asignado_a: 'u1',
    asignado_por: 'u2',
    created_at: '2026-06-10T08:00:00',
    updated_at: '2026-06-10T08:00:00',
  },
];

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderPage() {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter>
        <MisTareasProfesorPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Setup
// ──────────────────────────────────────────────────────────────────────────────
beforeEach(() => {
  vi.clearAllMocks();
  mockMutationCrear.mockReturnValue(defaultMutation as ReturnType<typeof useMutationCrearTareaPropia>);
  mockMutationEditar.mockReturnValue(defaultMutation as ReturnType<typeof useMutationEditarTareaPropia>);
});

// ──────────────────────────────────────────────────────────────────────────────
// 7b.2 — "Crear tarea" button + portal modal
// ──────────────────────────────────────────────────────────────────────────────
describe('7b.2 — Crear tarea button + modal', () => {
  beforeEach(() => {
    mockUseTareas.mockReturnValue({
      data: sampleTareas,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);
  });

  it('shows a "Crear tarea" button in the page header', () => {
    renderPage();
    expect(screen.getByRole('button', { name: /crear tarea/i })).toBeInTheDocument();
  });

  it('opens the crear modal on button click', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/nueva tarea/i)).toBeInTheDocument();
  });

  it('crear modal has a descripcion field and submit button', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    expect(screen.getByLabelText(/descripci[oó]n/i)).toBeInTheDocument();
    // The submit button inside the dialog
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^guardar$/i })).toBeInTheDocument();
  });

  it('calls useMutationCrearTareaPropia.mutateAsync on submit with descripcion', async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockMutationCrear.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationCrearTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    await user.type(screen.getByLabelText(/descripci[oó]n/i), 'Nueva tarea de prueba');
    // Submit form — the modal's submit button is "Guardar"
    await user.click(screen.getByRole('button', { name: /^guardar$/i }));
    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({ descripcion: 'Nueva tarea de prueba' }),
      );
    });
  });

  it('modal closes after successful create', async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockMutationCrear.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationCrearTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    await user.type(screen.getByLabelText(/descripci[oó]n/i), 'Test');
    await user.click(screen.getByRole('button', { name: /^guardar$/i }));
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('modal closes on Escape key', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
});

// ──────────────────────────────────────────────────────────────────────────────
// 7b.3 — Edit tarea modal (replaces clipped dropdown)
// ──────────────────────────────────────────────────────────────────────────────
describe('7b.3 — Editar tarea modal (portal)', () => {
  beforeEach(() => {
    mockUseTareas.mockReturnValue({
      data: sampleTareas,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);
  });

  it('renders an edit button per tarea row', () => {
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    expect(editButtons.length).toBe(sampleTareas.length);
  });

  it('opens the editar modal when the edit button is clicked', async () => {
    const user = userEvent.setup();
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    await user.click(editButtons[0]);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('editar modal prefills with the tarea descripcion', async () => {
    const user = userEvent.setup();
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    await user.click(editButtons[0]);
    const descripcionField = screen.getByDisplayValue('Revisar TPs del grupo A');
    expect(descripcionField).toBeInTheDocument();
  });

  it('editar modal has a estado selector prefilled with current estado', async () => {
    const user = userEvent.setup();
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    await user.click(editButtons[0]);
    // There should be a select or combobox with PENDIENTE selected
    const estadoSelect = screen.getByDisplayValue(/pendiente/i);
    expect(estadoSelect).toBeInTheDocument();
  });

  it('calls useMutationEditarTareaPropia.mutateAsync on save', async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockMutationEditar.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationEditarTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    await user.click(editButtons[0]);
    // Change descripcion
    const descripcionField = screen.getByDisplayValue('Revisar TPs del grupo A');
    await user.clear(descripcionField);
    await user.type(descripcionField, 'Descripcion actualizada');
    // Submit
    await user.click(screen.getByRole('button', { name: /guardar/i }));
    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          tareaId: 't1',
          data: expect.objectContaining({ descripcion: 'Descripcion actualizada' }),
        }),
      );
    });
  });

  it('editar modal closes after save', async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockMutationEditar.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationEditarTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    await user.click(editButtons[0]);
    await user.click(screen.getByRole('button', { name: /guardar/i }));
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  it('no inline dropdown buttons exist in the table rows (overflow-safe)', () => {
    mockUseTareas.mockReturnValue({
      data: sampleTareas,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);
    renderPage();
    // The old dropdown showed ESTADO_OPTIONS as <button> elements inside the table.
    // In the new design, those never appear — only the EstadoBadge spans.
    // Verify there are no buttons with estado option text ("Pendiente", "Resuelta", etc.)
    // Only the two Editar buttons + one Crear tarea button = 3 buttons total.
    const allButtons = screen.getAllByRole('button');
    // Should be: 1 "Crear tarea" + 2 "Editar" = 3 total (no dropdown option buttons)
    expect(allButtons).toHaveLength(3);
  });
});

// ──────────────────────────────────────────────────────────────────────────────
// 7b.4 — TRIANGULATE: edge cases + validation
// ──────────────────────────────────────────────────────────────────────────────
describe('7b.4 — Triangulate: validation + edge cases', () => {
  beforeEach(() => {
    mockUseTareas.mockReturnValue({
      data: sampleTareas,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);
  });

  it('crear modal: shows validation error when descripcion is empty on submit', async () => {
    const mutateAsync = vi.fn();
    mockMutationCrear.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationCrearTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    // Submit without filling descripcion
    await user.click(screen.getByRole('button', { name: /^guardar$/i }));
    await waitFor(() => {
      expect(screen.getByText(/requerido/i)).toBeInTheDocument();
    });
    expect(mutateAsync).not.toHaveBeenCalled();
  });

  it('crear modal: includes materia_id: null when no materia selected', async () => {
    const mutateAsync = vi.fn().mockResolvedValue({});
    mockMutationCrear.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationCrearTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByRole('button', { name: /crear tarea/i }));
    await user.type(screen.getByLabelText(/descripci[oó]n/i), 'Tarea sin materia');
    await user.click(screen.getByRole('button', { name: /^guardar$/i }));
    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({ materia_id: null }),
      );
    });
  });

  it('editar modal: shows validation error when descripcion is cleared', async () => {
    const mutateAsync = vi.fn();
    mockMutationEditar.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationEditarTareaPropia>);

    const user = userEvent.setup();
    renderPage();
    const editButtons = screen.getAllByRole('button', { name: /editar|edit/i });
    await user.click(editButtons[0]);
    const descripcionField = screen.getByDisplayValue('Revisar TPs del grupo A');
    await user.clear(descripcionField);
    await user.click(screen.getByRole('button', { name: /guardar/i }));
    await waitFor(() => {
      expect(screen.getByText(/requerido/i)).toBeInTheDocument();
    });
    expect(mutateAsync).not.toHaveBeenCalled();
  });

  it('shows Mis Tareas header regardless of tareas array length', () => {
    mockUseTareas.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useMisTareasProfesor>);
    renderPage();
    expect(screen.getByText('Mis Tareas')).toBeInTheDocument();
    // "Crear tarea" button still present when empty
    expect(screen.getByRole('button', { name: /crear tarea/i })).toBeInTheDocument();
  });
});
