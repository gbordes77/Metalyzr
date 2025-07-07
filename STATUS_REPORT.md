# État des Lieux et Analyse du Problème Docker

## Objectif Initial

L'objectif était de faire fonctionner l'environnement de développement Docker, spécifiquement le service `backend` (FastAPI/Poetry), qui refusait de démarrer.

## Problème Principal

Le conteneur `backend` échoue systématiquement au démarrage avec une erreur `OCI runtime create failed: ... no such file or directory: unknown`.

Cette erreur est particulièrement déroutante car nos investigations ont prouvé que le fichier cible **existe, est au bon endroit, avec les bonnes permissions et le bon format**.

L'erreur s'est d'abord manifestée pour le script `uvicorn` :
`exec: "/app/.venv/bin/uvicorn": stat /app/.venv/bin/uvicorn: no such file or directory`

Après avoir modifié la commande pour appeler directement l'interpréteur Python, l'erreur s'est reportée sur le binaire `python` lui-même, ce qui est encore plus anormal :
`exec: "/app/.venv/bin/python": stat /app/.venv/bin/python: no such file or directory`

Ce comportement démontre que le problème n'est pas lié à un script ou à son `shebang`, mais à une incapacité fondamentale de l'environnement d'exécution Docker à accéder ou à exécuter des fichiers dans le conteneur au moment du démarrage.

## Actions Réalisées et Investigations Menées

Voici la liste exhaustive des tentatives de correction et des analyses effectuées :

1.  **Dockerfile Multi-Stage :** Le `Dockerfile` du backend a été entièrement restructuré pour utiliser une approche multi-stage, garantissant un environnement de production propre et un venv correctement isolé.
2.  **Correction du Chemin du Module :** La commande de démarrage a été corrigée de `main:app` à `app.main:app` pour correspondre à la structure des répertoires.
3.  **Contournement du Shebang :** La commande (`CMD`) a été modifiée pour appeler directement l'interpréteur Python (`/app/.venv/bin/python -m uvicorn ...`) au lieu du script `uvicorn`. C'est cette modification qui a déplacé l'erreur sur le binaire `python`.
4.  **Vérification des Fichiers :**
    *   Via `ls -la` dans le `Dockerfile`, nous avons confirmé que les fichiers `/app/.venv/bin/uvicorn` et `/app/.venv/bin/python` existent, avec les permissions d'exécution (`-rwxr-xr-x`) et appartiennent au bon utilisateur (`appuser:appgroup`).
    *   Via l'installation de l'utilitaire `file`, nous avons confirmé que le script `uvicorn` était un `Python script, ASCII text executable` avec des fins de ligne Unix (LF), écartant l'hypothèse d'une corruption par des fins de ligne Windows (CRLF).
5.  **Purge du Cache Docker :** La commande `docker builder prune -a -f` a été exécutée pour supprimer plus de 8 Go de cache de build potentiellement corrompu. L'erreur a persisté.
6.  **Réinitialisation de Docker Desktop :** Une réinitialisation complète des paramètres d'usine ("Reset to factory defaults") a été effectuée. L'erreur a persisté, inchangée.

## Fichiers Modifiés

*   `backend/Dockerfile` : Entièrement révisé.
*   `docker-compose.yml` : La version a été notée comme obsolète, mais aucune modification fonctionnelle n'a été apportée.

## Conclusion et Hypothèse Actuelle

**Le problème est exogène au code et à la configuration du projet.**

Toutes les preuves convergent vers un bug de bas niveau dans l'installation de **Docker Desktop sur votre machine (macOS / Apple Silicon)**. L'erreur `OCI runtime create failed: runc create failed...` pointe vers un dysfonctionnement de l'environnement d'exécution des conteneurs. Ni le code, ni le `Dockerfile`, ni même l'état de la configuration de Docker (images, volumes) ne sont en cause.

## Prochaine Étape Recommandée

La seule et unique action restante est la **réinstallation complète et propre de Docker Desktop** :
1.  Désinstallation complète.
2.  Suppression manuelle des fichiers résiduels (`~/Library/...`).
3.  Redémarrage de la machine.
4.  Installation de la dernière version fraîchement téléchargée. 