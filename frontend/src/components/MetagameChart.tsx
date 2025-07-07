import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { MetagameEntry } from '../services/api';

interface MetagameChartProps {
  data: MetagameEntry[];
  type?: 'pie' | 'bar';
  className?: string;
}

const COLORS = [
  '#3B82F6', // Blue
  '#EF4444', // Red
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#6B7280', // Gray
  '#F97316', // Orange
  '#14B8A6', // Teal
  '#84CC16', // Lime
];

export const MetagameChart: React.FC<MetagameChartProps> = ({ 
  data, 
  type = 'pie', 
  className = '' 
}) => {
  // Préparer les données pour les graphiques
  const chartData = data.map((entry, index) => ({
    ...entry,
    color: COLORS[index % COLORS.length]
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.archetype}</p>
          <p className="text-sm text-gray-600">Catégorie: {data.category}</p>
          <p className="text-sm text-blue-600">
            Part de méta: {data.meta_share.toFixed(1)}%
          </p>
          <p className="text-sm text-green-600">
            Decks: {data.deck_count}
          </p>
          <p className="text-sm text-purple-600">
            Victoires moy.: {data.avg_wins.toFixed(1)}
          </p>
        </div>
      );
    }
    return null;
  };

  if (type === 'pie') {
    return (
      <div className={`w-full h-96 ${className}`}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              outerRadius={120}
              fill="#8884d8"
              dataKey="meta_share"
              label={({ archetype, meta_share }) => 
                meta_share > 5 ? `${archetype} (${meta_share.toFixed(1)}%)` : ''
              }
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              formatter={(value, entry: any) => (
                <span style={{ color: entry.color }}>
                  {entry.payload.archetype}
                </span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return (
    <div className={`w-full h-96 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="archetype" 
            angle={-45}
            textAnchor="end"
            height={80}
            interval={0}
          />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="meta_share" fill="#3B82F6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}; 