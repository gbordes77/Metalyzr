import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import RealDashboard from './pages/RealDashboard';
import AdminPanel from './pages/AdminPanel';

function App() {
  return (
    <Router>
      <div>
        <main>
          <Routes>
            <Route path="/" element={<RealDashboard />} />
            <Route path="/dashboard" element={<RealDashboard />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 