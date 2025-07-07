import { useAdminStore } from '../store/adminStore';
import { act, renderHook } from '@testing-library/react';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Admin Store Tests', () => {
  beforeEach(() => {
    // Reset store state
    useAdminStore.setState({
      stats: { tournaments: 0, archetypes: 0, decks: 0 },
      status: 'checking',
      lastUpdate: null,
      errors: []
    });
    
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    test('should have correct initial state', () => {
      const { result } = renderHook(() => useAdminStore());
      
      expect(result.current.stats).toEqual({
        tournaments: 0,
        archetypes: 0,
        decks: 0
      });
      expect(result.current.status).toBe('checking');
      expect(result.current.lastUpdate).toBeNull();
      expect(result.current.errors).toEqual([]);
    });
  });

  describe('setStats Action', () => {
    test('should update stats partially', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.setStats({ tournaments: 42 });
      });
      
      expect(result.current.stats).toEqual({
        tournaments: 42,
        archetypes: 0,
        decks: 0
      });
    });

    test('should update multiple stats', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.setStats({
          tournaments: 100,
          archetypes: 25,
          decks: 500
        });
      });
      
      expect(result.current.stats).toEqual({
        tournaments: 100,
        archetypes: 25,
        decks: 500
      });
    });
  });

  describe('setStatus Action', () => {
    test('should update status to online', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.setStatus('online');
      });
      
      expect(result.current.status).toBe('online');
    });

    test('should update status to offline', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.setStatus('offline');
      });
      
      expect(result.current.status).toBe('offline');
    });
  });

  describe('Error Management', () => {
    test('should add error to errors array', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.addError('Test error message');
      });
      
      expect(result.current.errors).toContain('Test error message');
    });

    test('should maintain maximum 10 errors', () => {
      const { result } = renderHook(() => useAdminStore());
      
      // Add 12 errors
      act(() => {
        for (let i = 0; i < 12; i++) {
          result.current.addError(`Error ${i}`);
        }
      });
      
      expect(result.current.errors).toHaveLength(10);
      expect(result.current.errors[0]).toBe('Error 2'); // First 2 should be removed
      expect(result.current.errors[9]).toBe('Error 11');
    });

    test('should clear all errors', () => {
      const { result } = renderHook(() => useAdminStore());
      
      // Add some errors first
      act(() => {
        result.current.addError('Error 1');
        result.current.addError('Error 2');
      });
      
      expect(result.current.errors).toHaveLength(2);
      
      act(() => {
        result.current.clearErrors();
      });
      
      expect(result.current.errors).toEqual([]);
    });
  });

  describe('updateLastUpdate Action', () => {
    test('should update lastUpdate to current date', () => {
      const { result } = renderHook(() => useAdminStore());
      const beforeUpdate = new Date();
      
      act(() => {
        result.current.updateLastUpdate();
      });
      
      const afterUpdate = new Date();
      
      expect(result.current.lastUpdate).toBeInstanceOf(Date);
      expect(result.current.lastUpdate!.getTime()).toBeGreaterThanOrEqual(beforeUpdate.getTime());
      expect(result.current.lastUpdate!.getTime()).toBeLessThanOrEqual(afterUpdate.getTime());
    });
  });

  describe('Persistence', () => {
    test('should persist stats and lastUpdate to localStorage', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.setStats({ tournaments: 50 });
        result.current.updateLastUpdate();
      });
      
      // Zustand with persist should call localStorage.setItem
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'metalyzr-admin',
        expect.stringContaining('tournaments')
      );
    });
  });

  describe('State Combinations', () => {
    test('should handle complex state updates', () => {
      const { result } = renderHook(() => useAdminStore());
      
      act(() => {
        result.current.setStats({ tournaments: 75, archetypes: 20 });
        result.current.setStatus('online');
        result.current.addError('Non-critical warning');
        result.current.updateLastUpdate();
      });
      
      expect(result.current.stats.tournaments).toBe(75);
      expect(result.current.stats.archetypes).toBe(20);
      expect(result.current.status).toBe('online');
      expect(result.current.errors).toContain('Non-critical warning');
      expect(result.current.lastUpdate).toBeInstanceOf(Date);
    });
  });
}); 