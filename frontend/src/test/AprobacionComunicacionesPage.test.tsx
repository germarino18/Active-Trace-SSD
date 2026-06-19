import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

let mockQueryData: unknown = null;
let mockIsLoading = false;
let mockIsError = false;
let mockMutationIsPending = false;
const mockMutateAsync = vi.fn();
const queryClientSpy = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQueryClient: () => ({ invalidateQueries: queryClientSpy }),
    useQuery: () => ({
      data: mockQueryData,
      isLoading: mockIsLoading,
      isError: mockIsError,
    }),
    useMutation: () => ({
      mutateAsync: mockMutateAsync,
      isPending: mockMutationIsPending,
    }),
  };
});

import { AprobacionComunicacionesPage } from '@/features/coordinacion/pages/AprobacionComunicacionesPage';

const loteBase = {
  lote_id: 'l1',
  docente_id: 'd1',
  docente_nombre: 'Prof. García',
  asunto: 'Recordatorio de actividades pendientes',
  cuerpo: 'Estimado alumno, tenés actividades pendientes.',
  total_destinatarios: 15,
  created_at: '2026-01-15T10:00:00Z',
  destinatarios: [
    { alumno_id: 'a1', nombre: 'Ana', apellido: 'López', email: 'ana@test.com', estado: 'Pendiente' as const },
  ],
};

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AprobacionComunicacionesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AprobacionComunicacionesPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockIsError = false;
    mockMutationIsPending = false;
    mockMutateAsync.mockReset();
    queryClientSpy.mockReset();
  });

  it('shows loading state while fetching', () => {
    mockIsLoading = true;
    renderPage();
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('shows empty state when no lotes pendientes', () => {
    mockQueryData = { items: [], total: 0 };
    renderPage();
    expect(screen.getByText('No hay comunicaciones pendientes de aprobación')).toBeInTheDocument();
  });

  it('renders lote table with remitente, asunto, destinatarios and date', () => {
    mockQueryData = { items: [loteBase], total: 1 };
    renderPage();

    expect(screen.getByText('Prof. García')).toBeInTheDocument();
    expect(screen.getByText('Recordatorio de actividades pendientes')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('Aprobar Comunicaciones')).toBeInTheDocument();
  });

  it('opens PreviewComunicacionModal when "Ver preview" is clicked', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    renderPage();

    await user.click(screen.getByText('Ver preview'));
    expect(screen.getByText('Vista Previa')).toBeInTheDocument();
    expect(screen.getAllByText('Recordatorio de actividades pendientes').length).toBeGreaterThanOrEqual(1);
  });

  it('closes preview modal without action when close button is clicked', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    renderPage();

    await user.click(screen.getByText('Ver preview'));
    expect(screen.getByText('Vista Previa')).toBeInTheDocument();

    await user.click(screen.getByText('close'));
    expect(screen.queryByText('Vista Previa')).not.toBeInTheDocument();
    expect(mockMutateAsync).not.toHaveBeenCalled();
  });

  it('shows confirm dialog when "Aprobar" is clicked', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    renderPage();

    await user.click(screen.getByText('Aprobar'));
    expect(screen.getByText('Aprobar lote de comunicaciones')).toBeInTheDocument();
    expect(screen.getByText(/15 destinatario/)).toBeInTheDocument();
  });

  it('calls aprobarLote mutation when confirm dialog is confirmed', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    mockMutateAsync.mockResolvedValue(undefined);
    renderPage();

    await user.click(screen.getByText('Aprobar'));
    const confirmButtons = screen.getAllByText('Aprobar');
    await user.click(confirmButtons[confirmButtons.length - 1]);

    expect(mockMutateAsync).toHaveBeenCalledWith('l1');
  });

  it('shows confirm dialog when "Rechazar" is clicked', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    renderPage();

    await user.click(screen.getByText('Rechazar'));
    expect(screen.getByText('Rechazar lote de comunicaciones')).toBeInTheDocument();
    expect(screen.getByText(/irreversible/)).toBeInTheDocument();
  });

  it('calls cancelarLote mutation when reject confirm dialog is confirmed', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    mockMutateAsync.mockResolvedValue(undefined);
    renderPage();

    await user.click(screen.getByText('Rechazar'));
    await user.click(screen.getByRole('button', { name: 'Rechazar' }));

    expect(mockMutateAsync).toHaveBeenCalledWith('l1');
  });

  it('shows success feedback after approving a lote', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    mockMutateAsync.mockResolvedValue(undefined);
    renderPage();

    await user.click(screen.getByText('Aprobar'));
    const confirmButtons = screen.getAllByText('Aprobar');
    await user.click(confirmButtons[confirmButtons.length - 1]);

    expect(await screen.findByText(/lote aprobado/i)).toBeInTheDocument();
  });

  it('shows error feedback when approving a lote fails', async () => {
    const user = userEvent.setup();
    mockQueryData = { items: [loteBase], total: 1 };
    mockMutateAsync.mockRejectedValue(new Error('Network error'));
    renderPage();

    await user.click(screen.getByText('Aprobar'));
    const confirmButtons = screen.getAllByText('Aprobar');
    await user.click(confirmButtons[confirmButtons.length - 1]);

    expect(await screen.findByText(/Error al aprobar/i)).toBeInTheDocument();
  });

  it('shows error state when query fails', () => {
    mockIsError = true;
    renderPage();
    expect(screen.getByText('Error al cargar los lotes pendientes')).toBeInTheDocument();
  });
});
