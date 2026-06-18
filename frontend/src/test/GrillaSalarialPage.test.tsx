import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { GrillaSalarialPage } from '@/features/finanzas/pages/GrillaSalarialPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['FINANZAS'],
        permissions: ['FINANZAS', 'liquidaciones:*', 'facturas:*', 'finanzas:grilla:gestionar'],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['FINANZAS', 'ADMIN'].includes(p)),
  }),
}));

const mockUseSalariosBase = vi.fn();
const mockUsePlus = vi.fn();

vi.mock('@/features/finanzas/hooks/useGrillaSalarial', () => ({
  useSalariosBase: () => mockUseSalariosBase(),
  usePlus: () => mockUsePlus(),
  useCrearSalarioBase: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEditarSalarioBase: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCrearPlus: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEditarPlus: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

const mockSalariosBase = [
  {
    id: 'sb1',
    rol: 'PROFESOR' as const,
    importe: 500000,
    vigencia_desde: '2025-01-01',
  },
  {
    id: 'sb2',
    rol: 'TUTOR' as const,
    importe: 300000,
    vigencia_desde: '2025-01-01',
    vigencia_hasta: '2025-06-30',
  },
];

const mockPlus = [
  {
    id: 'p1',
    clave: 'ANTIGUEDAD',
    rol: 'PROFESOR' as const,
    descripcion: 'Antigüedad',
    importe: 50000,
    vigencia_desde: '2025-01-01',
  },
  {
    id: 'p2',
    clave: 'TITULO',
    rol: 'TUTOR' as const,
    descripcion: 'Título',
    importe: 30000,
    vigencia_desde: '2025-01-01',
    vigencia_hasta: '2025-06-30',
  },
];

function renderPage() {
  return render(
    <TestWrapper>
      <GrillaSalarialPage />
    </TestWrapper>,
  );
}

describe('GrillaSalarialPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseSalariosBase.mockReturnValue({ data: mockSalariosBase, isLoading: false });
    mockUsePlus.mockReturnValue({ data: mockPlus, isLoading: false });
  });

  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Grilla Salarial')).toBeInTheDocument();
    expect(screen.getByText('Gestioná los salarios base y plus por rol docente.')).toBeInTheDocument();
  });

  it('renders tabs', () => {
    renderPage();
    expect(screen.getByRole('tab', { name: 'Salario Base' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Plus' })).toBeInTheDocument();
  });

  it('renders SalarioBaseTable with data by default', () => {
    renderPage();
    expect(screen.getByText('Profesor')).toBeInTheDocument();
    expect(screen.getByText('Tutor')).toBeInTheDocument();
  });

  it('renders Nuevo salario base button when canEdit is true', () => {
    renderPage();
    expect(screen.getByText('Nuevo salario base')).toBeInTheDocument();
  });

  it('renders loading state for salarios base', () => {
    mockUseSalariosBase.mockReturnValue({ data: undefined, isLoading: true });

    renderPage();
    expect(screen.getByText('Grilla Salarial')).toBeInTheDocument();
    expect(screen.queryByText('Profesor')).not.toBeInTheDocument();
  });

  it('renders empty state when no salarios base', () => {
    mockUseSalariosBase.mockReturnValue({ data: [], isLoading: false });

    renderPage();
    expect(screen.getByText('No hay salarios base configurados')).toBeInTheDocument();
  });
});
