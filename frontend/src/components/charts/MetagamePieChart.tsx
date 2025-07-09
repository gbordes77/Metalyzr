import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MetagameShareData } from '../../services/metagameApiService';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#d0ed57'];
const MIN_SHARE_FOR_DISPLAY = 2.0; // Minimum percentage to be displayed as its own slice

interface MetagamePieChartProps {
  data: MetagameShareData[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ backgroundColor: '#fff', padding: '5px', border: '1px solid #ccc' }}>
        <p>{`${payload[0].name} : ${payload[0].value.toFixed(2)}%`}</p>
      </div>
    );
  }
  return null;
};

export const MetagamePieChart: React.FC<MetagamePieChartProps> = ({ data }) => {
  const chartData = useMemo(() => {
    const mainArchetypes = data.filter(item => item.share >= MIN_SHARE_FOR_DISPLAY);
    const otherArchetypes = data.filter(item => item.share < MIN_SHARE_FOR_DISPLAY);
    
    const otherShare = otherArchetypes.reduce((sum, item) => sum + item.share, 0);

    const finalData = mainArchetypes.map(item => ({ name: item.archetype, value: item.share }));
    if (otherShare > 0) {
      finalData.push({ name: 'Other', value: otherShare });
    }
    return finalData;
  }, [data]);

  if (!data || data.length === 0) {
    return <div>No data available to display the chart.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          outerRadius={150}
          fill="#8884d8"
          dataKey="value"
          nameKey="name"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}; 