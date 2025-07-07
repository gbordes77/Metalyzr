import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PublicDashboard from './pages/public/PublicDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';

function App() {
  return (
    <Router>
      <div>
        <nav className="bg-gray-800 text-white p-4">
          <ul className="flex space-x-4">
            <li>
              <Link to="/">Public Dashboard</Link>
            </li>
            <li>
              <Link to="/admin">Admin Dashboard</Link>
            </li>
          </ul>
        </nav>
        <main>
          <Routes>
            <Route path="/" element={<PublicDashboard />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 