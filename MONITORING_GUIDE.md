# 📊 Guide Monitoring & Sécurité Metalyzr v2.0

## 🚀 Nouvelles Fonctionnalités Implémentées

### ✅ **Sécurité Renforcée**
- **Rate Limiting** avec slowapi (limites par endpoint)
- **CORS sécurisé** (origins spécifiques, pas de wildcard)
- **Logging structuré** avec rotation automatique
- **Gestion d'erreurs** centralisée avec métriques

### ✅ **Monitoring Complet**
- **Métriques Prometheus** exposées sur `/metrics`
- **Dashboard Grafana** préconfigurés
- **Alertes** pour performance et availability
- **Health checks** enrichis avec cache status

### ✅ **Documentation API**
- **OpenAPI 3.0** complète sur `/docs`
- **ReDoc** sur `/redoc`
- **Tags organisés** par domaine fonctionnel
- **Exemples** et descriptions détaillées

### ✅ **Tests d'Intégration**
- **Tests end-to-end** avec rate limiting
- **Tests sécurité** CORS et authentification
- **Tests performance** avec seuils définis
- **Tests monitoring** métriques Prometheus

---

## 🛠️ Installation & Configuration

### 1. **Installation des Dépendances**

```bash
# Backend avec nouvelles dépendances
cd backend
pip install -r requirements_simple.txt

# Vérifier l'installation
pip list | grep -E "(slowapi|redis|prometheus)"
```

### 2. **Démarrage du Stack Monitoring**

```bash
# Démarrer Redis + Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Vérifier les services
docker ps
```

### 3. **Démarrage de l'Application**

```bash
# Terminal 1: Backend avec monitoring
cd backend
source venv_new/bin/activate
python main_simple.py

# Terminal 2: Frontend (dans build/)
cd frontend/build
node serve-spa.js
```

---

## 📊 Endpoints de Monitoring

### **Métriques Système**
- **Health Check**: `GET /health`
  - Status API, cache, version
  - Rate limit: 30/minute

- **Métriques Prometheus**: `GET /metrics`
  - Compteurs, histogrammes, gauges
  - Format Prometheus standard

- **Cache Status**: `GET /api/cache/status`
  - État détaillé du cache MTGODecklistCache
  - Rate limit: 20/minute

### **Métriques Applicatives**
- **Stats Globales**: `GET /api/stats`
  - Tournois, decks, archétypes
  - Rate limit: 60/minute

- **Sync Cache**: `GET /api/cache/sync`
  - Force synchronisation
  - Rate limit: 3/minute

---

## 🔒 Rate Limiting

### **Limites par Endpoint**

| Endpoint | Limite | Type |
|----------|---------|------|
| `/health` | 30/minute | Monitoring |
| `/api/stats` | 60/minute | Analytics |
| `/api/tournaments` | 100/minute | Read |
| `/api/tournaments` (POST) | 10/minute | Write |
| `/api/cache/sync` | 3/minute | Admin |

### **Réponse Rate Limit Dépassé**
```json
{
  "error": "Rate limit exceeded: 60 per 1 minute"
}
```
**Status Code**: `429 Too Many Requests`

---

## 📈 Métriques Prometheus

### **Métriques Collectées**

```prometheus
# Requêtes HTTP
metalyzr_requests_total{method, endpoint, status}
metalyzr_request_duration_seconds{quantile}

# Cache Performance  
metalyzr_cache_hits_total{type}

# Erreurs API
metalyzr_api_errors_total{error_type}
```

### **Exemple Queries**

```prometheus
# Taux d'erreur 5min
rate(metalyzr_api_errors_total[5m])

# Latence P95
histogram_quantile(0.95, rate(metalyzr_request_duration_seconds_bucket[5m]))

# Requêtes par seconde
rate(metalyzr_requests_total[1m])

# Cache hit ratio
rate(metalyzr_cache_hits_total[5m])
```

---

## 🎛️ Dashboard Grafana

