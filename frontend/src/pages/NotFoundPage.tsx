import { useNavigate } from 'react-router-dom';
import { EmptyState, Button } from '@/shared/components/ds';

export function NotFoundPage() {
  const navigate = useNavigate();
  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <EmptyState
        code="404"
        title="Página no encontrada"
        message="La ruta que buscás no existe o fue movida. Verificá la dirección e intentá de nuevo."
        action={<Button variant="secondary" icon="home" onClick={() => navigate('/dashboard')}>Volver al inicio</Button>}
      />
    </div>
  );
}
