/**
 * 5.1 RED → GREEN → TRIANGULATE: AtrasadosGeneralPage comunicado buttons.
 *
 * TDD cycle:
 *   RED:   per-row "Enviar comunicado" button; top-level "Enviar a todos" button
 *   GREEN: buttons added to AtrasadosGeneralPage / ComunicadoFlexibleForm
 *   TRIANGULATE: individual vs. general, filter-respecting general send
 */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AtrasadosGeneralPage } from '@/features/academico/pages/AtrasadosGeneralPage';

// ── Mocks ────────────────────────────────────────────────────────────────────

const mockMutateAsync = vi.fn().mockResolvedValue({ total: 1, lote_id: 'l1', lotes: ['l1'] });
const mockMutate = vi.fn();

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useAtrasadosGeneralProfesor: () => ({
    data: [
      {
        entrada_padron_id: 'ep-1',
        nombre: 'Juan',
        apellido: 'Pérez',
        dictado_id: 'd-1',
        materia_nombre: 'Matemática',
        actividades_sin_entrega: ['TP1'],
      },
      {
        entrada_padron_id: 'ep-2',
        nombre: 'María',
        apellido: 'García',
        dictado_id: 'd-2',
        materia_nombre: 'Física',
        actividades_sin_entrega: ['Parcial'],
      },
    ],
    isLoading: false,
  }),
  useMutationComunicadoFlexible: () => ({
    mutateAsync: mockMutateAsync,
    mutate: mockMutate,
    isPending: false,
    isSuccess: false,
    isError: false,
    error: null,
  }),
}));

// ── Helper ───────────────────────────────────────────────────────────────────

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderPage() {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter>
        <AtrasadosGeneralPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

// ── §5.1 RED: per-row "Enviar comunicado" button ─────────────────────────────

describe('AtrasadosGeneralPage — comunicado buttons', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('5.1 renders a per-row comunicado button for each grouped alumno', () => {
    renderPage();
    // Two grouped rows (one per alumno, different entrada_padron_id)
    const perRowBtns = screen.getAllByRole('button', { name: /comunicado/i });
    // At minimum, each row should have an "Enviar comunicado" button.
    // The "Enviar a todos" top-level may also be present.
    expect(perRowBtns.length).toBeGreaterThanOrEqual(2);
  });

  it('5.3 renders a top-level "Enviar a todos" button', () => {
    renderPage();
    expect(screen.getByRole('button', { name: /enviar a todos/i })).toBeInTheDocument();
  });

  it('5.2 clicking a per-row button opens a form for that alumno', async () => {
    const user = userEvent.setup();
    renderPage();

    // Click the first row's "Enviar comunicado" button
    const rowBtns = screen.getAllByRole('button', { name: /comunicado individual/i });
    await user.click(rowBtns[0]);

    // Form should appear
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('5.4 form allows submission without an activity (actividad_id is optional)', async () => {
    const user = userEvent.setup();
    renderPage();

    // Open the first row's comunicado form
    const rowBtns = screen.getAllByRole('button', { name: /comunicado individual/i });
    await user.click(rowBtns[0]);

    // Fill in required fields
    const asuntoInput = screen.getByLabelText(/asunto/i);
    const cuerpoInput = screen.getByLabelText(/cuerpo/i);
    await user.type(asuntoInput, 'Hola {alumno_nombre}');
    await user.type(cuerpoInput, 'Tenés materias pendientes.');

    // Submit WITHOUT filling in the actividad field
    const submitBtn = screen.getByRole('button', { name: /enviar/i });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({
          destinatarios: expect.arrayContaining([
            expect.objectContaining({ entrada_padron_id: 'ep-1' }),
          ]),
        }),
      );
    });
  });

  it('5.5 shows success total after individual send', async () => {
    const user = userEvent.setup();
    mockMutateAsync.mockResolvedValueOnce({ total: 1, lote_id: 'l1', lotes: ['l1'] });
    renderPage();

    const rowBtns = screen.getAllByRole('button', { name: /comunicado individual/i });
    await user.click(rowBtns[0]);

    await user.type(screen.getByLabelText(/asunto/i), 'Test asunto');
    await user.type(screen.getByLabelText(/cuerpo/i), 'Test cuerpo');
    await user.click(screen.getByRole('button', { name: /enviar/i }));

    await waitFor(() => {
      expect(screen.getByText(/enviado.*1/i)).toBeInTheDocument();
    });
  });

  it('5.6 TRIANGULATE: individual send uses single-element destinatarios', async () => {
    const user = userEvent.setup();
    renderPage();

    const rowBtns = screen.getAllByRole('button', { name: /comunicado individual/i });
    await user.click(rowBtns[0]); // first alumno: ep-1

    await user.type(screen.getByLabelText(/asunto/i), 'Asunto individual');
    await user.type(screen.getByLabelText(/cuerpo/i), 'Cuerpo individual');
    await user.click(screen.getByRole('button', { name: /enviar/i }));

    await waitFor(() => {
      const callArgs = mockMutateAsync.mock.calls[0][0];
      expect(callArgs.destinatarios).toHaveLength(1);
      expect(callArgs.destinatarios[0].entrada_padron_id).toBe('ep-1');
    });
  });

  it('5.3 "Enviar a todos" sends all currently visible rows as destinatarios', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole('button', { name: /enviar a todos/i }));

    // Form opens for general send
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    await user.type(screen.getByLabelText(/asunto/i), 'Mensaje general');
    await user.type(screen.getByLabelText(/cuerpo/i), 'A todos los atrasados.');
    await user.click(screen.getByRole('button', { name: /enviar/i }));

    await waitFor(() => {
      const callArgs = mockMutateAsync.mock.calls[0][0];
      // Both rows are visible (no filter) → 2+ destinatarios
      expect(callArgs.destinatarios.length).toBeGreaterThanOrEqual(2);
    });
  });
});
