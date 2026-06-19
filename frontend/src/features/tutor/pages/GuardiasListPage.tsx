import { useState } from 'react';
import { useGuardias, useRegistrarGuardia } from '../hooks/useGuardias';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Button, Badge, Input } from '@/shared/components/ds';
import type { RegistrarGuardiaData } from '../types/tutor.types';

const ESTADO_TONE: Record<string, 'success' | 'warning' | 'neutral'> = {
  Confirmada: 'success',
  Pendiente: 'warning',
};

export function GuardiasListPage() {
  const { data, isLoading, isError, refetch } = useGuardias();
  const registrarGuardia = useRegistrarGuardia();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<RegistrarGuardiaData>({
    tipo: 'guardia', fecha: '', hora_inicio: '', hora_fin: '', materia_id: '', comision: '', observaciones: '',
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

  const items = data?.items ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Guardias</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Registro y seguimiento de guardias docentes.</p>
        </div>
        <Button
          variant={showForm ? 'secondary' : 'primary'}
          icon={showForm ? 'close' : 'add'}
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancelar' : 'Nueva Guardia'}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ background: 'var(--surface-container-lowest)', border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-lg)', padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
            <Input label="Fecha *" type="date" value={formData.fecha} onChange={(e) => setFormData((p) => ({ ...p, fecha: e.target.value }))} />
            <Input label="Hora Inicio *" type="time" value={formData.hora_inicio} onChange={(e) => setFormData((p) => ({ ...p, hora_inicio: e.target.value }))} />
            <Input label="Hora Fin *" type="time" value={formData.hora_fin} onChange={(e) => setFormData((p) => ({ ...p, hora_fin: e.target.value }))} />
            <Input label="Materia ID *" placeholder="ID de la materia" value={formData.materia_id} onChange={(e) => setFormData((p) => ({ ...p, materia_id: e.target.value }))} />
            <Input label="Comisión" value={formData.comision || ''} onChange={(e) => setFormData((p) => ({ ...p, comision: e.target.value }))} />
            <Input label="Observaciones" value={formData.observaciones || ''} onChange={(e) => setFormData((p) => ({ ...p, observaciones: e.target.value }))} />
          </div>
          {(formError || registrarGuardia.isError) && (
            <p style={{ margin: 0, fontSize: 13, color: 'var(--error)' }}>
              {formError || registrarGuardia.error?.message || 'Error al registrar la guardia'}
            </p>
          )}
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button type="submit" variant="primary" icon="save" disabled={registrarGuardia.isPending}>
              {registrarGuardia.isPending ? 'Registrando…' : 'Registrar Guardia'}
            </Button>
          </div>
        </form>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : isError ? (
        <EmptyState icon="error" title="Error al cargar guardias" action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>} />
      ) : items.length === 0 ? (
        <EmptyState icon="shield_off" title="No hay guardias registradas" message="Registrá tu primera guardia con el botón de arriba." />
      ) : (
        <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--surface-container)', borderBottom: '1px solid var(--outline-variant)' }}>
                {['Fecha', 'Materia', 'Hora Inicio', 'Hora Fin', 'Estado'].map((h) => (
                  <th key={h} style={{ padding: '12px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((g, i) => (
                <tr key={g.id}
                  style={{ borderTop: i > 0 ? '1px solid var(--outline-variant)' : undefined, background: 'var(--surface-container-lowest)', transition: 'background .12s ease' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--surface-container-low)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--surface-container-lowest)')}
                >
                  <td style={{ padding: '12px 16px', fontSize: 14, color: 'var(--on-surface)', fontFamily: 'var(--font-mono)' }}>
                    {new Date(g.fecha).toLocaleDateString('es-AR')}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)' }}>{g.materia_nombre}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>{g.hora_inicio}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>{g.hora_fin}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <Badge tone={ESTADO_TONE[g.estado] ?? 'neutral'}>{g.estado}</Badge>
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
