import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '@/features/academico/components/StatusBadge';

describe('StatusBadge', () => {
  it('renders Pendiente status correctly', () => {
    render(<StatusBadge status="Pendiente" />);
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('renders Enviando status with pulse animation', () => {
    const { container } = render(<StatusBadge status="Enviando" />);
    expect(screen.getByText('Enviando')).toBeInTheDocument();
    const pulseEl = container.querySelector('.animate-pulse');
    expect(pulseEl).toBeInTheDocument();
  });

  it('renders OK status correctly', () => {
    render(<StatusBadge status="OK" />);
    expect(screen.getByText('Enviado')).toBeInTheDocument();
  });

  it('renders Fallido status correctly', () => {
    render(<StatusBadge status="Fallido" />);
    expect(screen.getByText('Fallido')).toBeInTheDocument();
  });

  it('renders Cancelado status correctly', () => {
    render(<StatusBadge status="Cancelado" />);
    expect(screen.getByText('Cancelado')).toBeInTheDocument();
  });
});
