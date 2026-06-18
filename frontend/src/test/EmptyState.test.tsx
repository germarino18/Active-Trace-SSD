import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { EmptyState } from '@/features/academico/components/EmptyState';

describe('EmptyState', () => {
  it('renders the message correctly', () => {
    render(<EmptyState message="No hay datos disponibles" />);
    expect(screen.getByText('No hay datos disponibles')).toBeInTheDocument();
  });

  it('renders with default icon', () => {
    const { container } = render(<EmptyState message="Test" />);
    expect(container.querySelector('.material-symbols-outlined')).toBeInTheDocument();
  });

  it('renders with custom icon', () => {
    const { container } = render(<EmptyState message="Test" icon="warning" />);
    expect(container.querySelector('.material-symbols-outlined')).toBeInTheDocument();
  });
});
