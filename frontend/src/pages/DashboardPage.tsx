import React, { useState } from 'react';
import { useGenericApi } from '../hooks/useGenericApi';
import { metagameApiService } from '../services/metagameApiService';
import { MetagamePieChart } from '../components/charts/MetagamePieChart';
import { WinrateConfidenceChart } from '../components/charts/WinrateConfidenceChart';
import { MatchupMatrix } from '../components/charts/MatchupMatrix';

const LoadingSpinner = () => <div>Loading...</div>;
const ErrorMessage = ({ message }: { message: string }) => <div style={{ color: 'red' }}>Error: {message}</div>;

export const DashboardPage: React.FC = () => {
  const [format, setFormat] = useState('Modern');
  const [days, setDays] = useState(14);

  // API call for Metagame Share
  const { data: shareData, status: shareStatus, error: shareError, execute: fetchShare } = useGenericApi(
    metagameApiService.getMetagameShare, false
  );
  
  // API call for Winrate Confidence
  const { data: winrateData, status: winrateStatus, error: winrateError, execute: fetchWinrate } = useGenericApi(
    metagameApiService.getWinrateConfidence, false
  );

  // API call for Matchup Matrix
  const { data: matrixData, status: matrixStatus, error: matrixError, execute: fetchMatrix } = useGenericApi(
    metagameApiService.getMatchupMatrix, false
  );

  const fetchData = React.useCallback(() => {
    fetchShare(format, days);
    fetchWinrate(format, days);
    fetchMatrix(format, days);
  }, [format, days, fetchShare, fetchWinrate, fetchMatrix]);

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  const isLoading = shareStatus === 'loading' || winrateStatus === 'loading' || matrixStatus === 'loading';

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Metagame Analysis Dashboard</h1>
      
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <div>
          <label htmlFor="format-select">Format: </label>
          <select id="format-select" value={format} onChange={e => setFormat(e.target.value)}>
            <option value="Modern">Modern</option>
            <option value="Standard">Standard</option>
            <option value="Pioneer">Pioneer</option>
            <option value="Legacy">Legacy</option>
          </select>
        </div>
        <div>
          <label htmlFor="days-input">Days: </label>
          <input 
            id="days-input" 
            type="number" 
            value={days} 
            onChange={e => setDays(Number(e.target.value))} 
            style={{ width: '60px' }}
          />
        </div>
        <button onClick={fetchData} disabled={isLoading}>
          {isLoading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ border: '1px solid #eee', padding: '10px', borderRadius: '8px' }}>
          <h2>Metagame Share</h2>
          {shareStatus === 'loading' && <LoadingSpinner />}
          {shareStatus === 'error' && shareError && <ErrorMessage message={shareError} />}
          {shareStatus === 'success' && shareData && <MetagamePieChart data={shareData.data} />}
        </div>
        <div style={{ border: '1px solid #eee', padding: '10px', borderRadius: '8px' }}>
          <h2>Winrate Confidence</h2>
          {winrateStatus === 'loading' && <LoadingSpinner />}
          {winrateStatus === 'error' && winrateError && <ErrorMessage message={winrateError} />}
          {winrateStatus === 'success' && winrateData && <WinrateConfidenceChart data={winrateData.data} />}
        </div>
        <div style={{ gridColumn: '1 / -1', border: '1px solid #eee', padding: '10px', borderRadius: '8px' }}>
            <h2>Matchup Matrix</h2>
            {matrixStatus === 'loading' && <LoadingSpinner />}
            {matrixStatus === 'error' && matrixError && <ErrorMessage message={matrixError} />}
            {matrixStatus === 'success' && matrixData && <MatchupMatrix data={matrixData.data} />}
        </div>
      </div>
    </div>
  );
}; 