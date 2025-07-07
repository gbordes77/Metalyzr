import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTournaments, useArchetypes } from '../../hooks/useApi';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorMessage } from '../../components/ui/ErrorMessage';
import { Card } from '../../components/ui/Card';
import { 
  ArrowLeft, 
  Database, 
  Download, 
  Play, 
  Settings, 
  TrendingUp, 
  Users, 
  Activity,
  RefreshCw
} from 'lucide-react';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const { 
    data: tournaments, 
    loading: tournamentsLoading, 
    error: tournamentsError,
    refetch: refetchTournaments
  } = useTournaments({ limit: 10 });
  
  const { 
    data: archetypes, 
    loading: archetypesLoading, 
    error: archetypesError,
    refetch: refetchArchetypes
  } = useArchetypes();

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([refetchTournaments(), refetchArchetypes()]);
    } finally {
      setIsRefreshing(false);
    }
  };

  const totalDecks = archetypes?.reduce((sum, archetype) => sum + archetype.deck_count, 0) || 0;
  const activeArchetypes = archetypes?.filter(a => a.deck_count > 0).length || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="h-5 w-5 mr-1" />
                Retour au Dashboard
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Administration
                </h1>
                <p className="text-gray-600 mt-2">
                  Gestion et monitoring de Metalyzr
                </p>
              </div>
            </div>
            
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              Actualiser
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-center">
              <Database className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tournois</p>
                <p className="text-2xl font-bold text-gray-900">
                  {tournaments?.length || 0}
                </p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Archétypes actifs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {activeArchetypes}
                </p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center">
              <Users className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total decks</p>
                <p className="text-2xl font-bold text-gray-900">
                  {totalDecks}
                </p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Statut</p>
                <p className="text-lg font-semibold text-green-600">
                  En ligne
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Actions principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card 
            title="Scraping de Données"
            subtitle="Lancer le scraping des tournois"
          >
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Collecter les dernières données de tournois depuis MTGTop8
              </p>
              <button className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                <Play className="h-4 w-4 mr-2" />
                Lancer le Scraping
              </button>
            </div>
          </Card>
          
          <Card 
            title="Export des Données"
            subtitle="Télécharger les données"
          >
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Exporter les données de tournois et archétypes
              </p>
              <button className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                <Download className="h-4 w-4 mr-2" />
                Exporter CSV
              </button>
            </div>
          </Card>
          
          <Card 
            title="Configuration"
            subtitle="Paramètres système"
          >
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Configurer les archétypes et règles de détection
              </p>
              <button className="w-full flex items-center justify-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                <Settings className="h-4 w-4 mr-2" />
                Paramètres
              </button>
            </div>
          </Card>
        </div>

        {/* Tournois récents */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card 
            title="Tournois Récents"
            subtitle="Derniers tournois ajoutés"
          >
            {tournamentsLoading ? (
              <LoadingSpinner className="h-32" />
            ) : tournamentsError ? (
              <ErrorMessage message={tournamentsError} onRetry={refetchTournaments} />
            ) : tournaments && tournaments.length > 0 ? (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {tournaments.slice(0, 5).map(tournament => (
                  <div 
                    key={tournament.id}
                    className="flex justify-between items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {tournament.name}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {tournament.format} • {tournament.total_players} joueurs
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      tournament.is_complete 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-orange-100 text-orange-800'
                    }`}>
                      {tournament.is_complete ? 'Terminé' : 'En cours'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Aucun tournoi trouvé</p>
              </div>
            )}
          </Card>

          {/* Archétypes populaires */}
          <Card 
            title="Archétypes Populaires"
            subtitle="Top archétypes par nombre de decks"
          >
            {archetypesLoading ? (
              <LoadingSpinner className="h-32" />
            ) : archetypesError ? (
              <ErrorMessage message={archetypesError} onRetry={refetchArchetypes} />
            ) : archetypes && archetypes.length > 0 ? (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {archetypes
                  .filter(archetype => archetype.deck_count > 0)
                  .sort((a, b) => b.deck_count - a.deck_count)
                  .slice(0, 5)
                  .map(archetype => (
                    <div 
                      key={archetype.id}
                      className="flex justify-between items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {archetype.name}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {archetype.category} • {archetype.format}
                        </p>
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {archetype.deck_count} decks
                      </span>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Aucun archétype trouvé</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 