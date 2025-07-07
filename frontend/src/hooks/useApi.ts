import { useState, useEffect, useCallback } from 'react';
import { apiService, Tournament, Archetype, TournamentDetails, TournamentMetagame, Deck } from '../services/api';

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useTournaments(params?: {
  format?: string;
  limit?: number;
  offset?: number;
}): UseApiState<Tournament[]> {
  const [data, setData] = useState<Tournament[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const tournaments = await apiService.getTournaments(params);
      setData(tournaments);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [params?.format, params?.limit, params?.offset]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

export function useTournament(id: number): UseApiState<TournamentDetails> {
  const [data, setData] = useState<TournamentDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const tournament = await apiService.getTournament(id);
      setData(tournament);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [fetchData, id]);

  return { data, loading, error, refetch: fetchData };
}

export function useTournamentMetagame(id: number): UseApiState<TournamentMetagame> {
  const [data, setData] = useState<TournamentMetagame | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const metagame = await apiService.getTournamentMetagame(id);
      setData(metagame);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [fetchData, id]);

  return { data, loading, error, refetch: fetchData };
}

export function useArchetypes(params?: {
  format?: string;
  category?: string;
}): UseApiState<Archetype[]> {
  const [data, setData] = useState<Archetype[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const archetypes = await apiService.getArchetypes(params);
      setData(archetypes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [params?.format, params?.category]);

  return { data, loading, error, refetch: fetchData };
}

export function useFormats(): UseApiState<string[]> {
  const [data, setData] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const formats = await apiService.getFormats();
      setData(formats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

export function useCategories(): UseApiState<string[]> {
  const [data, setData] = useState<string[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const categories = await apiService.getCategories();
      setData(categories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

export function useTournamentDecks(
  tournamentId: number,
  params?: {
    archetype?: string;
    limit?: number;
  }
): UseApiState<Deck[]> {
  const [data, setData] = useState<Deck[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const decks = await apiService.getTournamentDecks(tournamentId, params);
      setData(decks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [tournamentId, params?.archetype, params?.limit]);

  useEffect(() => {
    if (tournamentId) {
      fetchData();
    }
  }, [fetchData, tournamentId]);

  return { data, loading, error, refetch: fetchData };
} 