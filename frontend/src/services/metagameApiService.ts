// Define the base URL for the API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// --- Response Types ---
// These should match the data structures returned by the FastAPI backend.

export interface MetagameShareData {
  archetype: string;
  count: number;
  share: number;
}

export interface WinrateConfidenceData {
  archetype: string;
  winrate: number;
  ci_lower: number;
  ci_upper: number;
}

export interface MatchupMatrixData {
  archetypes: string[];
  matrix: number[][];
}

export interface AnalysisResponse<T> {
  format: string;
  start_date: string;
  end_date: string;
  analysis_type: string;
  data: T;
}


// --- Fetch Wrapper ---

async function fetchWrapper<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API fetch error:', error);
    throw error;
  }
}

// --- API Service Functions ---

export const metagameApiService = {
  /**
   * Triggers a background task to update the metagame data.
   */
  triggerMetagameUpdate: (): Promise<{ message: string }> => {
    return fetchWrapper('/api/metagame/update', { method: 'POST' });
  },

  /**
   * Fetches the metagame share for a given format.
   * @param format The game format (e.g., 'Modern', 'Standard').
   * @param days The number of past days to include in the analysis.
   */
  getMetagameShare: (format: string, days: number): Promise<AnalysisResponse<MetagameShareData[]>> => {
    return fetchWrapper(`/api/metagame/analysis/metagame_share/${format}?days=${days}`);
  },

  /**
   * Fetches the winrate confidence intervals for a given format.
   * @param format The game format.
   * @param days The number of past days to include in the analysis.
   */
  getWinrateConfidence: (format: string, days: number): Promise<AnalysisResponse<WinrateConfidenceData[]>> => {
    return fetchWrapper(`/api/metagame/analysis/winrate_confidence/${format}?days=${days}`);
  },

  /**
   * Fetches the matchup matrix for a given format.
   * @param format The game format.
   * @param days The number of past days to include in the analysis.
   */
  getMatchupMatrix: (format: string, days: number): Promise<AnalysisResponse<MatchupMatrixData>> => {
    return fetchWrapper(`/api/metagame/analysis/matchup_matrix/${format}?days=${days}`);
  },
}; 