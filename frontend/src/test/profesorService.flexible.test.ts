/**
 * 4.2 RED → GREEN: enviarComunicadoFlexible service function tests.
 *
 * TDD cycle:
 *   RED:   tests written before implementation (import will fail first)
 *   GREEN: function added in profesor.service.ts — tests pass
 *   TRIANGULATE: individual (single-element) and general (multi-element) cases
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the api module before importing the service
vi.mock('@/shared/services/api', () => ({
  post: vi.fn(),
}));

import * as api from '@/shared/services/api';
import { enviarComunicadoFlexible } from '@/features/profesor/services/profesor.service';
import type { ComunicadoFlexibleData } from '@/features/profesor/types';

const mockPost = api.post as ReturnType<typeof vi.fn>;

describe('enviarComunicadoFlexible', () => {
  beforeEach(() => {
    mockPost.mockReset();
  });

  it('calls POST /api/v1/profesor/comunicado-atrasados-flexible with the payload', async () => {
    const payload: ComunicadoFlexibleData = {
      actividad_id: null,
      asunto_template: 'Hola {alumno_nombre}',
      cuerpo_template: 'Tenés materias pendientes.',
      destinatarios: [
        { entrada_padron_id: 'ep-1', dictado_id: 'd-1' },
      ],
    };
    const mockResult = { total: 1, lote_id: 'lote-abc', lotes: ['lote-abc'] };
    mockPost.mockResolvedValueOnce(mockResult);

    const result = await enviarComunicadoFlexible(payload);

    expect(mockPost).toHaveBeenCalledWith(
      '/api/v1/profesor/comunicado-atrasados-flexible',
      payload,
    );
    expect(result).toEqual(mockResult);
  });

  it('sends multiple destinatarios in general mode (TRIANGULATE)', async () => {
    const payload: ComunicadoFlexibleData = {
      actividad_id: undefined,
      asunto_template: 'Mensaje general {alumno_nombre}',
      cuerpo_template: 'Tenés atrasos.',
      destinatarios: [
        { entrada_padron_id: 'ep-1', dictado_id: 'd-1' },
        { entrada_padron_id: 'ep-2', dictado_id: 'd-2' },
      ],
    };
    const mockResult = { total: 2, lote_id: null, lotes: ['lote-1', 'lote-2'] };
    mockPost.mockResolvedValueOnce(mockResult);

    const result = await enviarComunicadoFlexible(payload);

    expect(mockPost).toHaveBeenCalledWith(
      '/api/v1/profesor/comunicado-atrasados-flexible',
      payload,
    );
    expect(result.total).toBe(2);
    expect(result.lotes).toHaveLength(2);
  });

  it('sends with actividad_id when provided (TRIANGULATE)', async () => {
    const actividadId = 'act-uuid-123';
    const payload: ComunicadoFlexibleData = {
      actividad_id: actividadId,
      asunto_template: 'Actividad pendiente',
      cuerpo_template: 'Tenés la actividad pendiente.',
      destinatarios: [{ entrada_padron_id: 'ep-3', dictado_id: 'd-3' }],
    };
    const mockResult = { total: 1, lote_id: 'lote-xyz', lotes: ['lote-xyz'] };
    mockPost.mockResolvedValueOnce(mockResult);

    await enviarComunicadoFlexible(payload);

    const calledWith = mockPost.mock.calls[0][1] as ComunicadoFlexibleData;
    expect(calledWith.actividad_id).toBe(actividadId);
  });
});