### **Accès**
- **URL**: http://localhost:3001
- **Login**: admin / metalyzr2025
- **Datasource**: Prometheus (http://prometheus:9090)

### **Panels Recommandés**

1. **API Overview**
   - Requests/sec timeline
   - Error rate percentage
   - Response time distribution

2. **Performance**
   - P50/P95/P99 latency
   - Throughput par endpoint
   - Cache hit ratio

3. **Errors & Alerts**
   - Error types breakdown
   - Rate limiting events
   - Cache failures

4. **System Resources**
   - CPU/Memory usage
   - Disk I/O
   - Network traffic

---

## 🚨 Alertes Configurées

### **Alertes Critiques**
- **API Down**: `up{job="metalyzr-api"} == 0`
- **High Error Rate**: `rate(metalyzr_api_errors_total[5m]) > 0.1`
- **High Memory**: `memory_usage > 85%`

### **Alertes Warning**
- **High Latency**: `P95 > 500ms for 3min`
- **Cache Issues**: `cache_hits == 0 for 5min`
- **High CPU**: `cpu_usage > 80% for 5min`

### **Configuration Slack/Email**
```yaml
# monitoring/alertmanager.yml
route:
  group_by: ['alertname']
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK'
    channel: '#alerts'
```

---

## 🧪 Tests d'Intégration

### **Exécution des Tests**

```bash
# Tests complets
python test_integration_complete.py

# Tests spécifiques avec pytest
pytest test_integration_complete.py::TestMetalyzrIntegration::test_rate_limiting -v
```

### **Tests Couverts**
- ✅ Health check et métriques
- ✅ Rate limiting fonctionnel
- ✅ Sécurité CORS
- ✅ Intégration cache
- ✅ Documentation API
- ✅ Opérations CRUD
- ✅ Gestion d'erreurs
- ✅ Performance baseline

---

## 🔧 Configuration Production

### **Variables d'Environnement**

```bash
# .env.production
METALYZR_ENV=production
REDIS_URL=redis://redis:6379
PROMETHEUS_URL=http://prometheus:9090
LOG_LEVEL=INFO
RATE_LIMIT_STORAGE=redis://redis:6379
CORS_ORIGINS=https://metalyzr.com,https://app.metalyzr.com
```

### **Optimisations Production**

1. **Rate Limiting Redis**
```python
# Utiliser Redis au lieu de in-memory
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379"
)
```

2. **Logging Externe**
```python
# Envoyer logs vers Elasticsearch/Loki
logging_config = {
    "handlers": {
        "file": {"filename": "/logs/metalyzr.log"},
        "syslog": {"address": "logs.metalyzr.com:514"}
    }
}
```

3. **Métriques Externes**
```yaml
# Prometheus remote_write
remote_write:
  - url: "https://prometheus.metalyzr.com/api/v1/write"
    basic_auth:
      username: "metalyzr"
      password: "secret"
```

---

## 🐛 Debugging & Troubleshooting

### **Logs Structurés**

```bash
# Voir les logs en temps réel
tail -f backend/metalyzr.log

# Filtrer par level
grep "ERROR" backend/metalyzr.log | jq

# Rechercher par IP client
grep "127.0.0.1" backend/metalyzr.log
```

### **Métriques Debug**

```bash
# Vérifier métriques exposées
curl http://localhost:8000/metrics | grep metalyzr

# Test rate limiting
for i in {1..70}; do curl -s http://localhost:8000/api/stats > /dev/null; echo "Request $i"; done
```

### **Cache Debug**

```bash
# Status cache détaillé
curl http://localhost:8000/api/cache/status | jq

# Force sync
curl http://localhost:8000/api/cache/sync | jq
```

---

## 📚 Resources Additionnelles

### **Documentation**
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/monitoring/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Grafana Dashboard Gallery](https://grafana.com/grafana/dashboards/)
- [slowapi Documentation](https://github.com/laurentS/slowapi)

### **Dashboards Grafana**
- **FastAPI Dashboard**: ID 15864
- **Redis Dashboard**: ID 11835
- **Node Exporter**: ID 1860

### **Métriques Recommandées**
```prometheus
# SLI/SLO pour Metalyzr
availability = up{job="metalyzr-api"}
latency_p95 = histogram_quantile(0.95, metalyzr_request_duration_seconds_bucket)
error_rate = rate(metalyzr_api_errors_total[5m]) / rate(metalyzr_requests_total[5m])
throughput = rate(metalyzr_requests_total[5m])
```

---

*Guide mis à jour pour Metalyzr v2.0 - Janvier 2025* 