import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TablaStatusComunicacion } from '@/features/academico/components/TablaStatusComunicacion';
import type { MensajeStatusEntry } from '@/features/academico/types';

const mockMensajes: MensajeStatusEntry[] = [
  {
    alumno: { id: '1', legajo: '123', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', comision: 'A' },
    status: 'OK',
    updated_at: '2026-06-17T23:59:00Z',
  },
  {
    alumno: { id: '2', legajo: '456', nombre: 'Maria', apellido: 'Lopez', email: 'maria@test.com', comision: 'B' },
    status: 'Enviando',
    updated_at: '2026-06-17T23:59:00Z',
  },
  {
    alumno: { id: '3', legajo: '789', nombre: 'Carlos', apellido: 'Garcia', email: 'carlos@test.com', comision: 'A' },
    status: 'Fallido',
    error: 'Error de conexión SMTP',
    updated_at: '2026-06-17T23:59:00Z',
  },
];

describe('TablaStatusComunicacion', () => {
  it('renders all messages with correct status badges', () => {
    render(<TablaStatusComunicacion mensajes={mockMensajes} />);

    expect(screen.getByText(/Perez, Juan/)).toBeInTheDocument();
    expect(screen.getByText(/Lopez, Maria/)).toBeInTheDocument();
    expect(screen.getByText(/Garcia, Carlos/)).toBeInTheDocument();
    expect(screen.getByText('Enviado')).toBeInTheDocument();
    expect(screen.getByText('Enviando')).toBeInTheDocument();
    expect(screen.getByText('Fallido')).toBeInTheDocument();
  });

  it('shows empty state when no messages', () => {
    render(<TablaStatusComunicacion mensajes={[]} />);
    expect(screen.getByText('No hay comunicaciones enviadas')).toBeInTheDocument();
  });

  it('shows terminal state indicator when complete', () => {
    render(<TablaStatusComunicacion mensajes={mockMensajes} isTerminal={true} />);
    expect(screen.getByText('Todos los envíos finalizados')).toBeInTheDocument();
  });

  it('shows updating indicator when not terminal', () => {
    render(<TablaStatusComunicacion mensajes={mockMensajes} isTerminal={false} />);
    expect(screen.getByText('Actualizando...')).toBeInTheDocument();
  });

  it('highlights failed rows', () => {
    const { container } = render(<TablaStatusComunicacion mensajes={mockMensajes} />);
    const rows = container.querySelectorAll('tbody tr');
    expect(rows[2]!.className).toContain('bg-error/5');
  });

  it('shows error tooltip on failed messages', () => {
    render(<TablaStatusComunicacion mensajes={mockMensajes} />);
    const failedRow = screen.getByText(/Garcia, Carlos/).closest('tr');
    expect(failedRow).toHaveAttribute('title', 'Error de conexión SMTP');
  });
});
