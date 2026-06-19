import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { ProfileResponse } from '@/features/perfil/types';

const mockGet = vi.fn();
const mockPatch = vi.fn();

vi.mock('@/shared/services/api', () => ({
  get: (...args: unknown[]) => mockGet(...args),
  patch: (...args: unknown[]) => mockPatch(...args),
}));

const mockUseQuery = vi.fn();
const mockUseMutation = vi.fn();
const mockInvalidateQueries = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: (...args: unknown[]) => mockUseQuery(...args),
    useMutation: (...args: unknown[]) => mockUseMutation(...args),
    useQueryClient: () => ({ invalidateQueries: mockInvalidateQueries }),
  };
});

import { useProfileQuery, useProfileMutation } from '@/features/perfil/hooks/useProfile';

const PROFILE_KEY = ['perfil'];

const mockProfile: ProfileResponse = {
  id: 'uuid-1',
  tenant_id: 'tenant-1',
  nombre: 'Juan',
  apellidos: 'García',
  email: 'juan@test.com',
  cuil: '20-12345678-9',
  dni: '12345678',
  cbu: null,
  alias_cbu: null,
  banco: 'Nación',
  regional: null,
  legajo: null,
  legajo_profesional: null,
  facturador: false,
  estado: 'Activo',
};

describe('useProfileQuery', () => {
  beforeEach(() => {
    mockUseQuery.mockReset();
    mockGet.mockReset();
  });

  it('calls useQuery with perfil key and GET /api/v1/perfil', () => {
    mockUseQuery.mockReturnValue({ data: mockProfile, isLoading: false, isError: false });

    useProfileQuery();

    expect(mockUseQuery).toHaveBeenCalledWith(
      expect.objectContaining({ queryKey: PROFILE_KEY }),
    );

    const callArg = mockUseQuery.mock.calls[0][0];
    mockGet.mockResolvedValue(mockProfile);
    callArg.queryFn();
    expect(mockGet).toHaveBeenCalledWith('/api/v1/perfil');
  });

  it('exposes data, isLoading, isError from useQuery', () => {
    mockUseQuery.mockReturnValue({ data: mockProfile, isLoading: false, isError: false });

    const result = useProfileQuery();

    expect(result.data).toEqual(mockProfile);
    expect(result.isLoading).toBe(false);
    expect(result.isError).toBe(false);
  });
});

describe('useProfileMutation', () => {
  beforeEach(() => {
    mockUseMutation.mockReset();
    mockPatch.mockReset();
    mockInvalidateQueries.mockReset();
  });

  it('calls useMutation with PATCH /api/v1/perfil — excludes cuil from body', () => {
    mockUseMutation.mockReturnValue({ mutateAsync: vi.fn(), isPending: false });

    useProfileMutation();

    expect(mockUseMutation).toHaveBeenCalled();

    const callArg = mockUseMutation.mock.calls[0][0];
    const payload = { nombre: 'Pedro', banco: 'Galicia' };
    mockPatch.mockResolvedValue({ ...mockProfile, ...payload });
    callArg.mutationFn(payload);

    expect(mockPatch).toHaveBeenCalledWith('/api/v1/perfil', payload);
    const patchBody = mockPatch.mock.calls[0][1];
    expect(patchBody).not.toHaveProperty('cuil');
    expect(patchBody).not.toHaveProperty('email');
  });

  it('invalidates perfil query on success', () => {
    mockUseMutation.mockReturnValue({ mutateAsync: vi.fn(), isPending: false });

    useProfileMutation();

    const callArg = mockUseMutation.mock.calls[0][0];
    callArg.onSuccess();

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: PROFILE_KEY });
  });
});
