// API réelle simple pour le MVP
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Interface pour les données réelles
export interface Tournament {
  id: number;
  name: string;
  format: string;
  date: string;
  participants: number;
}

export interface Archetype {
  id: number;
  name: string;
  description: string;
  winRate: number;
  popularity: number;
}

export interface Stats {
  tournaments: number;
  archetypes: number;
  decks: number;
  lastUpdate: string;
}

// API réelle avec gestion d'erreurs simple
class RealAPI {
  private async request<T>(endpoint: string): Promise<T> {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      throw error;
    }
  }

  // Méthodes API simples
  async getStats(): Promise<Stats> {
    return this.request<Stats>('/api/stats');
  }

  async getTournaments(): Promise<Tournament[]> {
    return this.request<Tournament[]>('/api/tournaments');
  }

  async getArchetypes(): Promise<Archetype[]> {
    return this.request<Archetype[]>('/api/archetypes');
  }

  async checkHealth(): Promise<{ status: string; timestamp: string }> {
    return this.request<{ status: string; timestamp: string }>('/health');
  }
}

export const api = new RealAPI(); 