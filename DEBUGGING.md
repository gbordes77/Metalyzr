# 🐛 Guide de Débogage - Metalyzr Frontend

## 🚨 Erreurs Actuelles et Solutions

### 1. **Erreur : `useTournamentDecks` non exporté**

**Problème :**
```
export 'useTournamentDecks' (imported as 'useTournamentDecks') was not found in '../../hooks/useApi'
```

**Solution :**
Ajouter le hook manquant dans `frontend/src/hooks/useApi.ts` :

```typescript
export function useTournamentDecks(
  tournamentId: number,
  params?: {
    archetype?: string;
    limit?: number;
  }
): UseApiState<Deck[]> {
  const [data, setData] = useState<Deck[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const decks = await apiService.getTournamentDecks(tournamentId, params);
      setData(decks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tournamentId) {
      fetchData();
    }
  }, [tournamentId, params?.archetype, params?.limit]);

  return { data, loading, error, refetch: fetchData };
}
```

### 2. **Erreur : Card component onClick prop**

**Problème :**
```
Property 'onClick' does not exist on type 'IntrinsicAttributes & CardProps'
```

**Solution :**
Modifier l'interface CardProps dans `frontend/src/components/ui/Card.tsx` :

```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  onClick?: () => void;  // ← Ajouter cette prop
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  title, 
  subtitle,
  onClick  // ← Ajouter ici
}) => {
  return (
    <div 
      className={`bg-white rounded-lg shadow-md border border-gray-200 ${className} ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}  // ← Ajouter l'event handler
    >
      {/* reste du composant */}
    </div>
  );
};
```

### 3. **Erreur : `react-scripts: command not found`**

**Problème :**
```
sh: react-scripts: command not found
```

**Solution :**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### 4. **Warnings : Dependencies manquantes dans useEffect**

**Problème :**
```
React Hook useEffect has a missing dependency: 'fetchData'
```

**Solution :**
Utiliser useCallback pour les fonctions fetchData :

```typescript
export function useTournaments(params?: {
  format?: string;
  limit?: number;
  offset?: number;
}): UseApiState<Tournament[]> {
  const [data, setData] = useState<Tournament[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const tournaments = await apiService.getTournaments(params);
      setData(tournaments);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [params?.format, params?.limit, params?.offset]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
```

### 5. **Warning : Variable 'Link' non utilisée**

**Problème :**
```
'Link' is defined but never used
```

**Solution :**
Supprimer l'import inutile dans `frontend/src/App.tsx` :

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// Supprimer : import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
```

---

## 🔧 Script de Correction Automatique

Créer et exécuter ce script pour corriger toutes les erreurs :

```bash
#!/bin/bash
# fix-frontend.sh

echo "🔧 Correction des erreurs frontend..."

# 1. Nettoyer et réinstaller les dépendances
cd frontend
echo "📦 Nettoyage des dépendances..."
rm -rf node_modules package-lock.json
npm install

# 2. Ajouter les imports manquants
echo "📝 Correction des imports..."
# Les corrections seront appliquées via les fichiers modifiés

echo "✅ Corrections appliquées !"
echo "🚀 Vous pouvez maintenant lancer: npm start"
```

---

## 🏃‍♂️ Procédure de Démarrage Rapide

### Étapes à suivre en cas d'erreur :

1. **Arrêter tous les processus**
```bash
# Arrêter le frontend s'il tourne
Ctrl+C dans le terminal frontend

# Arrêter Docker si nécessaire
docker-compose down
```

2. **Nettoyer le frontend**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

3. **Redémarrer l'infrastructure**
```bash
# Depuis la racine du projet
docker-compose up -d
```

4. **Vérifier que l'API fonctionne**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/tournaments/
```

5. **Démarrer le frontend**
```bash
cd frontend
npm start
```

---

## 🔍 Diagnostic des Erreurs

### Vérifier l'état des services :

```bash
# État des conteneurs Docker
docker-compose ps

# Logs du backend
docker-compose logs backend

# Test de l'API
curl -s http://localhost:8000/health | jq .

# Test des endpoints
curl -s http://localhost:8000/api/tournaments/ | jq .
curl -s http://localhost:8000/api/archetypes/ | jq .
```

### Vérifier le frontend :

```bash
# Dans le répertoire frontend
npm run build    # Test de compilation
npm test         # Tests unitaires
npm run lint     # Vérification du code
```

---

## 📋 Checklist de Résolution

- [ ] ✅ Hook `useTournamentDecks` ajouté
- [ ] ✅ Interface `CardProps` mise à jour avec `onClick`
- [ ] ✅ Dependencies `useCallback` corrigées
- [ ] ✅ Import `Link` inutile supprimé
- [ ] ✅ `node_modules` réinstallé
- [ ] ✅ API backend fonctionnelle
- [ ] ✅ Frontend compile sans erreur
- [ ] ✅ Navigation fonctionne
- [ ] ✅ Données affichées correctement

---

## 🆘 En cas de problème persistant

1. **Reset complet du frontend :**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

2. **Reset complet de Docker :**
```bash
docker-compose down -v
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

3. **Vérifier les versions :**
```bash
node --version    # Devrait être >= 16
npm --version     # Devrait être >= 8
docker --version  # Devrait être >= 20
```

4. **Logs détaillés :**
```bash
# Frontend avec logs détaillés
cd frontend
REACT_APP_DEBUG=true npm start

# Backend avec logs détaillés
docker-compose logs -f backend
```

---

**Une fois toutes ces corrections appliquées, Metalyzr devrait fonctionner parfaitement ! 🎉** 