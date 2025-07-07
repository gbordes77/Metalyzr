# Guide des Prérequis Manuels - Metalyzr

Ce document centralise les actions manuelles que vous devez réaliser sur votre machine pour que l'environnement de développement de Metalyzr puisse fonctionner correctement.

En tant qu'assistant IA, ma capacité à interagir avec votre système est volontairement limitée pour des raisons de sécurité. Je ne peux pas démarrer, arrêter ou configurer les services de base de votre ordinateur.

## 1. Démarrer Docker Desktop

**Pourquoi est-ce nécessaire ?**
Metalyzr utilise **Docker** pour créer un environnement de développement isolé et reproductible. Tous les services (base de données, backend, frontend) tournent dans des conteneurs Docker. Pour que je puisse construire et lancer ces conteneurs, le service Docker (le "démon") doit être en cours d'exécution sur votre machine.

**Action à réaliser :**
1.  Trouvez l'application **Docker Desktop** dans votre dossier "Applications" ou via le Spotlight.
2.  Lancez l'application.
3.  Attendez que l'icône de la baleine Docker dans votre barre de menu (en haut à droite de l'écran) soit stable et ne bouge plus. Cela indique que le service est prêt.

**Comment vérifier ?**
Vous pouvez ouvrir votre terminal et taper la commande suivante :
```bash
docker --version
```
Si Docker est bien démarré, cette commande vous retournera la version installée (ex: `Docker version 20.10.17...`). Si vous obtenez une erreur, le service n'est pas encore prêt.

## Prochaine Étape

Une fois que vous avez vérifié que Docker est bien en cours d'exécution, retournez dans notre conversation et envoyez simplement le message : **"GO"**.

Je reprendrai alors immédiatement mon travail pour lancer et tester l'infrastructure du projet. 

**Vous devez lancer le script depuis votre terminal.**

Veuillez lancer la commande suivante dans votre terminal :

```bash
sudo ./scripts/docker-fix-macos-m1.sh
```

Comme vous l'avez dit, le terminal vous demandera votre mot de passe administrateur immédiatement. Une fois que vous l'aurez entré, le script devrait pouvoir s'exécuter sans aucune erreur de permission et effectuer le nettoyage complet comme prévu.

Nous attendons la fin de l'exécution.

Après le redémarrage, nous pourrons passer à la dernière étape : vérifier si le problème est résolu en lançant `docker-compose up`. 