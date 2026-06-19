import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useEncuentro, useActualizarInstancia, useGenerarHtml } from '../hooks/useEncuentros';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Spinner } from '@/shared/components/Spinner';
import type { InstanciaEstado } from '../types';
import { Button } from '@/shared/components/ds';

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
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>{encuentro.titulo}</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>{encuentro.materia_nombre}</p>
        </div>
      </div>

      <div className="space-y-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
        <div className="grid grid-cols-2 gap-4">
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
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={!dirty || actualizar.isPending}
            >
              Guardar Cambios
            </Button>
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
        <Button
          variant="secondary"
          icon="code"
          onClick={handleGenerarHtml}
          disabled={generarHtml.isPending}
        >
          Generar contenido para el aula virtual
        </Button>

        {htmlGenerado && (
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-label-sm text-on-surface-variant">HTML generado:</p>
              <Button
                variant="ghost"
                size="sm"
                icon={copied ? 'check' : 'content_copy'}
                onClick={handleCopyHtml}
              >
                {copied ? 'Copiado' : 'Copiar'}
              </Button>
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
