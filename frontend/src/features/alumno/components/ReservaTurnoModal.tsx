import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { ConvocatoriaColoquio, FechaConCupo, ReservaColoquio } from '../types/alumno.types';
import * as alumnoService from '../services/alumno.service';

interface ReservaTurnoModalProps {
  convocatoria: ConvocatoriaColoquio;
  reservaPropia?: ReservaColoquio | null;
  onClose: () => void;
}

export function ReservaTurnoModal({ convocatoria, reservaPropia, onClose }: ReservaTurnoModalProps) {
  const queryClient = useQueryClient();
  const [selectedFecha, setSelectedFecha] = useState<string | null>(
    reservaPropia?.fecha ?? null,
  );

  const reservarMutation = useMutation({
    mutationFn: () => alumnoService.reservarTurno(convocatoria.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alumno', 'coloquios'] });
      onClose();
    },
  });

  const cancelarMutation = useMutation({
    mutationFn: () => alumnoService.cancelarReserva(reservaPropia!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alumno', 'coloquios'] });
      onClose();
    },
  });

  return (
    <div
      style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.5)' }}
      onClick={onClose}
    >
      <div
        style={{ width: '100%', maxWidth: 448, margin: '0 16px', borderRadius: 'var(--radius-xl)', background: 'var(--surface-container-lowest)', border: '1px solid var(--outline-variant)', padding: 24, boxShadow: 'var(--shadow-xl)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h3 style={{ margin: 0, fontSize: 14, fontWeight: 500, color: 'var(--on-surface)' }}>
            Reservar turno — {convocatoria.materia_nombre}
          </h3>
          <button type="button" onClick={onClose} style={{ borderRadius: 'var(--radius-lg)', padding: 4, border: 'none', background: 'none', color: 'var(--outline)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>close</span>
          </button>
        </div>

        <p style={{ margin: '0 0 16px', fontSize: 13, color: 'var(--on-surface-variant)' }}>
          Fecha límite: {new Date(convocatoria.fecha_limite).toLocaleDateString('es-AR')}
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 24 }}>
          {convocatoria.fechas.map((f: FechaConCupo) => (
            <button
              key={f.fecha_id}
              type="button"
              onClick={() => setSelectedFecha(f.fecha_id)}
              disabled={f.cupos_restantes === 0}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderRadius: 'var(--radius-lg)',
                border: `1px solid ${
                  selectedFecha === f.fecha_id
                    ? 'var(--primary)'
                    : f.cupos_restantes === 0
                      ? 'var(--outline-variant)'
                      : 'var(--outline-variant)'
                }`,
                background: selectedFecha === f.fecha_id ? 'color-mix(in srgb, var(--primary) 10%, transparent)' : 'transparent',
                padding: 12,
                textAlign: 'left',
                cursor: f.cupos_restantes === 0 ? 'not-allowed' : 'pointer',
                opacity: f.cupos_restantes === 0 ? 0.5 : 1,
                transition: 'border-color .15s ease, background .15s ease',
              }}
              onMouseEnter={(e) => {
                if (f.cupos_restantes > 0 && selectedFecha !== f.fecha_id) {
                  e.currentTarget.style.borderColor = 'var(--primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedFecha !== f.fecha_id) {
                  e.currentTarget.style.borderColor = 'var(--outline-variant)';
                }
              }}
            >
              <span style={{ fontSize: 13, color: 'var(--on-surface)' }}>
                {new Date(f.fecha).toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' })}
              </span>
              <span style={{ fontSize: 12, color: f.cupos_restantes > 0 ? 'var(--tertiary)' : 'var(--error)' }}>
                {f.cupos_restantes > 0 ? `${f.cupos_restantes} cupo${f.cupos_restantes !== 1 ? 's' : ''}` : 'Sin cupo'}
              </span>
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          {reservaPropia ? (
            <button
              type="button"
              onClick={() => cancelarMutation.mutate()}
              disabled={cancelarMutation.isPending}
              style={{
                flex: 1,
                borderRadius: 'var(--radius-lg)',
                border: '1px solid color-mix(in srgb, var(--error) 50%, transparent)',
                padding: '8px 16px',
                fontSize: 13,
                fontWeight: 500,
                color: 'var(--error)',
                background: 'transparent',
                cursor: cancelarMutation.isPending ? 'not-allowed' : 'pointer',
                opacity: cancelarMutation.isPending ? 0.5 : 1,
                transition: 'background .15s ease',
              }}
              onMouseEnter={(e) => { if (!cancelarMutation.isPending) e.currentTarget.style.background = 'color-mix(in srgb, var(--error) 10%, transparent)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              {cancelarMutation.isPending ? 'Cancelando...' : 'Cancelar reserva'}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => reservarMutation.mutate()}
              disabled={!selectedFecha || reservarMutation.isPending}
              style={{
                flex: 1,
                borderRadius: 'var(--radius-lg)',
                border: 'none',
                padding: '8px 16px',
                fontSize: 13,
                fontWeight: 500,
                color: 'var(--on-primary)',
                background: 'var(--primary)',
                cursor: (!selectedFecha || reservarMutation.isPending) ? 'not-allowed' : 'pointer',
                opacity: (!selectedFecha || reservarMutation.isPending) ? 0.5 : 1,
                transition: 'background .15s ease',
              }}
              onMouseEnter={(e) => { if (selectedFecha && !reservarMutation.isPending) e.currentTarget.style.background = 'color-mix(in srgb, var(--primary) 90%, black)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--primary)'; }}
            >
              {reservarMutation.isPending ? 'Reservando...' : 'Confirmar reserva'}
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            style={{
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--outline-variant)',
              padding: '8px 16px',
              fontSize: 13,
              fontWeight: 500,
              color: 'var(--on-surface)',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'background .15s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-container-low)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
          >
            Cerrar
          </button>
        </div>

        {reservarMutation.isError && (
          <p style={{ marginTop: 12, fontSize: 13, color: 'var(--error)' }}>
            Error al reservar. Intentá de nuevo.
          </p>
        )}
        {cancelarMutation.isError && (
          <p style={{ marginTop: 12, fontSize: 13, color: 'var(--error)' }}>
            Error al cancelar. Intentá de nuevo.
          </p>
        )}
      </div>
    </div>
  );
}
