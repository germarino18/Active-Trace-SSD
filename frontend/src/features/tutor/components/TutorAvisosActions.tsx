import { useConfirmarAck } from '@/features/coordinacion/hooks/useAvisos';

interface TutorAvisosActionsProps {
  avisoId: string;
  requiereAck: boolean;
  userAcked: boolean;
}

export function TutorAvisosActions({ avisoId, requiereAck, userAcked }: TutorAvisosActionsProps) {
  const confirmarAck = useConfirmarAck();

  if (!requiereAck) return null;

  if (userAcked) {
    return (
      <span className="text-label-xs text-success">✓ Confirmado</span>
    );
  }

  return (
    <button
      type="button"
      onClick={() => confirmarAck.mutate(avisoId)}
      disabled={confirmarAck.isPending}
      className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-2.5 py-1 text-label-xs font-medium text-primary transition-colors hover:bg-primary/20 disabled:opacity-50"
    >
      {confirmarAck.isPending ? 'Confirmando...' : 'Confirmar'}
    </button>
  );
}
