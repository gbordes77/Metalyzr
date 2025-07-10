# 👨‍💼 Guide d'Administration - Metalyzr

---

## 🚀 Vue d'Ensemble

Ce guide est destiné aux administrateurs de la plateforme Metalyzr. Il couvre le démarrage des services, la gestion des données et la maintenance de l'application. L'architecture actuelle est basée sur Docker, FastAPI et PostgreSQL, et utilise l'API de **Melee.gg** comme unique source de données.

---

## 🛠️ Démarrage et Surveillance des Services

### 1. Démarrage complet de l'environnement

L'ensemble de l'application (backend, base de données) est géré par Docker Compose.

```bash
# Pour démarrer tous les services en arrière-plan
docker-compose up -d

# Pour vérifier que les conteneurs sont bien en cours d'exécution
docker-compose ps
```
Vous devriez voir les services `backend` et `db` avec le statut `Up` ou `Running`.

### 2. Services à Surveiller

| Service | Port Interne | Port Externe | URL de Santé |
|---------|--------------|--------------|--------------|
| **Backend API** | 8000 | 8000 | `http://localhost:8000/` |
| **Database** | 5432 | 5432 | (Connexion directe) |

Pour vérifier que l'API est fonctionnelle, exécutez :
```bash
curl http://localhost:8000/
# Attendu: {"message":"Welcome to the Metalyzr API"}
```

### 3. Consulter les Logs

En cas de problème, la première étape est de consulter les logs du service backend.

```bash
# Afficher les logs du backend en temps réel
docker-compose logs -f backend
```

---

## 📊 Gestion des Données via le Panneau d'Administration

La tâche administrative la plus courante est de peupler la base de données avec les derniers tournois. Cette action est désormais centralisée dans une interface graphique simple.

### 1. Accès au Panneau d'Administration

-   **URL** : [http://localhost:3000/admin](http://localhost:3000/admin) (en supposant que le frontend tourne localement)

### 2. Procédure de Récupération des Données

Le panneau d'administration vous permet de déclencher le processus de récupération de manière ciblée.

1.  **Accédez à la page d'administration.** Vous y trouverez un formulaire de "Peuplement de la base de données".
2.  **Sélectionnez un format de jeu** dans le menu déroulant (ex: "Modern", "Pioneer"). La liste est automatiquement chargée depuis l'API.
3.  **(Optionnel) Choisissez une date de début.** Si vous ne souhaitez récupérer que les tournois joués après une certaine date, sélectionnez-la via le calendrier. Si laissé vide, le système récupérera par défaut les tournois des 14 derniers jours.
4.  **Cliquez sur "Fetch Data".**

Le système lancera alors une tâche en arrière-plan pour contacter l'API Melee.gg, récupérer tous les tournois, decks et matchs correspondants à vos critères, classifier les archétypes et charger le tout dans la base de données PostgreSQL.

Un message de notification vous confirmera que la tâche a bien été démarrée. Vous pouvez suivre la progression détaillée dans les logs du backend.

---

## 🔄 Maintenance

### 1. Arrêter l'environnement

Pour arrêter proprement tous les services :
```bash
docker-compose down
```

### 2. Forcer une reconstruction des images Docker

Si vous modifiez des dépendances (`pyproject.toml`) ou le `Dockerfile`, vous devez reconstruire l'image du backend.

```bash
docker-compose build
```

### 3. Accès direct à la Base de Données

Pour des opérations de maintenance avancées, vous pouvez vous connecter directement à la base de données PostgreSQL.

```bash
# Se connecter au conteneur de la base de données
docker-compose exec db psql -U user -d metalyzr_db
```
Depuis cet interpréteur, vous pouvez exécuter des requêtes SQL pour inspecter les données, effectuer des sauvegardes ou des restaurations. 