import { Component, type ReactNode, type ErrorInfo } from 'react';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
          <EmptyState message="Ocurrió un error inesperado" icon="error" />
          <p className="text-body-sm text-on-surface-variant max-w-md">
            {this.state.error?.message || 'Algo salió mal. Intentá de nuevo.'}
          </p>
          <Button type="button" variant="primary" onClick={this.handleRetry}>
            Reintentar
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
