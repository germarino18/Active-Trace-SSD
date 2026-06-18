import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="text-center">
        <h1 className="font-headline-xl text-headline-xl font-bold text-on-surface">404</h1>
        <p className="text-body-lg text-on-surface-variant mt-2">Página no encontrada</p>
        <Link to="/dashboard" className="text-primary hover:underline mt-4 inline-block">
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
