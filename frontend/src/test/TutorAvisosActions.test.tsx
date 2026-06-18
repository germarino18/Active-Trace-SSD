import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TutorAvisosActions } from '@/features/tutor/components/TutorAvisosActions';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockMutate = vi.fn();

vi.mock('@/features/coordinacion/hooks/useAvisos', () => ({
  useConfirmarAck: () => ({
    mutate: mockMutate,
    isPending: false,
    error: null,
  }),
}));

function renderComponent(requiereAck: boolean, userAcked: boolean) {
  return render(
    <QueryClientProvider client={queryClient}>
      <TutorAvisosActions avisoId="a1" requiereAck={requiereAck} userAcked={userAcked} />
    </QueryClientProvider>,
  );
}

describe('TutorAvisosActions', () => {
  beforeEach(() => {
    mockMutate.mockReset();
  });

  it('renders nothing when aviso does not require ack', () => {
    const { container } = renderComponent(false, false);
    expect(container.innerHTML).toBe('');
  });

  it('shows confirm button when aviso requires ack and not confirmed', () => {
    renderComponent(true, false);
    expect(screen.getByText('Confirmar')).toBeInTheDocument();
  });

  it('calls confirmarAck.mutate on button click', async () => {
    const user = userEvent.setup();
    renderComponent(true, false);
    await user.click(screen.getByText('Confirmar'));
    expect(mockMutate).toHaveBeenCalledWith('a1');
  });

  it('shows confirmed badge when already acked', () => {
    renderComponent(true, true);
    expect(screen.getByText('✓ Confirmado')).toBeInTheDocument();
    expect(screen.queryByText('Confirmar')).not.toBeInTheDocument();
  });
});
