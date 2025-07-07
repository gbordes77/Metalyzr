import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, MapPin, Users, Trophy } from 'lucide-react';
import { Tournament } from '../services/api';
import { Card } from './ui/Card';

interface TournamentCardProps {
  tournament: Tournament;
  onClick?: () => void;
  className?: string;
}

export const TournamentCard: React.FC<TournamentCardProps> = ({ 
  tournament, 
  onClick, 
  className = '' 
}) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/tournament/${tournament.id}`);
    }
  };
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getFormatColor = (format: string) => {
    const colors: { [key: string]: string } = {
      'Standard': 'bg-blue-100 text-blue-800',
      'Modern': 'bg-green-100 text-green-800',
      'Legacy': 'bg-purple-100 text-purple-800',
      'Vintage': 'bg-yellow-100 text-yellow-800',
      'Pioneer': 'bg-red-100 text-red-800',
      'Pauper': 'bg-gray-100 text-gray-800'
    };
    return colors[format] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card 
      className={`transition-all duration-200 hover:shadow-lg cursor-pointer hover:scale-105 ${className}`}
      onClick={handleClick}
    >
      <div className="space-y-4">
        {/* En-tête avec nom et format */}
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
            {tournament.name}
          </h3>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFormatColor(tournament.format)}`}>
            {tournament.format}
          </span>
        </div>

        {/* Informations du tournoi */}
        <div className="space-y-2">
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="h-4 w-4 mr-2" />
            {formatDate(tournament.date)}
          </div>
          
          {tournament.location && (
            <div className="flex items-center text-sm text-gray-600">
              <MapPin className="h-4 w-4 mr-2" />
              {tournament.location}
            </div>
          )}
          
          <div className="flex items-center text-sm text-gray-600">
            <Users className="h-4 w-4 mr-2" />
            {tournament.total_players} joueurs
          </div>
          
          {tournament.rounds && (
            <div className="flex items-center text-sm text-gray-600">
              <Trophy className="h-4 w-4 mr-2" />
              {tournament.rounds} rondes
            </div>
          )}
        </div>

        {/* Statut */}
        <div className="flex items-center justify-between">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            tournament.is_complete 
              ? 'bg-green-100 text-green-800' 
              : 'bg-orange-100 text-orange-800'
          }`}>
            {tournament.is_complete ? 'Terminé' : 'En cours'}
          </span>
          
          <span className="text-sm text-blue-600 hover:text-blue-800">
            Voir détails →
          </span>
        </div>
      </div>
    </Card>
  );
}; 