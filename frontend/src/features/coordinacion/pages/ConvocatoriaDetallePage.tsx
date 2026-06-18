import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  useConvocatoria,
  useImportarAlumnos,
  useMetricas,
  useResultados,
} from '../hooks/useColoquios';
import { MetricasColoquioCard } from '../components/MetricasColoquio';
import { Spinner } from '@/shared/components/Spinner';

type Tab = 'estudiantes' | 'reservas' | 'metricas' | 'resultados';

export function ConvocatoriaDetallePage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<Tab>('estudiantes');

  const { data: convocatoria, isLoading, isError } = useConvocatoria(id);
  const { data: metricas } = useMetricas(id);
  const { data: resultados } = useResultados(id);
  const importar = useImportarAlumnos();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importResult, setImportResult] = useState<string | null>(null);

  const handleImport = async () => {
    if (!id || !selectedFile) return;
    try {
      const result = await importar.mutateAsync({ convocatoriaId: id, file: selectedFile });
      setImportResult(`Se importaron ${result.alumnos} alumnos correctamente`);
      setSelectedFile(null);
    } catch {
      setImportResult('Error al importar alumnos');
    }
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: 'estudiantes', label: 'Estudiantes' },
    { key: 'reservas', label: 'Reservas' },
    { key: 'metricas', label: 'Métricas' },
    { key: 'resultados', label: 'Resultados' },
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError || !convocatoria) {
    return (
      <div className="rounded-xl border border-error/30 bg-error/5 p-6 text-center">
        <p className="text-body-md text-error">No se pudo cargar la convocatoria</p>
        <Link to="/coloquios" className="mt-2 inline-block text-label-sm text-primary hover:underline">
          Volver al listado
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Link to="/coloquios" className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">arrow_back</span>
        </Link>
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">
            {convocatoria.materia_nombre}
          </h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Instancia {convocatoria.instancia} &middot;{' '}
            {convocatoria.dias?.length ?? 0} día{(convocatoria.dias?.length ?? 0) !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      <div className="flex gap-1 rounded-xl border border-outline-variant bg-surface-container-lowest p-1">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 rounded-lg px-4 py-2 text-label-sm font-medium transition-colors ${
              tab === t.key
                ? 'bg-primary text-on-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'estudiantes' && (
        <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
          <div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">Importar Alumnos</h3>
            <p className="text-body-sm text-on-surface-variant mb-4">
              Subí un archivo CSV o XLSX con el listado de alumnos para esta convocatoria.
            </p>
          </div>

          <div
            onClick={() => document.getElementById('file-input')?.click()}
            className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-outline-variant bg-surface-container-lowest p-lg transition-colors hover:border-primary hover:bg-primary/5"
          >
            <input
              id="file-input"
              type="file"
              accept=".csv,.xlsx"
              onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              className="hidden"
              disabled={importar.isPending}
            />
            <span className="material-symbols-outlined text-[40px] text-outline mb-2">upload_file</span>
            <p className="text-body-md font-medium text-on-surface">
              {selectedFile ? selectedFile.name : 'Hacé clic para seleccionar un archivo'}
            </p>
            <p className="text-label-sm text-outline mt-1">Formatos aceptados: CSV, XLSX</p>
            {importar.isPending && (
              <div className="mt-3 flex items-center gap-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-outline border-t-primary" role="status" />
                <span className="text-label-sm text-on-surface-variant">Subiendo archivo...</span>
              </div>
            )}
          </div>

          {importResult && (
            <div className={`rounded-lg border p-3 text-label-sm ${
              importResult.startsWith('Se') ? 'border-success/30 bg-success/5 text-success' : 'border-error/30 bg-error/5 text-error'
            }`}>
              {importResult}
            </div>
          )}

          {selectedFile && !importar.isPending && (
            <div className="flex gap-2">
              <button
                onClick={handleImport}
                className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
              >
                Importar
              </button>
              <button
                onClick={() => { setSelectedFile(null); setImportResult(null); }}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-4 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container"
              >
                Cancelar
              </button>
            </div>
          )}

          {convocatoria.dias && convocatoria.dias.length > 0 && (
            <div className="mt-6">
              <h4 className="text-label-sm font-medium text-on-surface-variant mb-3">Días de la convocatoria</h4>
              <div className="space-y-2">
                {convocatoria.dias.map((dia, i) => (
                  <div key={dia.id ?? i} className="flex items-center justify-between rounded-lg bg-surface-container px-4 py-3">
                    <div className="flex items-center gap-4">
                      <span className="material-symbols-outlined text-[18px] text-outline">calendar_today</span>
                      <div>
                        <p className="text-body-sm text-on-surface">{dia.fecha}</p>
                        <p className="text-label-xs text-on-surface-variant">{dia.hora_inicio} - {dia.hora_fin}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-body-sm text-on-surface">{dia.slots} slots</p>
                      <p className="text-label-xs text-on-surface-variant">{dia.cupo_por_slot} cupos c/u</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === 'reservas' && (
        <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
          <h3 className="font-headline-sm text-headline-sm text-on-surface">Reservas</h3>
          {resultados && resultados.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-outline-variant">
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Alumno</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Legajo</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Fecha</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Hora</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {resultados.map((reserva) => (
                    <tr key={reserva.id} className="border-b border-outline-variant">
                      <td className="px-4 py-3 text-body-sm text-on-surface">{reserva.alumno_nombre}</td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">{reserva.alumno_legajo}</td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">{reserva.fecha}</td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">{reserva.hora}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center rounded-full bg-info/10 px-2 py-0.5 text-label-xs font-medium text-info">
                          {reserva.estado}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-body-md text-on-surface-variant py-8 text-center">No hay reservas registradas</p>
          )}
        </div>
      )}

      {tab === 'metricas' && (
        <div className="space-y-4">
          <MetricasColoquioCard metrics={metricas ?? { total_alumnos: 0, instancias_activas: 0, reservas_activas: 0, cupos_libres: 0 }} />
          {!metricas && (
            <p className="text-center text-body-sm text-on-surface-variant">No hay métricas disponibles</p>
          )}
        </div>
      )}

      {tab === 'resultados' && (
        <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
          <h3 className="font-headline-sm text-headline-sm text-on-surface">Resultados</h3>
          {resultados && resultados.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-outline-variant">
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Alumno</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Legajo</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Fecha</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                    <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nota</th>
                  </tr>
                </thead>
                <tbody>
                  {resultados.map((reserva) => (
                    <tr key={reserva.id} className="border-b border-outline-variant">
                      <td className="px-4 py-3 text-body-sm text-on-surface">{reserva.alumno_nombre}</td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">{reserva.alumno_legajo}</td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">{reserva.fecha}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${
                          reserva.estado === 'Aprobado' ? 'bg-success/10 text-success' :
                          reserva.estado === 'Desaprobado' ? 'bg-error/10 text-error' :
                          'bg-warning/10 text-warning'
                        }`}>
                          {reserva.estado}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                        {reserva.nota != null ? reserva.nota : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-body-md text-on-surface-variant py-8 text-center">No hay resultados disponibles</p>
          )}
        </div>
      )}
    </div>
  );
}
