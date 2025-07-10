# 📖 Guide Utilisateur - Metalyzr

---

## 🚀 Bienvenue sur Metalyzr !

Ce guide vous explique comment utiliser Metalyzr pour explorer les données du métagame de Magic: The Gathering. L'application a été entièrement reconstruite pour être plus simple, plus rapide et plus fiable, en utilisant les données réelles de **Melee.gg**.

---

## 🎯 Accès à la Plateforme

Pour utiliser l'application, vous devez d'abord lancer les services (voir le Guide Administrateur pour les détails techniques).

-   **Dashboard Principal** : [http://localhost:3000/](http://localhost:3000/)
-   **Panneau d'Administration** : [http://localhost:3000/admin](http://localhost:3000/admin)

---

## 📊 Explorer le Dashboard

Le Dashboard est le cœur de l'application. C'est ici que vous pouvez visualiser les analyses du métagame.

### 1. Vue d'Ensemble
Le tableau de bord est composé de plusieurs graphiques interactifs :
-   **Répartition du Métagame** : Un graphique circulaire montrant la part de chaque archétype dans le métagame.
-   **Taux de Victoire et Confiance** : Un graphique en barres qui affiche le taux de victoire de chaque archétype majeur, avec un intervalle de confiance pour juger de la pertinence statistique.
-   **Matrice des Matchups** : Un tableau de chaleur qui croise les archétypes et montre le taux de victoire de l'un contre l'autre.

### 2. Interactivité
-   **Filtres Globaux** : Vous pouvez filtrer l'ensemble des données du tableau de bord par format de jeu (Modern, Pioneer, etc.) et par période (les 7, 14 ou 30 derniers jours).
-   **Info-bulles** : Survolez les graphiques pour obtenir des détails précis sur les pourcentages, le nombre de matchs, etc.

Le tableau de bord est conçu pour être la source unique de vérité pour l'analyse du métagame.

---

## 🔧 Mettre à jour les Données (Panneau d'Administration)

Si vous avez les droits d'administrateur, vous pouvez mettre à jour la base de données avec les tournois les plus récents.

**Rendez-vous sur le Panneau d'Administration** ([http://localhost:3000/admin](http://localhost:3000/admin)).

Le processus est simple :
1.  **Choisissez un format** de jeu dans la liste.
2.  **Choisissez une date** de début pour la recherche de tournois.
3.  **Cliquez sur "Fetch Data"**.

Le système se chargera de tout en arrière-plan. Une fois la tâche terminée, les nouvelles données apparaîtront automatiquement dans le dashboard. Pour plus de détails, consultez le **Guide d'Administration**. 