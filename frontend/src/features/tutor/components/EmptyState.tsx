interface EmptyStateProps {
  message: string;
  icon?: string;
}

export function EmptyState({ message, icon = 'info' }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <span className="material-symbols-outlined text-[48px] text-outline mb-3">{icon}</span>
      <p className="text-body-md text-on-surface-variant">{message}</p>
    </div>
  );
}
