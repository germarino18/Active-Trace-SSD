import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useEncuentro, useActualizarInstancia, useGenerarHtml } from '../hooks/useEncuentros';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Spinner } from '@/shared/components/Spinner';
import type { InstanciaEstado } from '../types';

const estadoOptions: InstanciaEstado[] = ['Pendiente', 'Realizado', 'Cancelado'];

export function EncuentroDetallePage() {
  const { id } = useParams<{ id: string }>();
  const { hasPermission } = useAuth();

  const { data: encuentro, isLoading, isError } = useEncuentro(id);
  const actualizar = useActualizarInstancia();
  const generarHtml = useGenerarHtml();

  const [estado, setEstado] = useState<InstanciaEstado>('Pendiente');
  const [urlMeet, setUrlMeet] = useState('');
  const [urlGrabacion, setUrlGrabacion] = useState('');
  const [comentario, setComentario] = useState('');
  const [htmlGenerado, setHtmlGenerado] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (encuentro) {
      setEstado(encuentro.estado);
      setUrlMeet(encuentro.url_meet ?? '');
      setUrlGrabacion(encuentro.url_grabacion ?? '');
      setComentario(encuentro.comentario_interno ?? '');
    }
  }, [encuentro]);

  const handleSave = async () => {
    if (!id) return;
    try {
      await actualizar.mutateAsync({
        id,
        data: {
          estado,
          url_meet: urlMeet || undefined,
          url_grabacion: urlGrabacion || undefined,
          comentario_interno: comentario || undefined,
        },
      });
    } catch {
      // handled by query error state
    }
  };

  const handleGenerarHtml = async () => {
    if (!id) return;
    try {
      const html = await generarHtml.mutateAsync(id);
      setHtmlGenerado(html);
    } catch {
      // handled by mutation error state
    }
  };

  const handleCopyHtml = async () => {
    if (!htmlGenerado) return;
    try {
      await navigator.clipboard.writeText(htmlGenerado);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard not available
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError || !encuentro) {
    return (
      <div className="rounded-xl border border-error/30 bg-error/5 p-6 text-center">
        <p className="text-body-md text-error">No se pudo cargar el encuentro</p>
        <Link to="/encuentros" className="mt-2 inline-block text-label-sm text-primary hover:underline">
          Volver al listado
        </Link>
      </div>
    );
  }

  const canEdit = hasPermission('coordinacion:encuentros:editar');
  const dirty = estado !== encuentro.estado
    || urlMeet !== (encuentro.url_meet ?? '')
    || urlGrabacion !== (encuentro.url_grabacion ?? '')
    || comentario !== (encuentro.comentario_interno ?? '');

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-2">
        <Link to="/encuentros" className="text-on-surface-variant hover:text-on-surface">
          <span className="material-symbols-outlined">arrow_back</span>
        </Link>
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">{encuentro.titulo}</h2>
          <p className="text-body-md text-on-surface-variant mt-1">{encuentro.materia_nombre}</p>
        </div>
      </div>

      <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-label-sm text-on-surface-variant">Fecha</p>
            <p className="text-body-md text-on-surface">{encuentro.fecha}</p>
          </div>
          <div>
            <p className="text-label-sm text-on-surface-variant">Horario</p>
            <p className="text-body-md text-on-surface">{encuentro.hora_inicio} - {encuentro.hora_fin}</p>
          </div>
          {encuentro.docente_nombre && (
            <div>
              <p className="text-label-sm text-on-surface-variant">Docente</p>
              <p className="text-body-md text-on-surface">{encuentro.docente_nombre}</p>
            </div>
          )}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Estado</label>
          {canEdit ? (
            <select
              value={estado}
              onChange={(e) => setEstado(e.target.value as InstanciaEstado)}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
            >
              {estadoOptions.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          ) : (
            <p className="text-body-md text-on-surface">{estado}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">URL Meet</label>
          {canEdit ? (
            <input
              value={urlMeet}
              onChange={(e) => setUrlMeet(e.target.value)}
              placeholder="https://meet.google.com/..."
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
          ) : (
            <p className="text-body-md text-on-surface">{urlMeet || '-'}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">URL Grabación</label>
          {canEdit ? (
            <input
              value={urlGrabacion}
              onChange={(e) => setUrlGrabacion(e.target.value)}
              placeholder="https://drive.google.com/..."
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
          ) : (
            <p className="text-body-md text-on-surface">{urlGrabacion || '-'}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Comentario interno</label>
          {canEdit ? (
            <textarea
              value={comentario}
              onChange={(e) => setComentario(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
          ) : (
            <p className="text-body-md text-on-surface">{comentario || '-'}</p>
          )}
        </div>

        {canEdit && (
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              disabled={!dirty || actualizar.isPending}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              {actualizar.isPending && <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />}
              Guardar Cambios
            </button>
            {actualizar.isSuccess && (
              <span className="inline-flex items-center text-label-sm text-success">Cambios guardados</span>
            )}
            {actualizar.isError && (
              <span className="inline-flex items-center text-label-sm text-error">Error al guardar</span>
            )}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
        <h3 className="font-headline-sm text-headline-sm text-on-surface mb-4">Aula Virtual</h3>
        <button
          onClick={handleGenerarHtml}
          disabled={generarHtml.isPending}
          className="inline-flex items-center gap-2 rounded-lg border border-outline-variant bg-surface-container px-4 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container-high disabled:opacity-50"
        >
          {generarHtml.isPending ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-outline border-t-primary" />
          ) : (
            <span className="material-symbols-outlined text-[18px]">code</span>
          )}
          Generar contenido para el aula virtual
        </button>

        {htmlGenerado && (
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-label-sm text-on-surface-variant">HTML generado:</p>
              <button
                onClick={handleCopyHtml}
                className="inline-flex items-center gap-1 rounded-lg bg-surface-container px-3 py-1.5 text-label-xs text-on-surface-variant transition-colors hover:bg-surface-container-high"
              >
                <span className="material-symbols-outlined text-[14px]">
                  {copied ? 'check' : 'content_copy'}
                </span>
                {copied ? 'Copiado' : 'Copiar'}
              </button>
            </div>
            <pre className="max-h-96 overflow-auto rounded-lg border border-outline-variant bg-surface p-4 text-label-xs text-on-surface-variant">
              {htmlGenerado}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
