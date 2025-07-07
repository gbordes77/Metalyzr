import { useState, useEffect, useCallback } from 'react';
import { fetchAPI, APIError } from '../utils/api/fetchWrapper';

interface UseAPIDataOptions {
  autoFetch?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: APIError) => void;
  showNotifications?: boolean;
}

export function useAPIData<T = any>(
  endpoint: string,
  options: UseAPIDataOptions = {}
) {
  const {
    autoFetch = true,
    onSuccess,
    onError,
    showNotifications = true
  } = options;
  
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState<APIError | null>(null);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchAPI(endpoint);
      setData(result.data || result);
      onSuccess?.(result);
    } catch (err) {
      const apiError = err as APIError;
      setError(apiError);
      
      if (showNotifications) {
        console.error('API Error:', apiError.message || 'Erreur de chargement des données');
      }
      
      onError?.(apiError);
    } finally {
      setLoading(false);
    }
  }, [endpoint, onSuccess, onError, showNotifications]);
  
  useEffect(() => {
    if (autoFetch) {
      fetchData();
    }
  }, [autoFetch, fetchData]);
  
  return {
    data,
    loading,
    error,
    refetch: fetchData,
    isError: !!error,
    isSuccess: !loading && !error && data !== null
  };
} 