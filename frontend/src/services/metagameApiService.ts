import { fetchWrapper, API_BASE_URL } from '../utils/api/fetchWrapper';

// --- Response Type ---
// This should match the data structure returned by the FastAPI backend.
// This is defined in our backend/schemas.py
export interface MetagameShare {
    archetype: string;
    deck_count: int;
    prevalence: float;
}

// --- API Service Functions ---

export const metagameApiService = {
  /**
   * Fetches the metagame share for a given format.
   * @param formatName The game format (e.g., 'Modern', 'Standard').
   * @param startDate The start date for the analysis (YYYY-MM-DD).
   */
  getMetagameShare: (formatName: string, startDate?: string): Promise<MetagameShare[]> => {
    const params = new URLSearchParams({ format_name: formatName });
    if (startDate) {
      params.append('start_date', startDate);
    }
    return fetchWrapper(`/api/v1/metagame/?${params.toString()}`);
  },
}; 