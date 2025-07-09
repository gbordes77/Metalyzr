import { useState, useCallback, useEffect } from 'react';

type ApiStatus = 'idle' | 'loading' | 'success' | 'error';

interface UseApiState<T> {
  data: T | null;
  status: ApiStatus;
  error: string | null;
  execute: (...args: any[]) => Promise<void>;
}

/**
 * A generic hook for making API calls.
 * @param apiFunc The API function to call. This function is expected to return a promise.
 * @param immediate Whether to execute the API call immediately on component mount. Defaults to true.
 */
export function useGenericApi<T>(
  apiFunc: (...args: any[]) => Promise<T>,
  immediate = true
): UseApiState<T> {
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (...args: any[]) => {
      setStatus('loading');
      setError(null);
      try {
        const result = await apiFunc(...args);
        setData(result);
        setStatus('success');
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
        setError(errorMessage);
        setStatus('error');
        // Re-throw the error if the consumer wants to handle it as well
        throw err;
      }
    },
    [apiFunc]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { data, status, error, execute };
} 