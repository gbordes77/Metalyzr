# Guide Administrateur - Metalyzr

Ce guide est destiné à l'équipe d'administration de Metalyzr. Il explique comment utiliser l'interface d'administration pour gérer la qualité des données, enrichir les informations et configurer la plateforme.

## 1. Accès à l'Interface d'Administration

L'interface d'administration est une section protégée de l'application. 
- En environnement de développement local, vous pouvez y accéder via [http://localhost:3000/admin](http://localhost:3000/admin).
- L'accès en production nécessitera une authentification avec un compte administrateur.

## 2. Fonctionnalités de l'Interface

L'interface d'administration est organisée en plusieurs onglets, chacun ayant un rôle précis dans la gestion des données.

### a. Onglet "Archétypes"

Cet onglet est le cœur de la gestion des données. Il permet de :
- **Visualiser la liste** de tous les archétypes reconnus par le système.
- **Rechercher et filtrer** les archétypes par nom, format, etc.
- **Créer un nouvel archétype** : En cliquant sur le bouton "Nouvel Archétype", vous pouvez définir un nouveau type de deck (ex: nom, format, catégorie, cartes clés).
- **Modifier un archétype existant** : En sélectionnant un archétype dans la liste, vous pouvez modifier ses propriétés.

### b. Onglet "Règles"

Associé à la gestion des archétypes, cet onglet permet de définir la logique de détection automatique.
- **Créer une règle** : Pour un archétype sélectionné, vous pouvez ajouter des règles de détection. Par exemple, une règle "Contient toutes ces cartes" avec la liste `["Lightning Bolt", "Goblin Guide"]` pour l'archétype "Mono-Red Aggro".
- **Ajuster la confiance** : Chaque règle peut avoir un score de confiance pour affiner la précision de la détection automatique.

### c. Onglet "Validation"

Cet onglet est essentiel pour garantir la qualité des données.
- **File d'attente** : Il affiche une liste de toutes les decklists pour lesquelles le système de détection automatique n'a pas pu assigner un archétype avec une confiance suffisante.
- **Actions de validation** : Pour chaque deck en attente, un administrateur peut :
    1.  **Valider l'archétype suggéré** par le système.
    2.  **Assigner manuellement un autre archétype** depuis la liste des archétypes existants.
    3.  **Créer un nouvel archétype** directement à partir de ce deck s'il représente une innovation ou une nouvelle variante.

## 3. Workflow de Gestion des Données

Le workflow typique pour un administrateur est le suivant :

1.  **Surveiller l'onglet "Validation"** : C'est la tâche la plus récurrente. Traiter régulièrement la file d'attente pour que les données présentées aux utilisateurs soient à jour et précises.
2.  **Affiner les règles de détection** : Si vous remarquez que certains decks sont systématiquement mal classifiés, allez dans les onglets "Archétypes" et "Règles" pour ajuster la logique de détection.
3.  **Créer de nouveaux archétypes** : Lorsqu'un nouveau set de cartes sort ou que le métagame évolue, utilisez l'onglet "Archétypes" pour ajouter les nouvelles stratégies émergentes au système.

En maintenant rigoureusement la qualité des données via cette interface, l'équipe d'administration garantit que Metalyzr reste une source d'information fiable et pertinente pour la communauté. 