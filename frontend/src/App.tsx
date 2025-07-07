import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PublicDashboard from './pages/public/PublicDashboard';
import TournamentDetails from './pages/public/TournamentDetails';
import AdminDashboard from './pages/admin/AdminDashboard';

function App() {
  return (
    <Router>
      <div>
        <main>
          <Routes>
            <Route path="/" element={<PublicDashboard />} />
            <Route path="/tournament/:id" element={<TournamentDetails />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 