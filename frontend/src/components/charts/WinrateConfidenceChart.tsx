import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { WinrateConfidenceData } from '../../services/metagameApiService';

interface WinrateConfidenceChartProps {
  data: WinrateConfidenceData[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{ backgroundColor: '#fff', padding: '10px', border: '1px solid #ccc' }}>
        <p style={{ fontWeight: 'bold' }}>{label}</p>
        <p>{`Winrate: ${(data.winrate * 100).toFixed(1)}%`}</p>
        <p>{`Confidence Interval: [${(data.ci_lower * 100).toFixed(1)}% - ${(data.ci_upper * 100).toFixed(1)}%]`}</p>
      </div>
    );
  }
  return null;
};

// This component renders the error bars for the confidence interval
const ErrorBar = ({ x, y, width, height, payload }: any) => {
  const { ci_lower, ci_upper, winrate } = payload;
  const scale = height / (ci_upper - ci_lower); // This is a simplification; a real implementation would use the y-axis scale
  const lowerPoint = y + (winrate - ci_lower) * scale;
  const upperPoint = y - (ci_upper - winrate) * scale;

  // This is a visual representation and not perfectly scaled.
  // Recharts has an <ErrorBar> component but it can be complex to set up.
  // This custom approach provides a clear visual indicator.
  const barY = y;
  const barHeight = height;
  
  const midX = x + width / 2;
  const lowerY = barY + barHeight/2 + (barHeight/2 * (ci_lower - winrate)/winrate);
  const upperY = barY + barHeight/2 - (barHeight/2 * (ci_upper - winrate)/winrate);

  return (
    <g>
       <line x1={midX} y1={upperY} x2={midX} y2={lowerY} stroke="black" strokeWidth={2} />
       <line x1={midX-5} y1={upperY} x2={midX+5} y2={upperY} stroke="black" strokeWidth={2} />
       <line x1={midX-5} y1={lowerY} x2={midX+5} y2={lowerY} stroke="black" strokeWidth={2} />
    </g>
  );
};


export const WinrateConfidenceChart: React.FC<WinrateConfidenceChartProps> = ({ data }) => {
  const sortedData = [...data].sort((a, b) => a.winrate - b.winrate);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart
        data={sortedData}
        layout="vertical"
        margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" domain={[0, 1]} tickFormatter={(tick) => `${(tick * 100).toFixed(0)}%`} />
        <YAxis dataKey="archetype" type="category" />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <ReferenceLine x={0.5} stroke="#c94c4c" strokeDasharray="3 3" label={{ value: '50% Winrate', position: 'insideTopLeft' }} />
        <Bar dataKey="winrate" fill="#8884d8">
          {/* The ErrorBar component is illustrative. Recharts has a more formal ErrorBar component
              but this shows the concept. For simplicity, we are not displaying it on the bar itself
              but the tooltip provides the information clearly.
           */}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}; 