import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';

import * as aprobacionService from '@/features/coordinacion/services/aprobacion-comunicaciones.service';

vi.mock('@/features/coordinacion/services/aprobacion-comunicaciones.service');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
};

import {
  useLotesPendientes,
  useLotesPendientesCount,
  useAprobarLote,
  useCancelarLote,
} from '@/features/coordinacion/hooks/useAprobacionComunicaciones';

const mockLotes = {
  items: [
    {
      lote_id: 'l1',
      docente_id: 'd1',
      docente_nombre: 'Prof. García',
      asunto: 'Asunto test',
      cuerpo: 'Cuerpo test',
      total_destinatarios: 5,
      created_at: '2026-01-01T00:00:00Z',
    },
  ],
  total: 1,
};

describe('useLotesPendientes', () => {
  beforeEach(() => {
    vi.mocked(aprobacionService.getLotesPendientes).mockResolvedValue(mockLotes);
  });

  it('fetches pending lotes from service', async () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useLotesPendientes(), { wrapper });

    await vi.waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockLotes);
    expect(aprobacionService.getLotesPendientes).toHaveBeenCalledOnce();
  });
});

describe('useLotesPendientesCount', () => {
  it('returns total from query data', async () => {
    vi.mocked(aprobacionService.getLotesPendientes).mockResolvedValue(mockLotes);
    const wrapper = createWrapper();
    const { result } = renderHook(() => useLotesPendientesCount(), { wrapper });

    await vi.waitFor(() => expect(result.current).toBe(1));
  });

  it('returns 0 when data is not loaded yet', () => {
    vi.mocked(aprobacionService.getLotesPendientes).mockImplementation(
      () => new Promise(() => {}),
    );
    const wrapper = createWrapper();
    const { result } = renderHook(() => useLotesPendientesCount(), { wrapper });
    expect(result.current).toBe(0);
  });
});

describe('useAprobarLote', () => {
  it('calls aprobarLote service and invalidates cache on success', async () => {
    vi.mocked(aprobacionService.getLotesPendientes).mockResolvedValue(mockLotes);
    vi.mocked(aprobacionService.aprobarLote).mockResolvedValue(undefined);
    const wrapper = createWrapper();
    const { result } = renderHook(() => useAprobarLote(), { wrapper });

    await act(async () => {
      await result.current.mutateAsync('l1');
    });

    expect(aprobacionService.aprobarLote).toHaveBeenCalledWith('l1');
    await vi.waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useCancelarLote', () => {
  it('calls cancelarLote service and invalidates cache on success', async () => {
    vi.mocked(aprobacionService.getLotesPendientes).mockResolvedValue(mockLotes);
    vi.mocked(aprobacionService.cancelarLote).mockResolvedValue(undefined);
    const wrapper = createWrapper();
    const { result } = renderHook(() => useCancelarLote(), { wrapper });

    await act(async () => {
      await result.current.mutateAsync('l1');
    });

    expect(aprobacionService.cancelarLote).toHaveBeenCalledWith('l1');
    await vi.waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});
