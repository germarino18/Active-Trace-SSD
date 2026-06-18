import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TablaAtrasados } from '@/features/academico/components/TablaAtrasados';
import type { AtrasadoEntry } from '@/features/academico/types';

const mockData: AtrasadoEntry[] = [
  {
    alumno: { id: '1', legajo: '123', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', comision: 'A' },
    actividades_pendientes: 3,
    nota_actual: 4.5,
    porcentaje: 45,
    estado: 'atrasado',
  },
  {
    alumno: { id: '2', legajo: '456', nombre: 'Maria', apellido: 'Lopez', email: 'maria@test.com', comision: 'B' },
    actividades_pendientes: 0,
    nota_actual: 8.0,
    porcentaje: 80,
    estado: 'al_dia',
  },
];

function renderTable(data?: AtrasadoEntry[]) {
  return render(<TablaAtrasados data={data} />);
}

describe('TablaAtrasados', () => {
  it('renders overdue students with correct data', () => {
    renderTable(mockData);
    expect(screen.getByText('Perez, Juan')).toBeInTheDocument();
    expect(screen.getByText('Lopez, Maria')).toBeInTheDocument();
    expect(screen.getByText('juan@test.com')).toBeInTheDocument();
    expect(screen.getByText('maria@test.com')).toBeInTheDocument();
  });

  it('shows "Atrasado" status badge for at-risk students', () => {
    renderTable(mockData);
    expect(screen.getByText('Atrasado')).toBeInTheDocument();
    expect(screen.getByText('Al día')).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    renderTable([]);
    expect(screen.getByText('No hay alumnos atrasados en esta materia')).toBeInTheDocument();
  });

  it('highlights atrasado rows', () => {
    const { container } = renderTable(mockData);
    const rows = container.querySelectorAll('tbody tr');
    expect(rows[0]!.className).toContain('bg-error/5');
    expect(rows[1]!.className).not.toContain('bg-error/5');
  });
});
