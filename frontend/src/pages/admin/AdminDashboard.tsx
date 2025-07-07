import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminStore } from '../../store/adminStore';
import { useAPIData } from '../../hooks/useAPIData';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorMessage } from '../../components/ui/ErrorMessage';
import { Card } from '../../components/ui/Card';
import { ErrorBoundary } from '../../components/ErrorBoundary';
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

// Composants auxiliaires
const StatCard: React.FC<{
  icon: React.ReactNode;
  label: string;
  value: number | string;
  loading: boolean;
  color?: string;
}> = ({ icon, label, value, loading, color = 'text-gray-900' }) => (
  <Card>
    <div className="flex items-center">
      <div className="flex-shrink-0">
        {icon}
      </div>
      <div className="ml-4">
        <p className="text-sm font-medium text-gray-600">{label}</p>
        <p className={`text-2xl font-bold ${color}`}>
          {loading ? <LoadingSpinner className="h-6 w-6" /> : value}
        </p>
      </div>
    </div>
  </Card>
);

const ActionCard: React.FC<{
  title: string;
  subtitle: string;
  description: string;
  buttonText: string;
  buttonIcon: React.ReactNode;
  buttonClass: string;
  disabled?: boolean;
  onClick: () => void;
}> = ({ title, subtitle, description, buttonText, buttonIcon, buttonClass, disabled, onClick }) => (
  <Card title={title} subtitle={subtitle}>
    <div className="space-y-4">
      <p className="text-sm text-gray-600">{description}</p>
      <button 
        className={`w-full flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors ${buttonClass} ${
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        disabled={disabled}
        onClick={onClick}
      >
        {buttonIcon}
        {buttonText}
      </button>
    </div>
  </Card>
);

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  
  const { 
    stats, 
    status, 
    setStats, 
    setStatus, 
    updateLastUpdate,
    addError 
  } = useAdminStore();
  
  // Fetch stats avec le nouveau hook
  const { 
    data: statsData, 
    loading: statsLoading, 
    error: statsError,
    refetch: refetchStats 
  } = useAPIData('/api/stats', {
    onSuccess: (data) => {
      setStats(data);
      updateLastUpdate();
    },
    onError: (error) => {
      setStatus('offline');
      addError(`Stats error: ${error.message}`);
    },
    showNotifications: false
  });
  
  // Fetch health status
  const { 
    data: healthData, 
    loading: healthLoading,
    refetch: refetchHealth 
  } = useAPIData('/health', {
    onSuccess: (data) => {
      setStatus(data.status === 'healthy' ? 'online' : 'degraded');
    },
    onError: () => {
      setStatus('offline');
    },
    showNotifications: false
  });

  // Fetch tournaments
  const {
    data: tournaments,
    loading: tournamentsLoading,
    error: tournamentsError,
    refetch: refetchTournaments
  } = useAPIData('/api/tournaments/', {
    showNotifications: false
  });

  // Fetch archetypes  
  const {
    data: archetypes,
    loading: archetypesLoading,
    error: archetypesError,
    refetch: refetchArchetypes
  } = useAPIData('/api/archetypes/', {
    showNotifications: false
  });
  
  // Auto-refresh toutes les 30 secondes
  useEffect(() => {
    const interval = setInterval(() => {
      refetchStats();
      refetchHealth();
      refetchTournaments();
      refetchArchetypes();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [refetchStats, refetchHealth, refetchTournaments, refetchArchetypes]);
  
  const handleRefresh = useCallback(() => {
    refetchStats();
    refetchHealth();
    refetchTournaments();
    refetchArchetypes();
  }, [refetchStats, refetchHealth, refetchTournaments, refetchArchetypes]);
  
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'text-green-600';
      case 'offline': return 'text-red-600';
      case 'degraded': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };
  
  const getStatusText = () => {
    switch (status) {
      case 'online': return 'En ligne';
      case 'offline': return 'Hors ligne';
      case 'degraded': return 'Dégradé';
      default: return 'Vérification...';
    }
  };

  const isLoading = statsLoading && !stats.tournaments;
  const isRefreshing = statsLoading || healthLoading;
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner className="h-8 w-8" />
      </div>
    );
  }
  
  return (
    <ErrorBoundary>
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
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
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
            <StatCard
              icon={<Database className="h-8 w-8 text-blue-500" />}
              label="Tournois"
              value={stats.tournaments}
              loading={statsLoading}
            />
            
            <StatCard
              icon={<TrendingUp className="h-8 w-8 text-green-500" />}
              label="Archétypes actifs"
              value={stats.archetypes}
              loading={statsLoading}
            />
            
            <StatCard
              icon={<Users className="h-8 w-8 text-purple-500" />}
              label="Total decks"
              value={stats.decks}
              loading={statsLoading}
            />
            
            <StatCard
              icon={<Activity className="h-8 w-8 text-orange-500" />}
              label="Statut"
              value={getStatusText()}
              loading={healthLoading}
              color={getStatusColor()}
            />
          </div>

          {/* Actions principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <ActionCard
              title="Scraping de Données"
              subtitle="Lancer le scraping des tournois"
              description="Collecter les dernières données de tournois depuis MTGTop8"
              buttonText="Lancer le Scraping"
              buttonIcon={<Play className="h-4 w-4 mr-2" />}
              buttonClass="bg-green-600 text-white hover:bg-green-700"
              disabled={status === 'offline'}
              onClick={() => {
                console.log('Scraping lancé');
                // Votre logique de scraping ici
              }}
            />
            
            <ActionCard
              title="Export des Données"
              subtitle="Télécharger les données"
              description="Exporter les données de tournois et archétypes"
              buttonText="Exporter CSV"
              buttonIcon={<Download className="h-4 w-4 mr-2" />}
              buttonClass="bg-blue-600 text-white hover:bg-blue-700"
              disabled={stats.tournaments === 0}
              onClick={() => {
                console.log('Export CSV');
                // Votre logique d'export ici
              }}
            />
            
            <ActionCard
              title="Configuration"
              subtitle="Paramètres système"
              description="Configurer les archétypes et règles de détection"
              buttonText="Paramètres"
              buttonIcon={<Settings className="h-4 w-4 mr-2" />}
              buttonClass="bg-gray-600 text-white hover:bg-gray-700"
              onClick={() => {
                console.log('Configuration');
                // Votre logique de configuration ici
              }}
            />
          </div>

          {/* Recent Data */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card 
              title="Tournois Récents"
              subtitle="Derniers tournois ajoutés"
            >
              {tournamentsError ? (
                <ErrorMessage message={tournamentsError.message} onRetry={refetchTournaments} />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {tournamentsLoading ? (
                    <LoadingSpinner className="h-8 w-8 mx-auto" />
                  ) : tournaments?.data?.length > 0 ? (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {tournaments.data.slice(0, 5).map((tournament: any) => (
                        <div 
                          key={tournament.id}
                          className="flex justify-between items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                          <div>
                            <span className="font-medium">{tournament.name}</span>
                            <p className="text-sm text-gray-500">{tournament.format}</p>
                          </div>
                          <span className="text-sm text-gray-400">{tournament.date}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <>
                      Aucun tournoi récent
                      <button 
                        onClick={refetchTournaments}
                        className="block mx-auto mt-2 text-blue-600 hover:text-blue-700"
                      >
                        Réessayer
                      </button>
                    </>
                  )}
                </div>
              )}
            </Card>

            <Card 
              title="Archétypes Populaires"
              subtitle="Top archétypes par nombre de decks"
            >
              {archetypesError ? (
                <ErrorMessage message={archetypesError.message} onRetry={refetchArchetypes} />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {archetypesLoading ? (
                    <LoadingSpinner className="h-8 w-8 mx-auto" />
                  ) : archetypes?.data?.length > 0 ? (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {archetypes.data.slice(0, 5).map((archetype: any) => (
                        <div 
                          key={archetype.id}
                          className="flex justify-between items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                        >
                          <div>
                            <span className="font-medium">{archetype.name}</span>
                            <p className="text-sm text-gray-500">{archetype.description}</p>
                          </div>
                          <span className="text-sm text-gray-400">{archetype.deck_count || 0} decks</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <>
                      Aucun archétype populaire
                      <button 
                        onClick={refetchArchetypes}
                        className="block mx-auto mt-2 text-blue-600 hover:text-blue-700"
                      >
                        Réessayer
                      </button>
                    </>
                  )}
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default AdminDashboard; 