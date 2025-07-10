import React, { useState, useEffect } from 'react';
import { metagameApiService } from '../../services/api';
import { Card } from '../../components/ui/Card';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import ErrorMessage from '../../components/ui/ErrorMessage';

const AdminPanel: React.FC = () => {
    const [formats, setFormats] = useState<string[]>([]);
    const [selectedFormat, setSelectedFormat] = useState<string>('');
    const [startDate, setStartDate] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [notification, setNotification] = useState<string | null>(null);

    useEffect(() => {
        const fetchFormats = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const supportedFormats = await metagameApiService.getSupportedFormats();
                setFormats(supportedFormats);
                if (supportedFormats.length > 0) {
                    setSelectedFormat(supportedFormats[0]);
                }
            } catch (err) {
                setError('Failed to fetch supported formats.');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchFormats();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setNotification(null);
        try {
            const response = await metagameApiService.populateDatabase(selectedFormat, startDate);
            setNotification(response.message);
        } catch (err) {
            setError('Failed to start data population task.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Admin Panel</h1>
            <Card>
                <h2 className="text-xl font-semibold mb-2">Populate Metagame Database</h2>
                <p className="text-gray-600 mb-4">
                    Select a format and a start date to fetch tournament data from Melee.gg.
                    If no filters are selected, recent data for major formats will be fetched.
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                            <label htmlFor="format-select" className="block text-sm font-medium text-gray-700">
                                Format
                            </label>
                            <select
                                id="format-select"
                                value={selectedFormat}
                                onChange={(e) => setSelectedFormat(e.target.value)}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                {formats.map(format => (
                                    <option key={format} value={format}>{format}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="start-date" className="block text-sm font-medium text-gray-700">
                                Start Date
                            </label>
                            <input
                                type="date"
                                id="start-date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="mt-1 block w-full pl-3 pr-2 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            />
                        </div>
                    </div>
                    <div className="flex items-center">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300"
                        >
                            {isLoading && <LoadingSpinner />}
                            Fetch Data
                        </button>
                    </div>
                </form>
                {error && <ErrorMessage message={error} />}
                {notification && (
                    <div className="mt-4 p-3 bg-green-100 text-green-800 rounded-md">
                        {notification}
                    </div>
                )}
            </Card>
        </div>
    );
};

export default AdminPanel; 