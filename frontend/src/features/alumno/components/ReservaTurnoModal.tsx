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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="w-full max-w-md mx-4 rounded-xl bg-surface-container-lowest border border-outline-variant p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-label-md font-medium text-on-surface">Reservar turno — {convocatoria.materia_nombre}</h3>
          <button type="button" onClick={onClose} className="rounded-lg p-1 text-outline hover:text-on-surface transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <p className="text-label-sm text-on-surface-variant mb-4">
          Fecha límite: {new Date(convocatoria.fecha_limite).toLocaleDateString('es-AR')}
        </p>

        <div className="space-y-2 mb-6">
          {convocatoria.fechas.map((f: FechaConCupo) => (
            <button
              key={f.fecha_id}
              type="button"
              onClick={() => setSelectedFecha(f.fecha_id)}
              disabled={f.cupos_restantes === 0}
              className={`w-full flex items-center justify-between rounded-lg border p-3 text-left transition-colors ${
                selectedFecha === f.fecha_id
                  ? 'border-primary bg-primary/10'
                  : f.cupos_restantes === 0
                    ? 'border-outline-variant opacity-50 cursor-not-allowed'
                    : 'border-outline-variant hover:border-primary/50'
              }`}
            >
              <span className="text-label-sm text-on-surface">
                {new Date(f.fecha).toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' })}
              </span>
              <span className={`text-label-xs ${f.cupos_restantes > 0 ? 'text-tertiary' : 'text-error'}`}>
                {f.cupos_restantes > 0 ? `${f.cupos_restantes} cupo${f.cupos_restantes !== 1 ? 's' : ''}` : 'Sin cupo'}
              </span>
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          {reservaPropia ? (
            <button
              type="button"
              onClick={() => cancelarMutation.mutate()}
              disabled={cancelarMutation.isPending}
              className="flex-1 rounded-lg border border-error/50 px-4 py-2 text-label-sm font-medium text-error transition-colors hover:bg-error/10 disabled:opacity-50"
            >
              {cancelarMutation.isPending ? 'Cancelando...' : 'Cancelar reserva'}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => reservarMutation.mutate()}
              disabled={!selectedFecha || reservarMutation.isPending}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              {reservarMutation.isPending ? 'Reservando...' : 'Confirmar reserva'}
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cerrar
          </button>
        </div>

        {reservarMutation.isError && (
          <p className="mt-3 text-label-sm text-error">Error al reservar. Intentá de nuevo.</p>
        )}
        {cancelarMutation.isError && (
          <p className="mt-3 text-label-sm text-error">Error al cancelar. Intentá de nuevo.</p>
        )}
      </div>
    </div>
  );
}
