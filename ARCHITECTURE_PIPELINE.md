# Architecture du Pipeline de Données de Metalyzr

## 1. Objectif : Un Pipeline Unifié

L'objectif de Metalyzr est de fournir des analyses de métagame à jour et pertinentes. Pour ce faire, le projet s'articule autour d'un pipeline de données qui intègre trois composants externes clés, chacun jouant un rôle distinct mais complémentaire. Ce document décrit l'architecture de ce pipeline, de l'acquisition des données brutes à leur classification.

Les trois piliers de notre stratégie de données sont :
1.  **`fbettega/mtg_decklist_scrapper`**: Pour l'acquisition de nouvelles données.
2.  **`Jiliac/MTGODecklistCache`**: Comme source massive de données historiques.
3.  **`Badaro/MTGOArchetypeParser`**: L'inspiration pour notre moteur de classification d'archétypes.

---

## 2. Les Composants du Pipeline

### Composant 1 : Acquisition de Données Actives
- **Projet de Référence** : `fbettega/mtg_decklist_scrapper`
- **Rôle dans Metalyzr** : C'est notre **point d'entrée actif** pour les données de tournois récents. Ce scraper Python est capable de se connecter à des plateformes comme Melee.gg et MTGO pour télécharger les derniers résultats.
- **Intégration** :
    - Le scraper est intégré en tant que sous-module Git dans le répertoire `scrapers/`.
    - Il est exécuté comme une tâche préliminaire (manuellement ou via un script/worker) pour peupler un cache local de fichiers JSON.
- **Flux** : `Exécution du script` -> `Connexion aux plateformes (Melee, MTGO)` -> `Téléchargement des tournois` -> `Stockage en fichiers JSON dans un cache local`.

### Composant 2 : Base de Données Historiques
- **Projet de Référence** : `Jiliac/MTGODecklistCache`
- **Rôle dans Metalyzr** : Il constitue notre **fondation de données historiques**. Ce dépôt, bien qu'archivé et non maintenu, contient des années de résultats de tournois dans un format JSON structuré. Il est essentiel pour l'analyse des tendances à long terme.
- **Intégration** :
    - Les données de ce projet sont actuellement présentes dans le répertoire `data/` (ou un équivalent).
    - Metalyzr a (ou aura) un lecteur de cache capable de parcourir cette arborescence de fichiers, de les lire et de les transformer en objets utilisables par le reste de l'application.
- **Flux** : `Lecteur de cache` -> `Parcours du répertoire de données historiques` -> `Chargement des fichiers JSON de tournois passés`.

### Composant 3 : Moteur de Classification d'Archétypes
- **Projet de Référence** : `Badaro/MTGOArchetypeParser` (en C#)
- **Rôle dans Metalyzr** : C'est le **cerveau analytique** du pipeline. Son rôle est de prendre une liste de deck (une *decklist*) et de la classifier en un archétype connu (ex: "Izzet Murktide", "4C Control", "Burn").
- **Intégration** :
    - Le projet Metalyzr n'utilise pas directement le projet C# original. Il s'en inspire fortement en implémentant une version Python de ce moteur de classification basé sur des règles.
    - On retrouve cette logique dans le module `backend/integrations/badaro_archetype_engine.py`.
- **Flux** : `Decklist en entrée` -> `Analyse des cartes par le moteur de règles` -> `Nom de l'archétype en sortie`.

---

## 3. Le Pipeline Unifié : Schéma de Fonctionnement

Ces trois composants s'assemblent en un flux logique unique :

```mermaid
graph TD
    subgraph "Étape 1: Acquisition"
        A[Exécution de mtg_decklist_scrapper] --> B{Cache Local (Nouveaux Tournois)};
        C[Cache Existant (Jiliac/MTGODecklistCache)] --> D{Cache Local (Tournois Historiques)};
    end

    subgraph "Étape 2: Traitement"
        B --> E[Lecteur de Cache];
        D --> E;
        E --> F[Extraction d'une Decklist];
        F --> G[Moteur de Classification d'Archétypes];
        G --> H{Archétype Identifié};
    end

    subgraph "Étape 3: Stockage & Exposition"
        H --> I[Base de Données Metalyzr];
        F --> I;
        I --> J[API Backend];
        J --> K[Frontend / Client];
    end

    style B fill:#e6fffa,stroke:#38b2ac
    style D fill:#e6fffa,stroke:#38b2ac
    style G fill:#fefcbf,stroke:#d69e2e
    style I fill:#c3dafe,stroke:#4299e1
```

**Description du schéma :**

1.  **Acquisition** : On commence par collecter les données. Soit en exécutant le scraper `mtg_decklist_scrapper` pour obtenir des données fraîches, soit en utilisant le cache de données historiques de `Jiliac`. Les deux sources alimentent un pool de tournois au format JSON.
2.  **Traitement** : Un service central (un `ETL` ou un `service de traitement`) lit les fichiers JSON. Pour chaque tournoi, il extrait les listes de decks. Chaque liste est ensuite soumise au moteur de classification, qui retourne le nom de l'archétype correspondant.
3.  **Stockage & Exposition** : Les données enrichies (tournoi + joueurs + decklists + archétypes) sont finalement stockées dans la base de données principale de Metalyzr (probablement PostgreSQL). Le backend expose ensuite ces données via une API REST, qui est consommée par le frontend ou tout autre client. 