import React, { useState } from 'react';
import { api } from '../api/realAPI';
import { useRealData } from '../hooks/useRealData';

interface Tournament {
  id: number;
  name: string;
  format: string;
  date: string;
  participants: number;
  source?: string;
  external_url?: string;
  organizer?: string;
}

interface Archetype {
  id: number;
  name: string;
  description: string;
  winRate: number;
  popularity: number;
}

const AdminPanel: React.FC = () => {
  const [newTournament, setNewTournament] = useState({
    name: '',
    format: 'Standard',
    participants: 0,
    date: new Date().toISOString().split('T')[0],
    source: 'melee',
    external_url: '',
    organizer: 'Melee.gg'
  });

  const [newArchetype, setNewArchetype] = useState({
    name: '',
    description: '',
    winRate: 50,
    popularity: 1
  });

  const [message, setMessage] = useState<string>('');

  // Données en temps réel
  const { data: stats, loading: statsLoading, refetch: refetchStats } = 
    useRealData(() => api.getStats());
  
  const { data: tournaments, loading: tournamentsLoading, refetch: refetchTournaments } = 
    useRealData(() => api.getTournaments());
  
  const { data: archetypes, loading: archetypesLoading, refetch: refetchArchetypes } = 
    useRealData(() => api.getArchetypes());

  const handleAddTournament = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/tournaments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTournament)
      });
      
      if (response.ok) {
        setMessage('✅ Tournoi ajouté avec succès!');
        setNewTournament({
          name: '',
          format: 'Standard',
          participants: 0,
          date: new Date().toISOString().split('T')[0],
          source: 'manual',
          external_url: '',
          organizer: 'Manual Entry'
        });
        refetchTournaments();
        refetchStats();
      } else {
        setMessage('❌ Erreur lors de l\'ajout du tournoi');
      }
    } catch (error) {
      setMessage('❌ Erreur de connexion');
    }
  };

  const handleAddArchetype = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/archetypes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newArchetype)
      });
      
      if (response.ok) {
        setMessage('✅ Archétype ajouté avec succès!');
        setNewArchetype({
          name: '',
          description: '',
          winRate: 50,
          popularity: 1
        });
        refetchArchetypes();
        refetchStats();
      } else {
        setMessage('❌ Erreur lors de l\'ajout de l\'archétype');
      }
    } catch (error) {
      setMessage('❌ Erreur de connexion');
    }
  };

  const handleRefreshAll = () => {
    refetchStats();
    refetchTournaments();
    refetchArchetypes();
    setMessage('🔄 Données actualisées');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Administration Metalyzr</h1>
            <p className="text-gray-600 mt-2">Gestion des tournois et archétypes</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={handleRefreshAll}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              🔄 Actualiser
            </button>
            <a
              href="/"
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
            >
              📊 Dashboard
            </a>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-blue-800">{message}</p>
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Statistiques</h3>
            {statsLoading ? (
              <p className="text-gray-500">Chargement...</p>
            ) : stats ? (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">🏆 {stats.tournaments} tournois</p>
                <p className="text-sm text-gray-600">🎯 {stats.archetypes} archétypes</p>
                <p className="text-sm text-gray-600">🃏 {stats.decks} decks</p>
                <p className="text-xs text-gray-500">MAJ: {new Date(stats.lastUpdate).toLocaleString()}</p>
              </div>
            ) : (
              <p className="text-red-500">Erreur de chargement</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Add Tournament Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">➕ Ajouter un Tournoi</h2>
            <form onSubmit={handleAddTournament} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom du tournoi
                </label>
                <input
                  type="text"
                  value={newTournament.name}
                  onChange={(e) => setNewTournament({...newTournament, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Format
                </label>
                <select
                  value={newTournament.format}
                  onChange={(e) => setNewTournament({...newTournament, format: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Standard">Standard</option>
                  <option value="Modern">Modern</option>
                  <option value="Legacy">Legacy</option>
                  <option value="Pioneer">Pioneer</option>
                  <option value="Commander">Commander</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Participants
                </label>
                <input
                  type="number"
                  value={newTournament.participants}
                  onChange={(e) => setNewTournament({...newTournament, participants: parseInt(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  value={newTournament.date}
                  onChange={(e) => setNewTournament({...newTournament, date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Source
                </label>
                <select
                  value={newTournament.source}
                  onChange={(e) => setNewTournament({...newTournament, source: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="melee">Melee.gg (API)</option>
                  <option value="mtgtop8">MTGTop8 (Scraping)</option>
                  <option value="mtgo">MTGO (Scraping)</option>
                  <option value="manual">Manuel</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Lien externe (optionnel)
                </label>
                <input
                  type="url"
                  value={newTournament.external_url}
                  onChange={(e) => setNewTournament({...newTournament, external_url: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://www.mtgtop8.com/event?e=12345"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organisateur
                </label>
                <input
                  type="text"
                  value={newTournament.organizer}
                  onChange={(e) => setNewTournament({...newTournament, organizer: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nom de l'organisateur"
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
              >
                Ajouter le Tournoi
              </button>
            </form>
          </div>

          {/* Add Archetype Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">➕ Ajouter un Archétype</h2>
            <form onSubmit={handleAddArchetype} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom de l'archétype
                </label>
                <input
                  type="text"
                  value={newArchetype.name}
                  onChange={(e) => setNewArchetype({...newArchetype, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newArchetype.description}
                  onChange={(e) => setNewArchetype({...newArchetype, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Taux de victoire (%)
                </label>
                <input
                  type="number"
                  value={newArchetype.winRate}
                  onChange={(e) => setNewArchetype({...newArchetype, winRate: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                  max="100"
                  step="0.1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Popularité (%)
                </label>
                <input
                  type="number"
                  value={newArchetype.popularity}
                  onChange={(e) => setNewArchetype({...newArchetype, popularity: parseFloat(e.target.value) || 0})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                  max="100"
                  step="0.1"
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md transition-colors"
              >
                Ajouter l'Archétype
              </button>
            </form>
          </div>
        </div>

        {/* Data Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          {/* Tournaments Table */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Tournois ({tournaments?.length || 0})</h3>
            {tournamentsLoading ? (
              <p className="text-gray-500">Chargement...</p>
            ) : tournaments && tournaments.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Nom</th>
                      <th className="text-left py-2">Format</th>
                      <th className="text-left py-2">Participants</th>
                      <th className="text-left py-2">Date</th>
                      <th className="text-left py-2">Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tournaments.map((tournament: Tournament) => (
                      <tr key={tournament.id} className="border-b">
                        <td className="py-2 font-medium">
                          {tournament.external_url ? (
                            <a 
                              href={tournament.external_url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 hover:underline"
                            >
                              {tournament.name} 🔗
                            </a>
                          ) : (
                            tournament.name
                          )}
                        </td>
                        <td className="py-2">{tournament.format}</td>
                        <td className="py-2">{tournament.participants}</td>
                        <td className="py-2">{tournament.date}</td>
                        <td className="py-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            tournament.source === 'melee' ? 'bg-green-100 text-green-800' :
                            tournament.source === 'mtgtop8' ? 'bg-blue-100 text-blue-800' :
                            tournament.source === 'mtgo' ? 'bg-purple-100 text-purple-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {tournament.organizer || tournament.source}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">Aucun tournoi</p>
            )}
          </div>

          {/* Archetypes Table */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Archétypes ({archetypes?.length || 0})</h3>
            {archetypesLoading ? (
              <p className="text-gray-500">Chargement...</p>
            ) : archetypes && archetypes.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Nom</th>
                      <th className="text-left py-2">WR%</th>
                      <th className="text-left py-2">Pop%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {archetypes.map((archetype) => (
                      <tr key={archetype.id} className="border-b">
                        <td className="py-2 font-medium">{archetype.name}</td>
                        <td className="py-2">{archetype.winRate}%</td>
                        <td className="py-2">{archetype.popularity}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">Aucun archétype</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel; 