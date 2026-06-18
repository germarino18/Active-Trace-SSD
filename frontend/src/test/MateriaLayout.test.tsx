import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MateriaLayout } from '@/features/academico/components/MateriaLayout';

function renderLayout() {
  return render(
    <MemoryRouter initialEntries={['/materias/123/importar']}>
      <Routes>
        <Route path="/materias/:id" element={<MateriaLayout />}>
          <Route path="importar" element={<div>Importar Page Content</div>} />
          <Route path="atrasados" element={<div>Atrasados Page Content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe('MateriaLayout', () => {
  it('renders tabs for sub-pages', () => {
    renderLayout();
    expect(screen.getByText('Importar')).toBeInTheDocument();
    expect(screen.getByText('Atrasados')).toBeInTheDocument();
    expect(screen.getByText('Comunicar')).toBeInTheDocument();
    expect(screen.getByText('Entregas Pendientes')).toBeInTheDocument();
    expect(screen.getByText('Monitor')).toBeInTheDocument();
  });

  it('renders active tab content', () => {
    renderLayout();
    expect(screen.getByText('Importar Page Content')).toBeInTheDocument();
  });

  it('shows materia ID in header', () => {
    renderLayout();
    expect(screen.getByText(/ID: 123/)).toBeInTheDocument();
  });

  it('navigates between tabs', async () => {
    renderLayout();
    const atrasadosLink = screen.getByText('Atrasados');
    expect(atrasadosLink.getAttribute('href')).toContain('atrasados');
  });
});
