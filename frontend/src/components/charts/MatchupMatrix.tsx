import React from 'react';
import { MatchupMatrixData } from '../../services/metagameApiService';

interface MatchupMatrixProps {
  data: MatchupMatrixData;
}

// Helper function to get a color based on winrate
const getColorForWinrate = (winrate: number): string => {
  if (winrate > 0.6) return '#d4edda'; // Strong win
  if (winrate > 0.52) return '#e2f0d9'; // Slight edge
  if (winrate < 0.4) return '#f8d7da'; // Strong loss
  if (winrate < 0.48) return '#fcebe3'; // Slight disadvantage
  return '#f5f5f5'; // Neutral
};

export const MatchupMatrix: React.FC<MatchupMatrixProps> = ({ data }) => {
  const { archetypes, matrix } = data;

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ borderCollapse: 'collapse', width: '100%', minWidth: '600px', fontSize: '14px' }}>
        <thead>
          <tr>
            <th style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'left' }}>Archetype</th>
            {archetypes.map((archetype, index) => (
              <th key={index} style={{ padding: '8px', border: '1px solid #ddd', writingMode: 'vertical-rl', textOrientation: 'mixed' }}>
                {archetype}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {archetypes.map((rowArchetype, rowIndex) => (
            <tr key={rowIndex}>
              <td style={{ padding: '8px', border: '1px solid #ddd', fontWeight: 'bold' }}>{rowArchetype}</td>
              {matrix[rowIndex].map((winrate, colIndex) => (
                <td 
                  key={colIndex} 
                  style={{ 
                    padding: '8px', 
                    border: '1px solid #ddd', 
                    textAlign: 'center',
                    backgroundColor: getColorForWinrate(winrate),
                    color: rowIndex === colIndex ? '#999' : 'inherit'
                  }}
                >
                  {rowIndex === colIndex ? '—' : `${(winrate * 100).toFixed(0)}%`}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}; 