import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import './index.css'; // Keep global styles

function App() {
  return (
    <Router>
      <main>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          {/* Admin panel route can be re-added later */}
          {/* <Route path="/admin" element={<AdminPanel />} /> */}
        </Routes>
      </main>
    </Router>
  );
}

export default App; 