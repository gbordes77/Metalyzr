import React, { useState, useCallback, useEffect } from 'react';
import { useGenericApi } from '../hooks/useGenericApi';
import { metagameApiService } from '../services/metagameApiService';
import { MetagamePieChart } from '../components/charts/MetagamePieChart';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ErrorMessage } from '../components/ui/ErrorMessage';

export const DashboardPage: React.FC = () => {
  const [format, setFormat] = useState('Standard');
  const [startDate, setStartDate] = useState<string>(
    new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );

  const {
    data: shareData,
    status: shareStatus,
    error: shareError,
    execute: fetchShare,
  } = useGenericApi(metagameApiService.getMetagameShare, false);

  const fetchData = useCallback(() => {
    fetchShare(format, startDate);
  }, [format, startDate, fetchShare]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const isLoading = shareStatus === 'loading';

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Metagame Analysis Dashboard</h1>
      
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '8px' }}>
        <div>
          <label htmlFor="format-select">Format: </label>
          <select id="format-select" value={format} onChange={e => setFormat(e.target.value)}>
            <option value="Standard">Standard</option>
            <option value="Modern">Modern</option>
            <option value="Pioneer">Pioneer</option>
            <option value="Legacy">Legacy</option>
          </select>
        </div>
        <div>
          <label htmlFor="start-date-input">Start Date: </label>
          <input 
            id="start-date-input" 
            type="date" 
            value={startDate} 
            onChange={e => setStartDate(e.target.value)} 
          />
        </div>
        <button onClick={fetchData} disabled={isLoading}>
          {isLoading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>
      
      <div style={{ border: '1px solid #eee', padding: '10px', borderRadius: '8px' }}>
        <h2>Metagame Share</h2>
        {shareStatus === 'loading' && <LoadingSpinner />}
        {shareStatus === 'error' && shareError && <ErrorMessage message={shareError} />}
        {shareStatus === 'success' && shareData && <MetagamePieChart data={shareData} />}
      </div>
    </div>
  );
}; 