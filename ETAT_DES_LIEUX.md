# État des Lieux du Projet Metalyzr - 11 Juillet 2024

## Objectif Initial

Refondre le projet Metalyzr en un MVP fonctionnel capable de récupérer, d'analyser et d'afficher des données réelles de métagame pour Magic: The Gathering, en se basant sur des sources de données fiables.

## ✅ Ce qui est fonctionnel et stable

1.  **Architecture Docker :**
    *   Un environnement `docker-compose` a été mis en place et est maintenant **stable**.
    *   Il orchestre les services nécessaires : un backend en **FastAPI**, une base de données **PostgreSQL**, et le frontend.
    *   Les `Dockerfile` et `docker-compose.yml` ont été débogués et simplifiés pour assurer des constructions fiables.

2.  **Backend et Base de Données :**
    *   Le backend FastAPI est structuré avec une architecture modulaire (services, intégrations, API).
    *   La base de données PostgreSQL est correctement configurée et le backend s'y connecte sans problème au démarrage.
    *   Les dépendances Python sont gérées proprement via `pyproject.toml` et Poetry.

3.  **Connexion à l'API `start.gg` (source pour Melee.gg) :**
    *   Un client GraphQL **entièrement fonctionnel** pour l'API de `start.gg` a été développé (`backend/integrations/startgg_client.py`).
    *   La clé d'API fournie par l'utilisateur est intégrée de manière sécurisée via les variables d'environnement dans `docker-compose`.
    *   **Le système est capable de s'authentifier et de récupérer avec succès des listes de tournois depuis l'API `start.gg`**. La connexion est une réussite technique.

## ❌ Le Point de Blocage Fondamental

Le seul et unique problème qui nous empêche d'avancer est un **problème de source de données**.

*   **Le service `start.gg` / `Melee.gg` ne semble plus lister de tournois pour le jeu "Magic: The Gathering"**.
*   Nos appels à l'API, bien que techniquement réussis, retournent des tournois pour d'autres jeux (Super Smash Bros., Street Fighter, etc.) mais systématiquement **zéro tournoi de Magic**.
*   Sans une source de données valide, le pipeline de données, bien que fonctionnel, ne peut importer aucune donnée pertinente. L'application reste donc vide.

##  tentativas de Contornar o Bloqueio (tentatives de contournement)

Plusieurs alternatives ont été explorées pour trouver une autre source de données, sans succès :

1.  **Scraping de `mtgo.com`** : Le site officiel charge son contenu dynamiquement via JavaScript. Une tentative de scraping avec `requests` & `BeautifulSoup` a échoué. Une tentative plus avancée avec `Selenium` a également échoué, probablement en raison de protections anti-bot.
2.  **API `magicthegathering.io`** : Ne contient que des données sur les cartes et les éditions, pas de résultats de tournois.
3.  **API `deckbrew.com`** : Est hors service (erreur SSL).

## Conclusion

Le projet est techniquement sain et prêt à fonctionner. La fondation (Docker, FastAPI, DB, client API) est solide. Le blocage n'est pas technique, mais **stratégique** : il nous manque une source de données fiable et accessible pour les résultats de tournois de Magic.

La prochaine étape cruciale est d'identifier et d'intégrer une telle source. 