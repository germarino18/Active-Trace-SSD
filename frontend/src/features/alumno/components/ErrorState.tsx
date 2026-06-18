interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = 'Error al cargar datos', onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <span className="material-symbols-outlined text-[48px] text-error mb-3">error</span>
      <p className="text-body-md text-on-surface-variant mb-4">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
