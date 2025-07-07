const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Tournament {
  id: number;
  name: string;
  format: string;
  date: string;
  location: string;
  total_players: number;
  rounds: number;
  is_complete: boolean;
}

export interface TournamentDetails extends Tournament {
  organizer: string;
  tournament_type: string;
  source_site: string;
  decks_count: number;
  created_at: string;
}

export interface Archetype {
  id: number;
  name: string;
  format: string;
  category: string;
  description: string;
  color_identity: string;
  key_cards: string[];
  deck_count: number;
}

export interface ArchetypeDetails extends Archetype {
  variations: any;
  created_at: string;
  statistics: {
    total_decks: number;
    avg_wins: number;
    avg_losses: number;
    best_position: number | null;
  };
}

export interface Deck {
  id: number;
  player_name: string;
  position: number | null;
  wins: number;
  losses: number;
  draws: number;
  archetype: string;
  color_identity: string;
  total_cards: number;
}

export interface MetagameEntry {
  archetype: string;
  category: string;
  deck_count: number;
  meta_share: number;
  avg_wins: number;
  best_position: number | null;
}

export interface TournamentMetagame {
  tournament_id: number;
  tournament_name: string;
  total_decks: number;
  metagame: MetagameEntry[];
}

class ApiService {
  private async fetchApi<T>(endpoint: string): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.fetchApi('/health');
  }

  // Tournaments
  async getTournaments(params?: {
    format?: string;
    limit?: number;
    offset?: number;
  }): Promise<Tournament[]> {
    const searchParams = new URLSearchParams();
    if (params?.format) searchParams.set('format', params.format);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());
    
    const query = searchParams.toString();
    return this.fetchApi(`/api/tournaments/${query ? `?${query}` : ''}`);
  }

  async getTournament(id: number): Promise<TournamentDetails> {
    return this.fetchApi(`/api/tournaments/${id}/`);
  }

  async getTournamentMetagame(id: number): Promise<TournamentMetagame> {
    return this.fetchApi(`/api/tournaments/${id}/metagame/`);
  }

  async getTournamentDecks(id: number, params?: {
    archetype?: string;
    limit?: number;
  }): Promise<Deck[]> {
    const searchParams = new URLSearchParams();
    if (params?.archetype) searchParams.set('archetype', params.archetype);
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    
    const query = searchParams.toString();
    return this.fetchApi(`/api/tournaments/${id}/decks/${query ? `?${query}` : ''}`);
  }

  // Archetypes
  async getArchetypes(params?: {
    format?: string;
    category?: string;
  }): Promise<Archetype[]> {
    const searchParams = new URLSearchParams();
    if (params?.format) searchParams.set('format', params.format);
    if (params?.category) searchParams.set('category', params.category);
    
    const query = searchParams.toString();
    return this.fetchApi(`/api/archetypes/${query ? `?${query}` : ''}`);
  }

  async getArchetype(id: number): Promise<ArchetypeDetails> {
    return this.fetchApi(`/api/archetypes/${id}/`);
  }

  async getArchetypeDecks(id: number, limit?: number): Promise<Deck[]> {
    const query = limit ? `?limit=${limit}` : '';
    return this.fetchApi(`/api/archetypes/${id}/decks/${query}`);
  }

  async getFormats(): Promise<string[]> {
    // Extraire les formats depuis les archétypes
    const archetypes = await this.getArchetypes();
    return Array.from(new Set(archetypes.map(a => a.format)));
  }

  async getCategories(): Promise<string[]> {
    // Extraire les catégories depuis les archétypes
    const archetypes = await this.getArchetypes();
    return Array.from(new Set(archetypes.map(a => a.category)));
  }
}

export const apiService = new ApiService(); 