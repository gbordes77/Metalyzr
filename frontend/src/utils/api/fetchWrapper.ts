interface FetchOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
}

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function fetchAPI(
  endpoint: string, 
  options: FetchOptions = {}
): Promise<any> {
  const { retries = 3, retryDelay = 1000, ...fetchOptions } = options;
  const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const url = `${baseURL}${endpoint}`;
  
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
      
      const response = await fetch(url, {
        ...fetchOptions,
        headers: {
          'Content-Type': 'application/json',
          ...fetchOptions.headers,
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      // Gérer les réponses non-OK
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `HTTP ${response.status}`,
          response.status,
          errorData.code
        );
      }
      
      return await response.json();
      
    } catch (error) {
      lastError = error as Error;
      
      // Ne pas retry sur certaines erreurs
      if (error instanceof APIError && [400, 401, 403, 404].includes(error.status!)) {
        throw error;
      }
      
      // Attendre avant de retry (backoff exponentiel)
      if (attempt < retries - 1) {
        await new Promise(resolve => 
          setTimeout(resolve, retryDelay * Math.pow(2, attempt))
        );
      }
    }
  }
  
  throw lastError || new APIError('Erreur de connexion au serveur');
} 