import { useNavigate } from 'react-router-dom';
import { EmptyState, Button } from '@/shared/components/ds';

export function ForbiddenPage() {
  const navigate = useNavigate();
  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <EmptyState
        code="403"
        title="Sin permisos"
        message="No tenés acceso a esta sección. Si creés que es un error, contactá a tu administrador."
        action={<Button variant="secondary" icon="home" onClick={() => navigate('/')}>Volver al inicio</Button>}
      />
    </div>
  );
}
