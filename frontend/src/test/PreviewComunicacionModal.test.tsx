import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { PreviewComunicacionModal } from '@/features/academico/components/PreviewComunicacionModal';
import type { ComunicacionDestinatario } from '@/features/academico/types';

const mockDestinatarios: ComunicacionDestinatario[] = [
  {
    alumno: { id: '1', legajo: '123', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', comision: 'A' },
    asunto: 'Notificación de atraso',
    cuerpo: 'Estimado Juan, tiene 3 actividades pendientes.',
  },
];

describe('PreviewComunicacionModal', () => {
  it('renders preview content when open', () => {
    render(
      <PreviewComunicacionModal
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        asunto="Comunicación de atraso"
        cuerpo="Estimado/a estudiante:"
        destinatarios={mockDestinatarios}
      />,
    );

    expect(screen.getByText('Vista Previa')).toBeInTheDocument();
    expect(screen.getByText('Comunicación de atraso')).toBeInTheDocument();
    expect(screen.getByText('Estimado/a estudiante:')).toBeInTheDocument();
    expect(screen.getByText(/Perez, Juan/)).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <PreviewComunicacionModal
        isOpen={false}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        asunto="Test"
        cuerpo="Test"
        destinatarios={[]}
      />,
    );

    expect(screen.queryByText('Vista Previa')).not.toBeInTheDocument();
  });

  it('calls onConfirm when confirm button is clicked', async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();

    render(
      <PreviewComunicacionModal
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={onConfirm}
        asunto="Test"
        cuerpo="Test"
        destinatarios={mockDestinatarios}
      />,
    );

    await user.click(screen.getByText('Confirmar envío'));
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it('disables buttons when sending', () => {
    render(
      <PreviewComunicacionModal
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        asunto="Test"
        cuerpo="Test"
        destinatarios={[]}
        isSending={true}
      />,
    );

    expect(screen.getByText('Enviando...')).toBeDisabled();
  });
});
