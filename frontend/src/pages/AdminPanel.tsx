import React, { useState, useEffect, useRef } from 'react';
import { metagameApiService } from '../../services/api';
import { Card } from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import ErrorMessage from '../../components/ui/ErrorMessage';

// Define the type for the status object
interface ITaskStatus {
    status: 'idle' | 'running' | 'completed' | 'failed';
    progress: number;
    total: number;
    message: string;
    error: string | null;
}

const AdminPanel: React.FC = () => {
    const [formats, setFormats] = useState<string[]>([]);
    const [selectedFormat, setSelectedFormat] = useState<string>('');
    const [startDate, setStartDate] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(true); // Loading formats initially
    const [error, setError] = useState<string | null>(null);
    const [notification, setNotification] = useState<string | null>(null);
    
    const [taskStatus, setTaskStatus] = useState<ITaskStatus | null>(null);
    const pollingInterval = useRef<NodeJS.Timeout | null>(null);

    const fetchTaskStatus = async () => {
        try {
            const status = await metagameApiService.getPopulationStatus();
            setTaskStatus(status);

            if (status.status === 'completed' || status.status === 'failed') {
                if (pollingInterval.current) {
                    clearInterval(pollingInterval.current);
                    pollingInterval.current = null;
                }
                if (status.status === 'completed') {
                    setNotification('Data population completed successfully!');
                } else {
                    setError(`Data population failed: ${status.error}`);
                }
            }
        } catch (err) {
            setError('Could not fetch task status.');
            if (pollingInterval.current) {
                clearInterval(pollingInterval.current);
                pollingInterval.current = null;
            }
        }
    };

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const supportedFormats = await metagameApiService.getSupportedFormats();
                setFormats(supportedFormats);
                if (supportedFormats.length > 0) {
                    setSelectedFormat(supportedFormats[0]);
                }
                // Also fetch initial task status in case a task was already running
                await fetchTaskStatus();
            } catch (err) {
                setError('Failed to load supported formats.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchInitialData();

        return () => {
            if (pollingInterval.current) {
                clearInterval(pollingInterval.current);
            }
        };
    }, []);

    useEffect(() => {
        // If a task is running, start polling
        if (taskStatus?.status === 'running' && !pollingInterval.current) {
            pollingInterval.current = setInterval(fetchTaskStatus, 2000); // Poll every 2 seconds
        }
    }, [taskStatus]);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setError(null);
        setNotification(null);
        
        if (taskStatus?.status === 'running') {
            setError("A task is already in progress.");
            return;
        }

        try {
            const response = await metagameApiService.populateDatabase(selectedFormat, startDate);
            setNotification(response.message);
            // Immediately start polling for status
            await fetchTaskStatus();
        } catch (err: any) {
            setError(err.message || 'An unexpected error occurred.');
        }
    };
    
    const isTaskRunning = taskStatus?.status === 'running';

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Admin Panel</h1>
            <Card>
                <h2 className="text-xl font-semibold mb-2">Populate Database</h2>
                <p className="text-gray-600 mb-4">
                    Fetch tournament data from Melee.gg. You can filter by format and start date.
                </p>
                {isLoading ? (
                    <LoadingSpinner />
                ) : error && !taskStatus?.error ? (
                    <ErrorMessage message={error} />
                ) : (
                    <form onSubmit={handleSubmit}>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label htmlFor="format" className="block text-sm font-medium text-gray-700">Format</label>
                                <select
                                    id="format"
                                    value={selectedFormat}
                                    onChange={(e) => setSelectedFormat(e.target.value)}
                                    className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                    disabled={isTaskRunning}
                                >
                                    {formats.map(f => <option key={f} value={f}>{f}</option>)}
                                </select>
                            </div>
                            <div>
                                <label htmlFor="start-date" className="block text-sm font-medium text-gray-700">Start Date</label>
                                <input
                                    type="date"
                                    id="start-date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                    disabled={isTaskRunning}
                                />
                            </div>
                        </div>
                        <button 
                            type="submit" 
                            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                            disabled={isTaskRunning}
                        >
                            {isTaskRunning ? 'Fetching Data...' : 'Fetch Data'}
                        </button>
                    </form>
                )}
            </Card>

            {notification && <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-md">{notification}</div>}
            {taskStatus?.error && <ErrorMessage message={taskStatus.error} />}

            {isTaskRunning && taskStatus && (
                <Card className="mt-4">
                    <h3 className="text-lg font-semibold">Task Progress</h3>
                    <p className="text-gray-700 mb-2">{taskStatus.message}</p>
                    <div className="w-full bg-gray-200 rounded-full h-4">
                        <div 
                            className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                            style={{ width: `${taskStatus.total > 0 ? (taskStatus.progress / taskStatus.total) * 100 : 0}%` }}
                        ></div>
                    </div>
                    <p className="text-right text-sm text-gray-600 mt-1">
                        {taskStatus.progress} / {taskStatus.total}
                    </p>
                </Card>
            )}
        </div>
    );
};

export default AdminPanel; 