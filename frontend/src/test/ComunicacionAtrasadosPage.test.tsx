import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComunicacionAtrasadosPage } from '@/features/academico/pages/ComunicacionAtrasadosPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockPreview = vi.fn();

vi.mock('@/features/academico/hooks/useAtrasados', () => ({
  useAtrasados: () => ({
    data: {
      alumnos: [
        {
          alumno: { id: '1', legajo: '123', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', comision: 'A' },
          actividades_pendientes: 3,
          nota_actual: 4.5,
          porcentaje: 45,
          estado: 'atrasado',
        },
      ],
      umbral: 60,
    },
    isLoading: false,
  }),
}));

vi.mock('@/features/academico/hooks/useComunicacion', () => ({
  usePreviewComunicacion: () => ({
    mutateAsync: mockPreview,
    data: {
      asunto: 'Comunicación de atraso',
      cuerpo: 'Estimado estudiante:',
      destinatarios: [
        {
          alumno: { id: '1', legajo: '123', nombre: 'Juan', apellido: 'Perez', email: 'juan@test.com', comision: 'A' },
          asunto: 'Atraso en actividades',
          cuerpo: 'Tiene 3 actividades pendientes',
        },
      ],
    },
    isPending: false,
    isError: false,
    error: null,
  }),
  useEnviarComunicacion: () => ({
    mutateAsync: vi.fn().mockResolvedValue({ comunicacion_id: 'comm-123' }),
    isPending: false,
    isError: false,
    error: null,
    isSuccess: false,
  }),
  useStatusComunicacion: () => ({
    data: null,
    isLoading: false,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/materias/123/comunicar']}>
        <Routes>
          <Route path="/materias/:id/comunicar" element={<ComunicacionAtrasadosPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ComunicacionAtrasadosPage', () => {
  it('renders student list for selection', () => {
    renderPage();
    expect(screen.getByText(/Perez, Juan/)).toBeInTheDocument();
    expect(screen.getByText('juan@test.com')).toBeInTheDocument();
  });

  it('shows selection count', async () => {
    const user = userEvent.setup();
    renderPage();

    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);

    expect(screen.getByText(/1 alumno/)).toBeInTheDocument();
  });

  it('enables preview button when students are selected', async () => {
    const user = userEvent.setup();
    renderPage();

    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);

    const previewBtn = screen.getByText('Vista previa');
    expect(previewBtn).not.toBeDisabled();
  });

  it('calls preview mutation when button clicked', async () => {
    const user = userEvent.setup();
    renderPage();

    const checkbox = screen.getByRole('checkbox');
    await user.click(checkbox);

    const previewBtn = screen.getByText('Vista previa');
    await user.click(previewBtn);

    expect(mockPreview).toHaveBeenCalledWith(['1']);
  });
});
