import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TestWrapper } from './TestWrapper';
import type { ProfileResponse } from '@/features/perfil/types';

const mockUseProfileQuery = vi.fn();
const mockUseProfileMutation = vi.fn();

vi.mock('@/features/perfil/hooks/useProfile', () => ({
  useProfileQuery: () => mockUseProfileQuery(),
  useProfileMutation: () => mockUseProfileMutation(),
}));

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        nombre: 'Juan',
        apellido: 'García',
        email: 'juan@test.com',
        roles: ['PROFESOR'],
        tenant_id: 'tenant-1',
      },
    },
  }),
}));

import { ProfilePage } from '@/pages/ProfilePage';

const mockProfile: ProfileResponse = {
  id: 'uuid-1',
  tenant_id: 'tenant-1',
  nombre: 'Juan',
  apellidos: 'García',
  email: 'juan@test.com',
  cuil: '20-12345678-9',
  dni: '12345678',
  cbu: '1234567890123456789012',
  alias_cbu: 'juan.garcia',
  banco: 'Nación',
  regional: 'CABA',
  legajo: null,
  legajo_profesional: 'LP-001',
  facturador: false,
  estado: 'Activo',
};

function renderProfilePage() {
  return render(
    <TestWrapper>
      <ProfilePage />
    </TestWrapper>,
  );
}

describe('ProfilePage', () => {
  beforeEach(() => {
    mockUseProfileQuery.mockReset();
    mockUseProfileMutation.mockReset();
    mockUseProfileMutation.mockReturnValue({ mutateAsync: vi.fn(), isPending: false });
  });

  it('renders loading state while fetching', () => {
    mockUseProfileQuery.mockReturnValue({ isLoading: true, isError: false, data: undefined, refetch: vi.fn() });
    renderProfilePage();
    expect(screen.getByText(/cargando información/i)).toBeInTheDocument();
  });

  it('renders error state with retry button when fetch fails', () => {
    mockUseProfileQuery.mockReturnValue({ isLoading: false, isError: true, data: undefined, refetch: vi.fn() });
    renderProfilePage();
    expect(screen.getByText(/no se pudo cargar el perfil/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
  });

  it('renders CUIL as read-only — cannot be edited', async () => {
    mockUseProfileQuery.mockReturnValue({ isLoading: false, isError: false, data: mockProfile, refetch: vi.fn() });
    renderProfilePage();

    const cuilInputs = screen.getAllByDisplayValue('20-12345678-9');
    cuilInputs.forEach((input) => {
      expect(input).toHaveAttribute('readonly');
    });
  });

  it('renders email as read-only', async () => {
    mockUseProfileQuery.mockReturnValue({ isLoading: false, isError: false, data: mockProfile, refetch: vi.fn() });
    renderProfilePage();

    const emailInput = screen.getByDisplayValue('juan@test.com');
    expect(emailInput).toHaveAttribute('readonly');
  });

  it('editing personal section does not affect banking section edit state', async () => {
    mockUseProfileQuery.mockReturnValue({ isLoading: false, isError: false, data: mockProfile, refetch: vi.fn() });
    const user = userEvent.setup();
    renderProfilePage();

    const editButtons = screen.getAllByRole('button', { name: /editar/i });
    await user.click(editButtons[0]);

    const cancelButtons = screen.getAllByRole('button', { name: /cancelar/i });
    expect(cancelButtons).toHaveLength(1);

    const editButtonsAfter = screen.getAllByRole('button', { name: /editar/i });
    expect(editButtonsAfter).toHaveLength(1);
  });

  it('cancel personal restores original values', async () => {
    mockUseProfileQuery.mockReturnValue({ isLoading: false, isError: false, data: mockProfile, refetch: vi.fn() });
    const user = userEvent.setup();
    renderProfilePage();

    const editButtons = screen.getAllByRole('button', { name: /editar/i });
    await user.click(editButtons[0]);

    const nombreInput = screen.getByDisplayValue('Juan');
    await user.clear(nombreInput);
    await user.type(nombreInput, 'Pedro');

    const cancelButton = screen.getByRole('button', { name: /cancelar/i });
    await user.click(cancelButton);

    expect(screen.getByDisplayValue('Juan')).toBeInTheDocument();
  });
});
