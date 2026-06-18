import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ImportarCalificacionesPage } from '@/features/academico/pages/ImportarCalificacionesPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockUpload = vi.fn();

vi.mock('@/features/academico/hooks/useImportarCalificaciones', () => ({
  useUploadCalificaciones: () => ({
    mutateAsync: mockUpload,
    isPending: false,
    isError: false,
    error: null,
  }),
  useConfirmarImportacion: () => ({
    mutateAsync: vi.fn().mockResolvedValue({ message: 'ok' }),
    isPending: false,
    isSuccess: false,
    isError: false,
    error: null,
  }),
  useConfigurarUmbral: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
    isSuccess: false,
    isError: false,
    error: null,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/materias/123/importar']}>
        <Routes>
          <Route path="/materias/:id/importar" element={<ImportarCalificacionesPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ImportarCalificacionesPage', () => {
  beforeEach(() => {
    mockUpload.mockReset();
  });

  it('renders upload area', () => {
    renderPage();
    expect(screen.getByText(/subí un archivo/i)).toBeInTheDocument();
    expect(screen.getByText(/hacé clic para seleccionar/i)).toBeInTheDocument();
  });

  it('shows file name after valid file selection', () => {
    renderPage();
    const fileInput = screen.getByTestId('file-input');
    const file = new File(['test'], 'notas.csv', { type: 'text/csv' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText('notas.csv')).toBeInTheDocument();
  });

  it('shows error for invalid file format', () => {
    renderPage();
    const fileInput = screen.getByTestId('file-input');
    const file = new File(['test'], 'notas.pdf', { type: 'application/pdf' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText(/Formato de archivo no soportado/i)).toBeInTheDocument();
  });
});
