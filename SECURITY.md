# Sécurité Metalyzr

## Gestion des secrets
- **Jamais de secrets dans le code** (ni .env, ni clé API, ni cookie)
- Utilisez **GitHub Secrets** pour la CI/CD
- En local, stockez les secrets dans un fichier `.env` non versionné (`.gitignore`)
- Changez les secrets régulièrement

## Bonnes pratiques
- Respect des recommandations **OWASP Top 10 API**
- Limitez les accès (principle of least privilege)
- Sauvegardes chiffrées (AES-256)
- Logs : rotation 7 jours, max 10 Mo
- RGPD : anonymisation, droit à l'oubli, consentement explicite

## Procédure de disclosure
- Si vous découvrez une faille, contactez l'équipe en privé (issue GitHub en mode "Security" ou email mainteneur)
- Ne publiez jamais de vulnérabilité sans accord
- Correction prioritaire, publication d'un changelog 