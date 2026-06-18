import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { AvisoCrearPage } from '@/features/coordinacion/pages/AvisoCrearPage';

const mockMutateAsync = vi.fn();
const mockCrearAvisoState = vi.hoisted(() => ({ isError: false }));

vi.mock('@/features/coordinacion/hooks/useAvisos', () => ({
  useCrearAviso: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
    get isError() { return mockCrearAvisoState.isError; },
  }),
  useAvisos: () => ({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
  useAviso: () => ({
    data: null,
    isLoading: false,
  }),
  useActualizarAviso: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useEliminarAviso: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useConfirmarAck: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <AvisoCrearPage />
    </TestWrapper>,
  );
}

describe('AvisoCrearPage', () => {
  it('renders page title', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: 'Crear Aviso' })).toBeInTheDocument();
  });

  it('renders all form fields', () => {
    renderPage();
    expect(screen.getByPlaceholderText('Ej: Recordatorio de carga de actas')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Contenido del aviso...')).toBeInTheDocument();
    expect(screen.getAllByRole('combobox').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole('spinbutton')).toBeInTheDocument();
  });

  it('renders scope selector', () => {
    renderPage();
    const scopeSelect = screen.getAllByRole('combobox')[0];
    expect(scopeSelect).toBeInTheDocument();
  });

  it('fills form and submits successfully', async () => {
    const user = userEvent.setup();
    mockMutateAsync.mockResolvedValueOnce({ id: 'new-1' });

    const { container } = renderPage();

    await user.type(
      screen.getByPlaceholderText('Ej: Recordatorio de carga de actas'),
      'Test Aviso',
    );
    await user.type(
      screen.getByPlaceholderText('Contenido del aviso...'),
      'Test mensaje del aviso',
    );

    const dateInputs = container.querySelectorAll<HTMLInputElement>('input[type="date"]');
    await user.type(dateInputs[0]!, '2024-01-01');
    await user.type(dateInputs[1]!, '2024-01-31');

    await user.click(screen.getByRole('button', { name: 'Crear Aviso' }));

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalled();
    });

    const callData = mockMutateAsync.mock.calls[0]![0];
    expect(callData.titulo).toBe('Test Aviso');
    expect(callData.mensaje).toBe('Test mensaje del aviso');
    expect(callData.scope).toBe('Global');
  });

  it('shows error state when mutation fails', async () => {
    mockCrearAvisoState.isError = true;
    renderPage();

    expect(
      screen.getByText('Error al crear el aviso. Intentá de nuevo.'),
    ).toBeInTheDocument();
  });
});
