import { useState } from 'react';
import { useGuardias, useRegistrarGuardia } from '../hooks/useGuardias';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import type { RegistrarGuardiaData } from '../types/tutor.types';

export function GuardiasListPage() {
  const { data, isLoading, isError, refetch } = useGuardias();
  const registrarGuardia = useRegistrarGuardia();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<RegistrarGuardiaData>({
    tipo: 'guardia',
    fecha: '',
    hora_inicio: '',
    hora_fin: '',
    materia_id: '',
    comision: '',
    observaciones: '',
  });
  const [formError, setFormError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    if (!formData.fecha || !formData.hora_inicio || !formData.hora_fin || !formData.materia_id) {
      setFormError('Completá los campos obligatorios: fecha, hora inicio, hora fin y materia');
      return;
    }

    try {
      await registrarGuardia.mutateAsync(formData);
      setShowForm(false);
      setFormData({ tipo: 'guardia', fecha: '', hora_inicio: '', hora_fin: '', materia_id: '', comision: '', observaciones: '' });
    } catch {
      setFormError('Error al registrar la guardia');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Guardias</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Registro y seguimiento de guardias docentes.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
        >
          <span className="material-symbols-outlined text-[18px]">{showForm ? 'close' : 'add'}</span>
          {showForm ? 'Cancelar' : 'Nueva Guardia'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <label htmlFor="fecha" className="block text-label-sm font-medium text-on-surface mb-1">Fecha *</label>
              <input
                id="fecha"
                type="date"
                value={formData.fecha}
                onChange={(e) => setFormData((prev) => ({ ...prev, fecha: e.target.value }))}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface"
              />
            </div>
            <div>
              <label htmlFor="hora_inicio" className="block text-label-sm font-medium text-on-surface mb-1">Hora Inicio *</label>
              <input
                id="hora_inicio"
                type="time"
                value={formData.hora_inicio}
                onChange={(e) => setFormData((prev) => ({ ...prev, hora_inicio: e.target.value }))}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface"
              />
            </div>
            <div>
              <label htmlFor="hora_fin" className="block text-label-sm font-medium text-on-surface mb-1">Hora Fin *</label>
              <input
                id="hora_fin"
                type="time"
                value={formData.hora_fin}
                onChange={(e) => setFormData((prev) => ({ ...prev, hora_fin: e.target.value }))}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface"
              />
            </div>
            <div>
              <label htmlFor="materia_id" className="block text-label-sm font-medium text-on-surface mb-1">Materia *</label>
              <input
                id="materia_id"
                type="text"
                value={formData.materia_id}
                onChange={(e) => setFormData((prev) => ({ ...prev, materia_id: e.target.value }))}
                placeholder="ID de la materia"
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface"
              />
            </div>
            <div>
              <label htmlFor="comision" className="block text-label-sm font-medium text-on-surface mb-1">Comisión</label>
              <input
                id="comision"
                type="text"
                value={formData.comision || ''}
                onChange={(e) => setFormData((prev) => ({ ...prev, comision: e.target.value }))}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface"
              />
            </div>
            <div>
              <label htmlFor="observaciones" className="block text-label-sm font-medium text-on-surface mb-1">Observaciones</label>
              <input
                id="observaciones"
                type="text"
                value={formData.observaciones || ''}
                onChange={(e) => setFormData((prev) => ({ ...prev, observaciones: e.target.value }))}
                className="w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface"
              />
            </div>
          </div>

          {formError && (
            <p className="text-label-sm text-error">{formError}</p>
          )}

          {registrarGuardia.isError && (
            <p className="text-label-sm text-error">
              {registrarGuardia.error?.message || 'Error al registrar la guardia'}
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={registrarGuardia.isPending}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              {registrarGuardia.isPending ? 'Registrando...' : 'Registrar Guardia'}
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <LoadingState rows={5} cols={5} />
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState message="No hay guardias registradas" icon="shield_off" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Fecha</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Hora Inicio</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Hora Fin</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((guardia) => (
                <tr
                  key={guardia.id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm text-on-surface">
                    {new Date(guardia.fecha).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{guardia.materia_nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{guardia.hora_inicio}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{guardia.hora_fin}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex rounded-full bg-info/10 px-2 py-0.5 text-label-xs font-medium text-info">
                      {guardia.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
