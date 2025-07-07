const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

// Configuration CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Proxy simple pour l'API backend
app.use('/api/*', (req, res) => {
  const fetch = require('node-fetch');
  const url = `http://localhost:8000${req.url}`;
  
  fetch(url, {
    method: req.method,
    headers: req.headers,
    body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
  })
  .then(response => response.json())
  .then(data => res.json(data))
  .catch(err => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Proxy error' });
  });
});

// Proxy pour le health check
app.get('/health', (req, res) => {
  const fetch = require('node-fetch');
  fetch('http://localhost:8000/health')
    .then(response => response.json())
    .then(data => res.json(data))
    .catch(() => res.status(500).json({ error: 'Backend unavailable' }));
});

// Servir les fichiers statiques du build
app.use(express.static(path.join(__dirname, 'build')));

// Fallback pour React Router (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Frontend Metalyzr démarré sur http://localhost:${PORT}`);
  console.log(`📡 Proxy API configuré vers http://localhost:8000`);
  console.log(`🎯 Dashboard: http://localhost:${PORT}`);
  console.log(`👨‍💼 Admin: http://localhost:${PORT}/admin`);
});

module.exports = app; 