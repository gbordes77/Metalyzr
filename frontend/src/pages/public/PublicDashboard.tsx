import React, { useState } from 'react';
import { useTournaments, useArchetypes, useFormats } from '../../hooks/useApi';
import { TournamentCard } from '../../components/TournamentCard';
import { MetagameChart } from '../../components/MetagameChart';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorMessage } from '../../components/ui/ErrorMessage';
import { Card } from '../../components/ui/Card';
import { Filter, BarChart3, PieChart, TrendingUp } from 'lucide-react';

const PublicDashboard: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<string>('');
  const [chartType, setChartType] = useState<'pie' | 'bar'>('pie');

  const { data: tournaments, loading: tournamentsLoading, error: tournamentsError } = useTournaments({
    format: selectedFormat || undefined,
    limit: 6
  });

  const { data: archetypes, loading: archetypesLoading, error: archetypesError } = useArchetypes({
    format: selectedFormat || undefined
  });

  const { data: formats, loading: formatsLoading } = useFormats();

  // Préparer les données du métagame pour le graphique
  const metagameData = archetypes?.map(archetype => ({
    archetype: archetype.name,
    category: archetype.category,
    deck_count: archetype.deck_count,
    meta_share: archetypes.length > 0 
      ? (archetype.deck_count / archetypes.reduce((sum, a) => sum + a.deck_count, 0)) * 100 
      : 0,
    avg_wins: 0, // Pas disponible dans cette vue
    best_position: null
  })).filter(entry => entry.deck_count > 0) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Metalyzr
              </h1>
              <p className="text-gray-600 mt-2">
                Analyse du métagame Magic: The Gathering
              </p>
            </div>
            
            {/* Filtres */}
            <div className="mt-4 md:mt-0 flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <select
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={formatsLoading}
                  aria-label="Sélectionner un format"
                >
                  <option value="">Tous les formats</option>
                  {formats?.map(format => (
                    <option key={format} value={format}>
                      {format}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Statistiques rapides */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tournois analysés</p>
                <p className="text-2xl font-bold text-gray-900">
                  {tournaments?.length || 0}
                </p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Archétypes actifs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {archetypes?.filter(a => a.deck_count > 0).length || 0}
                </p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center">
              <PieChart className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Decks analysés</p>
                <p className="text-2xl font-bold text-gray-900">
                  {archetypes?.reduce((sum, a) => sum + a.deck_count, 0) || 0}
                </p>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Métagame Chart */}
          <Card 
            title="Répartition du Métagame"
            subtitle={selectedFormat ? `Format: ${selectedFormat}` : 'Tous formats confondus'}
          >
            {archetypesLoading ? (
              <LoadingSpinner className="h-64" />
            ) : archetypesError ? (
              <ErrorMessage message={archetypesError} />
            ) : metagameData.length > 0 ? (
              <div>
                <div className="flex justify-end mb-4">
                  <div className="flex rounded-md shadow-sm">
                    <button
                      onClick={() => setChartType('pie')}
                      className={`px-3 py-2 text-sm font-medium rounded-l-md border ${
                        chartType === 'pie'
                          ? 'bg-blue-50 text-blue-700 border-blue-200'
                          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                      }`}
                      aria-label="Graphique en secteurs"
                      title="Graphique en secteurs"
                    >
                      <PieChart className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => setChartType('bar')}
                      className={`px-3 py-2 text-sm font-medium rounded-r-md border-t border-r border-b ${
                        chartType === 'bar'
                          ? 'bg-blue-50 text-blue-700 border-blue-200'
                          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                      }`}
                      aria-label="Graphique en barres"
                      title="Graphique en barres"
                    >
                      <BarChart3 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <MetagameChart data={metagameData} type={chartType} />
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">Aucune donnée de métagame disponible</p>
              </div>
            )}
          </Card>

          {/* Tournois récents */}
          <Card 
            title="Tournois Récents"
            subtitle="Derniers tournois analysés"
          >
            {tournamentsLoading ? (
              <LoadingSpinner className="h-64" />
            ) : tournamentsError ? (
              <ErrorMessage message={tournamentsError} />
            ) : tournaments && tournaments.length > 0 ? (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {tournaments.map(tournament => (
                  <TournamentCard
                    key={tournament.id}
                    tournament={tournament}
                    className="hover:bg-gray-50"
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">Aucun tournoi trouvé</p>
              </div>
            )}
          </Card>
        </div>

        {/* Archétypes populaires */}
        {archetypes && archetypes.length > 0 && (
          <Card 
            title="Archétypes Populaires"
            subtitle="Archétypes les plus joués"
            className="mt-8"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {archetypes
                .filter(archetype => archetype.deck_count > 0)
                .sort((a, b) => b.deck_count - a.deck_count)
                .slice(0, 6)
                .map(archetype => (
                  <div 
                    key={archetype.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {archetype.name}
                      </h3>
                      <span className="text-sm text-gray-500">
                        {archetype.deck_count} decks
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      {archetype.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {archetype.category}
                      </span>
                      <span className="text-xs text-gray-500">
                        {archetype.color_identity || 'Incolore'}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default PublicDashboard; 