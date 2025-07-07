import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { useAPIData } from '../hooks/useAPIData';
import { fetchAPI } from '../utils/api/fetchWrapper';

// Mock fetchAPI
jest.mock('../utils/api/fetchWrapper');
const mockFetchAPI = fetchAPI as jest.MockedFunction<typeof fetchAPI>;

describe('useAPIData Hook Tests', () => {
  beforeEach(() => {
    mockFetchAPI.mockClear();
  });

  describe('Auto-fetch behavior', () => {
    test('should auto-fetch data on mount by default', async () => {
      const mockData = { tournaments: 42 };
      mockFetchAPI.mockResolvedValue(mockData);

      const { result } = renderHook(() => useAPIData('/api/stats'));

      expect(result.current.loading).toBe(true);
      expect(result.current.data).toBeNull();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockData);
      expect(result.current.isSuccess).toBe(true);
      expect(mockFetchAPI).toHaveBeenCalledWith('/api/stats');
    });

    test('should not auto-fetch when autoFetch is false', () => {
      mockFetchAPI.mockResolvedValue({});

      const { result } = renderHook(() => 
        useAPIData('/api/stats', { autoFetch: false })
      );

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeNull();
      expect(mockFetchAPI).not.toHaveBeenCalled();
    });
  });

  describe('Success handling', () => {
    test('should call onSuccess callback with data', async () => {
      const mockData = { archetypes: 15 };
      const onSuccess = jest.fn();
      mockFetchAPI.mockResolvedValue(mockData);

      renderHook(() => useAPIData('/api/archetypes', { onSuccess }));

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalledWith(mockData);
      });
    });

    test('should extract data from result.data if present', async () => {
      const mockResponse = { data: { tournaments: 100 }, meta: { count: 1 } };
      mockFetchAPI.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useAPIData('/api/tournaments'));

      await waitFor(() => {
        expect(result.current.data).toEqual({ tournaments: 100 });
      });
    });

    test('should use full result if no data property', async () => {
      const mockResponse = { tournaments: 50 };
      mockFetchAPI.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useAPIData('/api/stats'));

      await waitFor(() => {
        expect(result.current.data).toEqual({ tournaments: 50 });
      });
    });
  });

  describe('Error handling', () => {
    test('should handle API errors', async () => {
      const mockError = new Error('Network error');
      const onError = jest.fn();
      mockFetchAPI.mockRejectedValue(mockError);

      const { result } = renderHook(() => 
        useAPIData('/api/stats', { onError })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe(mockError);
      expect(result.current.isError).toBe(true);
      expect(result.current.isSuccess).toBe(false);
      expect(onError).toHaveBeenCalledWith(mockError);
    });

    test('should log errors when showNotifications is true', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      const mockError = new Error('API Error');
      mockFetchAPI.mockRejectedValue(mockError);

      renderHook(() => 
        useAPIData('/api/stats', { showNotifications: true })
      );

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('API Error:', 'API Error');
      });

      consoleSpy.mockRestore();
    });

    test('should not log errors when showNotifications is false', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      const mockError = new Error('API Error');
      mockFetchAPI.mockRejectedValue(mockError);

      renderHook(() => 
        useAPIData('/api/stats', { showNotifications: false })
      );

      await waitFor(() => {
        expect(result.current.error).toBe(mockError);
      });

      expect(consoleSpy).not.toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('Refetch functionality', () => {
    test('should refetch data when refetch is called', async () => {
      const mockData1 = { tournaments: 10 };
      const mockData2 = { tournaments: 20 };
      
      mockFetchAPI
        .mockResolvedValueOnce(mockData1)
        .mockResolvedValueOnce(mockData2);

      const { result } = renderHook(() => useAPIData('/api/stats'));

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.data).toEqual(mockData1);
      });

      // Trigger refetch
      result.current.refetch();

      await waitFor(() => {
        expect(result.current.data).toEqual(mockData2);
      });

      expect(mockFetchAPI).toHaveBeenCalledTimes(2);
    });

    test('should set loading state during refetch', async () => {
      const mockData = { tournaments: 10 };
      mockFetchAPI.mockResolvedValue(mockData);

      const { result } = renderHook(() => useAPIData('/api/stats'));

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Trigger refetch
      result.current.refetch();

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });
  });

  describe('Loading states', () => {
    test('should show loading initially when auto-fetching', () => {
      mockFetchAPI.mockImplementation(() => new Promise(() => {})); // Never resolves

      const { result } = renderHook(() => useAPIData('/api/stats'));

      expect(result.current.loading).toBe(true);
      expect(result.current.isSuccess).toBe(false);
      expect(result.current.isError).toBe(false);
    });

    test('should clear error state on successful refetch', async () => {
      const mockError = new Error('Network error');
      const mockData = { tournaments: 42 };

      mockFetchAPI
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockData);

      const { result } = renderHook(() => useAPIData('/api/stats'));

      // Wait for error
      await waitFor(() => {
        expect(result.current.error).toBe(mockError);
      });

      // Refetch should clear error
      result.current.refetch();

      await waitFor(() => {
        expect(result.current.error).toBeNull();
        expect(result.current.data).toEqual(mockData);
      });
    });
  });

  describe('TypeScript generics', () => {
    test('should work with typed data', async () => {
      interface StatsData {
        tournaments: number;
        archetypes: number;
      }

      const mockData: StatsData = { tournaments: 42, archetypes: 15 };
      mockFetchAPI.mockResolvedValue(mockData);

      const { result } = renderHook(() => useAPIData<StatsData>('/api/stats'));

      await waitFor(() => {
        expect(result.current.data?.tournaments).toBe(42);
        expect(result.current.data?.archetypes).toBe(15);
      });
    });
  });
}); 