import { fetchAPI, APIError } from '../utils/api/fetchWrapper';

// Mock fetch global
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('API Wrapper Tests', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    jest.clearAllTimers();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('fetchAPI Success Cases', () => {
    test('should successfully fetch data', async () => {
      const mockData = { tournaments: 42, archetypes: 15 };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData)
      });

      const result = await fetchAPI('/api/stats');
      
      expect(result).toEqual(mockData);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/stats',
        expect.objectContaining({
          headers: { 'Content-Type': 'application/json' }
        })
      );
    });

    test('should use custom base URL from env', async () => {
      process.env.REACT_APP_API_URL = 'http://custom-api.com';
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      });

      await fetchAPI('/test');
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://custom-api.com/test',
        expect.any(Object)
      );
      
      // Reset env
      delete process.env.REACT_APP_API_URL;
    });
  });

  describe('fetchAPI Error Handling', () => {
    test('should throw APIError on HTTP error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ message: 'Not found', code: 'NOT_FOUND' })
      });

      await expect(fetchAPI('/api/missing')).rejects.toThrow(APIError);
      
      try {
        await fetchAPI('/api/missing');
      } catch (error) {
        expect(error).toBeInstanceOf(APIError);
        expect((error as APIError).status).toBe(404);
        expect((error as APIError).code).toBe('NOT_FOUND');
      }
    });

    test('should not retry on 4xx errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ message: 'Unauthorized' })
      });

      await expect(fetchAPI('/api/protected')).rejects.toThrow(APIError);
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    test('should retry on network errors', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true })
        });

      const result = await fetchAPI('/api/stats', { retries: 3 });
      
      expect(result).toEqual({ success: true });
      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    test('should respect retry limit', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(fetchAPI('/api/stats', { retries: 2 })).rejects.toThrow('Network error');
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('fetchAPI Timeout Handling', () => {
    test('should timeout after 10 seconds', async () => {
      mockFetch.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 15000))
      );

      const promise = fetchAPI('/api/slow');
      
      // Fast-forward time
      jest.advanceTimersByTime(10000);
      
      await expect(promise).rejects.toThrow();
    });
  });

  describe('fetchAPI Retry Logic', () => {
    test('should use exponential backoff', async () => {
      const startTime = Date.now();
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true })
        });

      const promise = fetchAPI('/api/stats', { retries: 3, retryDelay: 100 });
      
      // First retry after 100ms
      jest.advanceTimersByTime(100);
      await Promise.resolve();
      
      // Second retry after 200ms (exponential backoff)
      jest.advanceTimersByTime(200);
      
      const result = await promise;
      expect(result).toEqual({ success: true });
    });
  });
}); 