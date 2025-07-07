import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface Stats {
  tournaments: number;
  archetypes: number;
  decks: number;
}

interface AdminState {
  stats: Stats;
  status: 'online' | 'offline' | 'degraded' | 'checking';
  lastUpdate: Date | null;
  errors: string[];
  
  // Actions
  setStats: (stats: Partial<Stats>) => void;
  setStatus: (status: AdminState['status']) => void;
  addError: (error: string) => void;
  clearErrors: () => void;
  updateLastUpdate: () => void;
}

export const useAdminStore = create<AdminState>()(
  devtools(
    persist(
      (set) => ({
        stats: {
          tournaments: 0,
          archetypes: 0,
          decks: 0
        },
        status: 'checking',
        lastUpdate: null,
        errors: [],
        
        setStats: (newStats) => 
          set((state) => ({ 
            stats: { ...state.stats, ...newStats } 
          })),
          
        setStatus: (status) => set({ status }),
        
        addError: (error) => 
          set((state) => ({ 
            errors: [...state.errors, error].slice(-10) // Garder les 10 dernières erreurs
          })),
          
        clearErrors: () => set({ errors: [] }),
        
        updateLastUpdate: () => set({ lastUpdate: new Date() })
      }),
      {
        name: 'metalyzr-admin',
        partialize: (state) => ({ 
          stats: state.stats,
          lastUpdate: state.lastUpdate 
        })
      }
    )
  )
); 