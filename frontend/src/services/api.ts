const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiService = {
  get: async (endpoint: string) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  },
  post: async (endpoint: string, body: any) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
};

export const metagameApiService = {
  getMetagameShare: (format: string, days: number) => {
    return apiService.get(`/metagame/analysis/metagame_share/${format}?days=${days}`);
  },
  getWinrateConfidence: (format: string, days: number) => {
    return apiService.get(`/metagame/analysis/winrate_confidence/${format}?days=${days}`);
  },
  getMatchupMatrix: (format: string, days: number) => {
    return apiService.get(`/metagame/analysis/matchup_matrix/${format}?days=${days}`);
  },
  getSupportedFormats: (): Promise<string[]> => {
    return apiService.get('/metagame/formats');
  },
  populateDatabase: (format?: string, startDate?: string): Promise<{ message: string }> => {
    let url = '/metagame/populate-database';
    const params = new URLSearchParams();
    if (format) {
      params.append('format_name', format);
    }
    if (startDate) {
      params.append('start_date', startDate);
    }
    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
    return apiService.post(url, {});
  }
}; 