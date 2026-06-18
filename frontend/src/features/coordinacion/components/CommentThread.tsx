import { useState } from 'react';
import type { ComentarioTarea } from '../types';

interface CommentThreadProps {
  comentarios: ComentarioTarea[];
  onAddComment: (contenido: string) => Promise<void>;
}

export function CommentThread({ comentarios, onAddComment }: CommentThreadProps) {
  const [contenido, setContenido] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!contenido.trim()) return;
    setIsSubmitting(true);
    try {
      await onAddComment(contenido.trim());
      setContenido('');
    } finally {
      setIsSubmitting(false);
    }
  };

  const sorted = [...comentarios].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );

  return (
    <div className="space-y-4">
      <h3 className="font-medium text-on-surface">Comentarios</h3>

      <div className="space-y-2">
        <textarea
          value={contenido}
          onChange={(e) => setContenido(e.target.value)}
          placeholder="Agregá un comentario..."
          rows={3}
          className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
        />
        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!contenido.trim() || isSubmitting}
            className="inline-flex items-center gap-1 rounded-lg bg-primary px-4 py-1.5 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting ? 'Enviando...' : 'Comentar'}
          </button>
        </div>
      </div>

      {sorted.length === 0 ? (
        <p className="text-body-sm text-on-surface-variant">Sin comentarios aún.</p>
      ) : (
        <div className="space-y-3">
          {sorted.map((comentario) => (
            <div
              key={comentario.id}
              className="rounded-lg border border-outline-variant bg-surface-container-lowest p-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-label-sm font-medium text-on-surface">
                  {comentario.autor_nombre}
                </span>
                <span className="text-label-xs text-on-surface-variant">
                  {new Date(comentario.created_at).toLocaleString('es-AR')}
                </span>
              </div>
              <p className="mt-1 text-body-sm text-on-surface-variant">{comentario.contenido}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
