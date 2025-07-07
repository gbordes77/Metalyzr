import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTournament, useTournamentMetagame, useTournamentDecks } from '../../hooks/useApi';
import { MetagameChart } from '../../components/MetagameChart';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorMessage } from '../../components/ui/ErrorMessage';
import { Card } from '../../components/ui/Card';
import { ArrowLeft, Calendar, MapPin, Users, Trophy, Filter, Medal } from 'lucide-react';

const TournamentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const tournamentId = id ? parseInt(id) : 0;
  
  const [selectedArchetype, setSelectedArchetype] = useState<string>('');
  const [chartType, setChartType] = useState<'pie' | 'bar'>('pie');

  const { data: tournament, loading: tournamentLoading, error: tournamentError } = useTournament(tournamentId);
  const { data: metagame, loading: metagameLoading, error: metagameError } = useTournamentMetagame(tournamentId);
  const { data: decks, loading: decksLoading, error: decksError } = useTournamentDecks(tournamentId, {
    archetype: selectedArchetype || undefined,
    limit: 20
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getPositionColor = (position: number | null) => {
    if (!position) return 'bg-gray-100 text-gray-700';
    if (position === 1) return 'bg-yellow-100 text-yellow-800';
    if (position <= 4) return 'bg-orange-100 text-orange-800';
    if (position <= 8) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-700';
  };

  if (tournamentLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (tournamentError || !tournament) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <ErrorMessage 
          message={tournamentError || 'Tournoi non trouvé'}
          onRetry={() => navigate('/tournaments')}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center mb-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
            >
              <ArrowLeft className="h-5 w-5 mr-1" />
              Retour
            </button>
            <h1 className="text-3xl font-bold text-gray-900">
              {tournament.name}
            </h1>
          </div>
          
          {/* Informations du tournoi */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center text-gray-600">
              <Calendar className="h-4 w-4 mr-2" />
              {formatDate(tournament.date)}
            </div>
            
            {tournament.location && (
              <div className="flex items-center text-gray-600">
                <MapPin className="h-4 w-4 mr-2" />
                {tournament.location}
              </div>
            )}
            
            <div className="flex items-center text-gray-600">
              <Users className="h-4 w-4 mr-2" />
              {tournament.total_players} joueurs
            </div>
            
            <div className="flex items-center text-gray-600">
              <Trophy className="h-4 w-4 mr-2" />
              {tournament.rounds} rondes
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Statistiques du tournoi */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">Format</p>
              <p className="text-2xl font-bold text-gray-900">{tournament.format}</p>
            </div>
          </Card>
          
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">Organisateur</p>
              <p className="text-lg font-semibold text-gray-900">{tournament.organizer}</p>
            </div>
          </Card>
          
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">Decks analysés</p>
              <p className="text-2xl font-bold text-gray-900">{tournament.decks_count}</p>
            </div>
          </Card>
          
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600">Statut</p>
              <span className={`inline-block px-2 py-1 rounded-full text-sm font-medium ${
                tournament.is_complete 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {tournament.is_complete ? 'Terminé' : 'En cours'}
              </span>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Métagame du tournoi */}
          <Card 
            title="Métagame du Tournoi"
            subtitle={`Répartition des ${metagame?.total_decks || 0} decks`}
          >
            {metagameLoading ? (
              <LoadingSpinner className="h-64" />
            ) : metagameError ? (
              <ErrorMessage message={metagameError} />
            ) : metagame && metagame.metagame.length > 0 ? (
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
                      📊
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
                      📈
                    </button>
                  </div>
                </div>
                <MetagameChart data={metagame.metagame} type={chartType} />
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">Aucune donnée de métagame disponible</p>
              </div>
            )}
          </Card>

          {/* Liste des decks */}
          <Card 
            title="Decks du Tournoi"
            subtitle="Performances des joueurs"
          >
            {/* Filtre par archétype */}
            <div className="mb-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <select
                  value={selectedArchetype}
                  onChange={(e) => setSelectedArchetype(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Filtrer par archétype"
                >
                  <option value="">Tous les archétypes</option>
                  {metagame?.metagame.map(entry => (
                    <option key={entry.archetype} value={entry.archetype}>
                      {entry.archetype}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {decksLoading ? (
              <LoadingSpinner className="h-64" />
            ) : decksError ? (
              <ErrorMessage message={decksError} />
            ) : decks && decks.length > 0 ? (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {decks.map(deck => (
                  <div 
                    key={deck.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {deck.player_name}
                        </h4>
                        <p className="text-sm text-gray-600">
                          {deck.archetype}
                        </p>
                      </div>
                      {deck.position && (
                        <div className="flex items-center">
                          <Medal className="h-4 w-4 mr-1 text-gray-500" />
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPositionColor(deck.position)}`}>
                            {deck.position}e
                          </span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-4">
                        <span className="text-green-600">
                          {deck.wins}V
                        </span>
                        <span className="text-red-600">
                          {deck.losses}D
                        </span>
                        {deck.draws > 0 && (
                          <span className="text-gray-600">
                            {deck.draws}N
                          </span>
                        )}
                      </div>
                      <div className="text-gray-500">
                        {deck.total_cards} cartes
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">Aucun deck trouvé</p>
              </div>
            )}
          </Card>
        </div>

        {/* Tableau des archétypes */}
        {metagame && metagame.metagame.length > 0 && (
          <Card 
            title="Analyse des Archétypes"
            subtitle="Performance détaillée par archétype"
            className="mt-8"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Archétype</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Catégorie</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Decks</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Part de méta</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Victoires moy.</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-900">Meilleure place</th>
                  </tr>
                </thead>
                <tbody>
                  {metagame.metagame
                    .sort((a, b) => b.meta_share - a.meta_share)
                    .map(entry => (
                      <tr key={entry.archetype} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium text-gray-900">
                          {entry.archetype}
                        </td>
                        <td className="py-3 px-4 text-gray-600">
                          {entry.category}
                        </td>
                        <td className="py-3 px-4 text-right text-gray-900">
                          {entry.deck_count}
                        </td>
                        <td className="py-3 px-4 text-right text-gray-900">
                          {entry.meta_share.toFixed(1)}%
                        </td>
                        <td className="py-3 px-4 text-right text-gray-900">
                          {entry.avg_wins.toFixed(1)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          {entry.best_position ? (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPositionColor(entry.best_position)}`}>
                              {entry.best_position}e
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default TournamentDetails; 