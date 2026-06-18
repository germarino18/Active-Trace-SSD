import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { EquiposListPage } from '@/features/coordinacion/pages/EquiposListPage';
import { AvisosListPage } from '@/features/coordinacion/pages/AvisosListPage';
import { EncuentrosListPage } from '@/features/coordinacion/pages/EncuentrosListPage';
import { ConvocatoriasListPage } from '@/features/coordinacion/pages/ConvocatoriasListPage';
import { TareasListPage } from '@/features/coordinacion/pages/TareasListPage';
import { MonitorGeneralPage } from '@/features/coordinacion/pages/MonitorGeneralPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['COORDINADOR'],
        permissions: ['*'],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: () => true,
  }),
}));

let mockEquiposData: { asignaciones: []; total: number } = { asignaciones: [], total: 0 };
vi.mock('@/features/coordinacion/hooks/useEquipos', () => ({
  useEquipos: () => ({ data: mockEquiposData, isLoading: false }),
  useEliminarAsignacion: () => ({ mutate: vi.fn(), isPending: false }),
  useDocentes: () => ({ data: [], isLoading: false }),
  useAsignacionMasiva: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useClonarEquipo: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCrearAsignacion: () => ({ mutate: vi.fn(), isPending: false }),
  useActualizarAsignacion: () => ({ mutate: vi.fn(), isPending: false }),
  useMisEquipos: () => ({ data: { asignaciones: [], total: 0 }, isLoading: false }),
  useModificarVigencia: () => ({ mutate: vi.fn(), isPending: false }),
}));

let mockTareasData: { items: []; total: number } = { items: [], total: 0 };
vi.mock('@/features/coordinacion/hooks/useTareas', () => ({
  useTareas: () => ({ data: mockTareasData, isLoading: false, isError: false }),
  useMisTareas: () => ({ data: { items: [], total: 0 }, isLoading: false }),
  useTarea: () => ({ data: null, isLoading: false }),
  useCambiarEstado: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useAgregarComentario: () => ({ mutateAsync: vi.fn() }),
  useDelegarTarea: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCrearTarea: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

let mockAvisosData: { items: []; total: number } = { items: [], total: 0 };
vi.mock('@/features/coordinacion/hooks/useAvisos', () => ({
  useAvisos: () => ({ data: mockAvisosData, isLoading: false, isError: false }),
  useConfirmarAck: () => ({ mutate: vi.fn(), isPending: false }),
  useAviso: () => ({ data: null, isLoading: false }),
  useCrearAviso: () => ({ mutateAsync: vi.fn(), isPending: false, isError: false }),
  useActualizarAviso: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEliminarAviso: () => ({ mutate: vi.fn(), isPending: false }),
}));

let mockEncuentrosData: { items: []; total: number } = { items: [], total: 0 };
vi.mock('@/features/coordinacion/hooks/useEncuentros', () => ({
  useEncuentros: () => ({ data: mockEncuentrosData, isLoading: false, isError: false }),
  useEncuentro: () => ({ data: null, isLoading: false }),
  useCrearSlotRecurrente: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCrearEncuentroUnico: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useActualizarInstancia: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useGenerarHtml: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

let mockConvocatoriasData: { items: []; total: number } = { items: [], total: 0 };
vi.mock('@/features/coordinacion/hooks/useColoquios', () => ({
  useConvocatorias: () => ({ data: mockConvocatoriasData, isLoading: false, isError: false }),
  useConvocatoria: () => ({ data: null, isLoading: false }),
  useCrearConvocatoria: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useImportarAlumnos: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useMetricas: () => ({ data: null, isLoading: false }),
  useReservarTurno: () => ({ mutate: vi.fn(), isPending: false }),
  useResultados: () => ({ data: [], isLoading: false }),
}));

let mockMonitorData: { data: undefined; total_acciones: number } | undefined = undefined;
vi.mock('@/features/coordinacion/hooks/useMonitores', () => ({
  useMonitorGeneral: () => ({ data: mockMonitorData, isLoading: false, isError: false }),
  useMonitorCoordinacion: () => ({ data: null, isLoading: false }),
}));

describe('Empty states for coordinacion pages', () => {
  beforeEach(() => {
    mockEquiposData = { asignaciones: [], total: 0 };
    mockTareasData = { items: [], total: 0 };
    mockAvisosData = { items: [], total: 0 };
    mockEncuentrosData = { items: [], total: 0 };
    mockConvocatoriasData = { items: [], total: 0 };
    mockMonitorData = undefined;
  });

  it('EquiposListPage shows empty message', () => {
    render(<TestWrapper><EquiposListPage /></TestWrapper>);
    expect(screen.getByText('No se encontraron equipos docentes')).toBeInTheDocument();
  });

  it('TareasListPage shows empty message', () => {
    render(<TestWrapper><TareasListPage /></TestWrapper>);
    expect(
      screen.getByText('No se encontraron tareas con los filtros aplicados.'),
    ).toBeInTheDocument();
  });

  it('AvisosListPage shows empty message', () => {
    render(<TestWrapper><AvisosListPage /></TestWrapper>);
    expect(screen.getByText('No hay avisos disponibles')).toBeInTheDocument();
  });

  it('EncuentrosListPage shows empty message', () => {
    render(<TestWrapper><EncuentrosListPage /></TestWrapper>);
    expect(screen.getByText('No se encontraron encuentros')).toBeInTheDocument();
  });

  it('ConvocatoriasListPage shows empty message', () => {
    render(<TestWrapper><ConvocatoriasListPage /></TestWrapper>);
    expect(screen.getByText('No hay convocatorias registradas')).toBeInTheDocument();
  });

  it('MonitorGeneralPage shows empty message when no data', () => {
    render(<TestWrapper><MonitorGeneralPage /></TestWrapper>);
    expect(
      screen.getByText('No hay datos disponibles para el monitor'),
    ).toBeInTheDocument();
  });
});
