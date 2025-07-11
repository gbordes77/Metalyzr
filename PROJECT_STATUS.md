# État des Lieux et Mise en Stand-by (11 Juillet 2025)

## 1. Résumé de la Situation

Ce document acte la mise en pause de la version actuelle du projet Metalyzr.

L'objectif de ces derniers jours était de rendre le pipeline de collecte de données fonctionnel en se basant sur le scraper externe `fbettega/mtg_decklist_scrapper`.

**Succès notables :**
- Le projet a été nettoyé (documentation, environnements).
- Le scraper a été intégré comme sous-module et rattaché à un fork personnel (`gbordes77/mtg_decklist_scrapper`), nous en donnant le contrôle.
- Le workflow d'Intégration Continue (CI) a été corrigé pour gérer les sous-modules.
- Une fonctionnalité clé de filtrage par format a été ajoutée au scraper.
- L'authentification à Melee.gg est fonctionnelle.

**Problème fondamental :**
Le scraper `fbettega/mtg_decklist_scrapper` est instable et non maintenu. Chaque correction révèle une nouvelle erreur plus profonde, rendant le processus de débogage inefficace et non viable sur le long terme.

## 2. État du Code

- **Scraper (`gbordes77/mtg_decklist_scrapper`) :** Le code est dans un état non fonctionnel. Les dernières modifications sont commitées mais le script échoue sur une erreur de type `TypeError` lors de l'instanciation de l'objet `CacheItem`.
- **Backend / Frontend :** Le code principal de l'application est resté en l'état et n'a pas été touché.
- **Documentation :** Le projet dispose maintenant de deux documents de référence clairs (`ARCHITECTURE_PIPELINE.md` et `docs/melee_api_documentation.html`) qui serviront de base à la reprise.

## 3. Décision : Mise en Stand-by et Prochaine Étape

**La version actuelle du projet est mise en stand-by.**

La décision a été prise d'abandonner la tentative de réparation du scraper existant.

La reprise se fera sur un **projet neuf ou une branche dédiée**, focalisée sur la réécriture d'un pipeline de données minimaliste, propre et maîtrisé, en s'inspirant de la logique des 3 projets GitHub identifiés, comme discuté précédemment.

Tout le travail effectué jusqu'à présent est sauvegardé dans l'historique Git et servira de référence pour la suite. 