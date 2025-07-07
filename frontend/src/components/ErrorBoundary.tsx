import { Component, ReactNode } from 'react';

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
  
  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    // Vous pouvez envoyer l'erreur à un service de monitoring ici
  }
  
  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="error-container">
            <div className="error-content">
              <h2>⚠️ Une erreur est survenue</h2>
              <p>{this.state.error?.message}</p>
              <button 
                onClick={() => this.setState({ hasError: false, error: null })}
                className="retry-button"
              >
                Réessayer
              </button>
            </div>
          </div>
        )
      );
    }
    
    return this.props.children;
  }
} 