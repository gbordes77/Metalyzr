import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AdminDashboard from '../../src/pages/admin/AdminDashboard';
import { useAdminStore } from '../../src/store/adminStore';
import { fetchAPI } from '../../src/utils/api/fetchWrapper';

// Mock dependencies
jest.mock('../../src/utils/api/fetchWrapper');
const mockFetchAPI = fetchAPI as jest.MockedFunction<typeof fetchAPI>;

// Mock Zustand store
jest.mock('../../src/store/adminStore');
const mockUseAdminStore = useAdminStore as jest.MockedFunction<typeof useAdminStore>;

const MockedAdminDashboard = () => (
  <BrowserRouter>
    <AdminDashboard />
  </BrowserRouter>
);

describe('Admin Dashboard Integration Tests', () => {
  const mockStoreState = {
    stats: { tournaments: 0, archetypes: 0, decks: 0 },
    status: 'checking' as const,
    lastUpdate: null,
    errors: [],
    setStats: jest.fn(),
    setStatus: jest.fn(),
    addError: jest.fn(),
    clearErrors: jest.fn(),
    updateLastUpdate: jest.fn(),
  };

  beforeEach(() => {
    mockFetchAPI.mockClear();
    mockUseAdminStore.mockReturnValue(mockStoreState);
    jest.clearAllMocks();
  });

  describe('Initial Render', () => {
    test('should render admin dashboard with all sections', async () => {
      mockFetchAPI.mockResolvedValue({ tournaments: 42, archetypes: 15, decks: 358 });

      render(<MockedAdminDashboard />);

      // Check header
      expect(screen.getByText('Administration')).toBeInTheDocument();
      expect(screen.getByText('Gestion et monitoring de Metalyzr')).toBeInTheDocument();

      // Check stats cards
      expect(screen.getByText('Tournois')).toBeInTheDocument();
      expect(screen.getByText('Archétypes actifs')).toBeInTheDocument();
      expect(screen.getByText('Total decks')).toBeInTheDocument();
      expect(screen.getByText('Statut')).toBeInTheDocument();

      // Check action cards
      expect(screen.getByText('Scraping de Données')).toBeInTheDocument();
      expect(screen.getByText('Export des Données')).toBeInTheDocument();
      expect(screen.getByText('Configuration')).toBeInTheDocument();

      // Check recent sections
      expect(screen.getByText('Tournois Récents')).toBeInTheDocument();
      expect(screen.getByText('Archétypes Populaires')).toBeInTheDocument();
    });

    test('should call all API endpoints on mount', async () => {
      mockFetchAPI.mockResolvedValue({});

      render(<MockedAdminDashboard />);

      await waitFor(() => {
        expect(mockFetchAPI).toHaveBeenCalledWith('/api/stats');
        expect(mockFetchAPI).toHaveBeenCalledWith('/health');
        expect(mockFetchAPI).toHaveBeenCalledWith('/api/tournaments/');
        expect(mockFetchAPI).toHaveBeenCalledWith('/api/archetypes/');
      });
    });
  });

  describe('Data Loading States', () => {
    test('should show loading spinner when fetching initial data', () => {
      mockUseAdminStore.mockReturnValue({
        ...mockStoreState,
        stats: { tournaments: 0, archetypes: 0, decks: 0 }
      });

      // Mock pending API calls
      mockFetchAPI.mockImplementation(() => new Promise(() => {}));

      render(<MockedAdminDashboard />);

      expect(screen.getByRole('status')).toBeInTheDocument(); // Loading spinner
    });

    test('should update stats when API call succeeds', async () => {
      const mockStats = { tournaments: 100, archetypes: 25, decks: 500 };
      mockFetchAPI.mockResolvedValue(mockStats);

      render(<MockedAdminDashboard />);

      await waitFor(() => {
        expect(mockStoreState.setStats).toHaveBeenCalledWith(mockStats);
        expect(mockStoreState.updateLastUpdate).toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    test('should handle API errors gracefully', async () => {
      const mockError = new Error('Network error');
      mockFetchAPI.mockRejectedValue(mockError);

      render(<MockedAdminDashboard />);

      await waitFor(() => {
        expect(mockStoreState.setStatus).toHaveBeenCalledWith('offline');
        expect(mockStoreState.addError).toHaveBeenCalledWith(
          expect.stringContaining('Stats error: Network error')
        );
      });
    });

    test('should show error messages in recent sections when API fails', async () => {
      mockFetchAPI.mockRejectedValue(new Error('API Error'));

      render(<MockedAdminDashboard />);

      await waitFor(() => {
        expect(screen.getAllByText('Réessayer')).toHaveLength(2); // One for each recent section
      });
    });
  });

  describe('User Interactions', () => {
    test('should refresh all data when refresh button is clicked', async () => {
      mockFetchAPI.mockResolvedValue({});

      render(<MockedAdminDashboard />);

      const refreshButton = screen.getByText('🔄 Actualiser');
      fireEvent.click(refreshButton);

      await waitFor(() => {
        expect(mockFetchAPI).toHaveBeenCalledTimes(8); // 4 initial + 4 refresh calls
      });
    });

    test('should navigate back when back button is clicked', () => {
      const mockNavigate = jest.fn();
      jest.doMock('react-router-dom', () => ({
        ...jest.requireActual('react-router-dom'),
        useNavigate: () => mockNavigate,
      }));

      render(<MockedAdminDashboard />);

      const backButton = screen.getByText('← Retour au Dashboard');
      fireEvent.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    test('should handle action button clicks', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      render(<MockedAdminDashboard />);

      // Test scraping button
      const scrapingButton = screen.getByText('▶ Lancer le Scraping');
      fireEvent.click(scrapingButton);
      expect(consoleSpy).toHaveBeenCalledWith('Scraping lancé');

      // Test export button
      const exportButton = screen.getByText('📥 Exporter CSV');
      fireEvent.click(exportButton);
      expect(consoleSpy).toHaveBeenCalledWith('Export CSV');

      // Test config button
      const configButton = screen.getByText('⚙️ Paramètres');
      fireEvent.click(configButton);
      expect(consoleSpy).toHaveBeenCalledWith('Configuration');

      consoleSpy.mockRestore();
    });
  });

  describe('Status Display', () => {
    test('should show correct status colors and text', () => {
      const testCases = [
        { status: 'online', expectedText: 'En ligne', expectedColor: 'text-green-600' },
        { status: 'offline', expectedText: 'Hors ligne', expectedColor: 'text-red-600' },
        { status: 'degraded', expectedText: 'Dégradé', expectedColor: 'text-yellow-600' },
        { status: 'checking', expectedText: 'Vérification...', expectedColor: 'text-gray-600' },
      ] as const;

      testCases.forEach(({ status, expectedText }) => {
        mockUseAdminStore.mockReturnValue({
          ...mockStoreState,
          status
        });

        const { rerender } = render(<MockedAdminDashboard />);

        expect(screen.getByText(expectedText)).toBeInTheDocument();

        rerender(<MockedAdminDashboard />);
      });
    });
  });

  describe('Data Display', () => {
    test('should display tournaments data when available', async () => {
      const mockTournaments = {
        data: [
          { id: 1, name: 'Test Tournament 1', format: 'Modern', date: '2025-01-01' },
          { id: 2, name: 'Test Tournament 2', format: 'Legacy', date: '2025-01-02' }
        ]
      };

      mockFetchAPI.mockResolvedValue(mockTournaments);

      render(<MockedAdminDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Test Tournament 1')).toBeInTheDocument();
        expect(screen.getByText('Modern')).toBeInTheDocument();
      });
    });

    test('should display archetypes data when available', async () => {
      const mockArchetypes = {
        data: [
          { id: 1, name: 'Mono-Red Aggro', description: 'Fast aggro deck', deck_count: 45 },
          { id: 2, name: 'Azorius Control', description: 'Control deck', deck_count: 32 }
        ]
      };

      mockFetchAPI.mockResolvedValue(mockArchetypes);

      render(<MockedAdminDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Mono-Red Aggro')).toBeInTheDocument();
        expect(screen.getByText('45 decks')).toBeInTheDocument();
      });
    });
  });

  describe('Auto-refresh', () => {
    test('should setup auto-refresh interval', () => {
      jest.useFakeTimers();
      const setIntervalSpy = jest.spyOn(global, 'setInterval');

      render(<MockedAdminDashboard />);

      expect(setIntervalSpy).toHaveBeenCalledWith(
        expect.any(Function),
        30000 // 30 seconds
      );

      jest.useRealTimers();
    });
  });

  describe('Button States', () => {
    test('should disable action buttons based on status and data', () => {
      mockUseAdminStore.mockReturnValue({
        ...mockStoreState,
        status: 'offline',
        stats: { tournaments: 0, archetypes: 0, decks: 0 }
      });

      render(<MockedAdminDashboard />);

      const scrapingButton = screen.getByText('▶ Lancer le Scraping');
      const exportButton = screen.getByText('📥 Exporter CSV');

      expect(scrapingButton).toBeDisabled(); // Disabled when offline
      expect(exportButton).toBeDisabled(); // Disabled when no tournaments
    });
  });
}); 