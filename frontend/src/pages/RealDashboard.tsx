import React from 'react';
import { api, Stats, Tournament, Archetype } from '../api/realAPI';
import { useRealData } from '../hooks/useRealData';

const RealDashboard: React.FC = () => {
  // Données réelles sans fallback
  const { data: stats, loading: statsLoading, error: statsError, refetch: refetchStats } = 
    useRealData<Stats>(() => api.getStats());
  
  const { data: tournaments, loading: tournamentsLoading, error: tournamentsError, refetch: refetchTournaments } = 
    useRealData<Tournament[]>(() => api.getTournaments());
  
  const { data: archetypes, loading: archetypesLoading, error: archetypesError, refetch: refetchArchetypes } = 
    useRealData<Archetype[]>(() => api.getArchetypes());

  const { data: health, loading: healthLoading, error: healthError, refetch: refetchHealth } = 
    useRealData<{ status: string; timestamp: string }>(() => api.checkHealth());

  const handleRefreshAll = () => {
    refetchStats();
    refetchTournaments();
    refetchArchetypes();
    refetchHealth();
  };

  const isSystemOnline = health?.status === 'healthy' && !healthError;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Metalyzr Dashboard</h1>
            <p className="text-gray-600 mt-2">Données réelles du système de métaanalyse MTG</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              isSystemOnline 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {healthLoading ? 'Vérification...' : isSystemOnline ? 'Système En Ligne' : 'Système Hors Ligne'}
            </div>
            <button
              onClick={handleRefreshAll}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Actualiser
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Tournois"
            value={stats?.tournaments}
            loading={statsLoading}
            error={statsError}
            icon="🏆"
          />
          <StatCard
            title="Archétypes"
            value={stats?.archetypes}
            loading={statsLoading}
            error={statsError}
            icon="🎯"
          />
          <StatCard
            title="Decks Analysés"
            value={stats?.decks}
            loading={statsLoading}
            error={statsError}
            icon="🃏"
          />
        </div>

        {/* Data Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Tournaments Section */}
          <DataSection
            title="Tournois Récents"
            loading={tournamentsLoading}
            error={tournamentsError}
            onRetry={refetchTournaments}
          >
            {tournaments && tournaments.length > 0 ? (
              <div className="space-y-3">
                {tournaments.slice(0, 5).map((tournament) => (
                  <div key={tournament.id} className="border-l-4 border-blue-500 pl-4 py-2">
                    <h4 className="font-medium text-gray-900">{tournament.name}</h4>
                    <p className="text-sm text-gray-600">
                      {tournament.format} • {tournament.participants} participants • {tournament.date}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Aucun tournoi trouvé</p>
            )}
          </DataSection>

          {/* Archetypes Section */}
          <DataSection
            title="Archétypes Populaires"
            loading={archetypesLoading}
            error={archetypesError}
            onRetry={refetchArchetypes}
          >
            {archetypes && archetypes.length > 0 ? (
              <div className="space-y-3">
                {archetypes.slice(0, 5).map((archetype) => (
                  <div key={archetype.id} className="border-l-4 border-green-500 pl-4 py-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">{archetype.name}</h4>
                        <p className="text-sm text-gray-600">{archetype.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-green-600">{archetype.winRate}% WR</div>
                        <div className="text-xs text-gray-500">{archetype.popularity}% META</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">Aucun archétype trouvé</p>
            )}
          </DataSection>
        </div>

        {/* System Info */}
        {stats && (
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Informations Système</h3>
            <p className="text-sm text-gray-600">
              Dernière mise à jour: {stats.lastUpdate}
            </p>
            <p className="text-sm text-gray-600">
              Base de données: {stats.tournaments} tournois, {stats.archetypes} archétypes, {stats.decks} decks
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Composant StatCard
interface StatCardProps {
  title: string;
  value?: number;
  loading: boolean;
  error?: string | null;
  icon: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, loading, error, icon }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center">
      <div className="text-2xl mr-3">{icon}</div>
      <div>
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        {loading ? (
          <div className="text-2xl font-bold text-gray-400">Chargement...</div>
        ) : error ? (
          <div className="text-2xl font-bold text-red-500">Erreur</div>
        ) : (
          <div className="text-2xl font-bold text-gray-900">{value || 0}</div>
        )}
      </div>
    </div>
  </div>
);

// Composant DataSection
interface DataSectionProps {
  title: string;
  loading: boolean;
  error?: string | null;
  onRetry: () => void;
  children: React.ReactNode;
}

const DataSection: React.FC<DataSectionProps> = ({ title, loading, error, onRetry, children }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex justify-between items-center mb-4">
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      {error && (
        <button
          onClick={onRetry}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Réessayer
        </button>
      )}
    </div>
    
    {loading ? (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    ) : error ? (
      <div className="text-center py-8">
        <p className="text-red-600 mb-2">Erreur: {error}</p>
        <button
          onClick={onRetry}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Réessayer
        </button>
      </div>
    ) : (
      children
    )}
  </div>
);

export default RealDashboard; 