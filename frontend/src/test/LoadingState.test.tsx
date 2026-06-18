import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { LoadingState } from '@/features/academico/components/LoadingState';

describe('LoadingState', () => {
  it('renders skeleton rows', () => {
    const { container } = render(<LoadingState rows={3} cols={4} />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders correct number of rows', () => {
    const { container } = render(<LoadingState rows={5} cols={3} />);
    const rows = container.querySelectorAll('tbody tr');
    expect(rows.length).toBe(5);
  });

  it('renders correct number of columns', () => {
    const { container } = render(<LoadingState rows={2} cols={6} />);
    const headerCells = container.querySelectorAll('thead th');
    expect(headerCells.length).toBe(6);
  });
});
