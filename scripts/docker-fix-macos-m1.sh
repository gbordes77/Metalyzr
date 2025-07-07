#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
# docker-fix-macos-m1.sh
# Script de réparation complète Docker Desktop sur macOS Apple Silicon

set -e

echo "🔧 Docker Desktop macOS M1/M2 - Réparation Complète"
echo "=================================================="

# 1. Backup des données importantes
echo "📦 Sauvegarde des données Docker..."
mkdir -p ~/docker-backup
docker ps -a --format "table {{.Names}}\t{{.Image}}" > ~/docker-backup/containers.txt
docker images --format "table {{.Repository}}:{{.Tag}}" > ~/docker-backup/images.txt

# 2. Arrêt complet de Docker
echo "🛑 Arrêt de Docker Desktop..."
osascript -e 'quit app "Docker"'
sleep 5

# 3. Kill forcé des processus résiduels
echo "💀 Nettoyage des processus..."
pkill -f docker || true
pkill -f com.docker || true
pkill -f hyperkit || true
pkill -f vpnkit || true

# 4. Suppression complète
echo "🗑️  Suppression de Docker Desktop..."
sudo rm -rf /Applications/Docker.app
rm -rf ~/Library/Group\ Containers/group.com.docker
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/.docker
rm -rf ~/Library/Application\ Support/Docker\ Desktop
rm -rf ~/Library/Preferences/com.docker.docker.plist
rm -rf ~/Library/Saved\ Application\ State/com.electron.docker-frontend.savedState
rm -rf ~/Library/Logs/Docker\ Desktop
rm -rf /usr/local/bin/docker
rm -rf /usr/local/bin/docker-compose
rm -rf /usr/local/bin/docker-credential-*

# 5. Nettoyage Homebrew si présent
echo "🍺 Nettoyage Homebrew..."
if command -v brew &> /dev/null; then
    brew uninstall --cask docker || true
    brew uninstall docker || true
    brew uninstall docker-compose || true
fi

# 6. Reset des permissions
echo "🔐 Reset des permissions système..."
sudo dscl . -delete /Groups/docker || true
sudo rm -rf /var/run/docker.sock || true

# 7. Téléchargement nouvelle version
echo "⬇️  Téléchargement Docker Desktop pour Apple Silicon..."
curl -o ~/Downloads/Docker.dmg "https://desktop.docker.com/mac/main/arm64/Docker.dmg"

# 8. Installation
echo "📥 Installation..."
hdiutil attach ~/Downloads/Docker.dmg
cp -R /Volumes/Docker/Docker.app /Applications/
hdiutil detach /Volumes/Docker

# 9. Configuration post-install
echo "⚙️  Configuration optimale M1/M2..."
mkdir -p ~/.docker
cat > ~/.docker/config.json << EOF
{
  "experimental": true,
  "features": {
    "buildkit": true
  },
  "builder": {
    "gc": {
      "defaultKeepStorage": "10GB",
      "enabled": true
    }
  }
}
EOF

# 10. Lancement initial
echo "🚀 Lancement de Docker Desktop..."
open -a Docker

echo "⏳ Attente du démarrage (30s)..."
sleep 30

# 11. Test de validation
echo "✅ Tests de validation..."
docker run --rm hello-world

# 12. Configuration spécifique M1/M2
echo "🎯 Configuration Apple Silicon..."
cat > ~/docker-m1-config.sh << 'SCRIPT'
#!/bin/bash
# Configuration optimale pour M1/M2

# Activer Rosetta pour x86 emulation
softwareupdate --install-rosetta --agree-to-license

# Configurer les resources
cat > ~/.docker/daemon.json << EOF
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": true,
  "features": {
    "buildkit": true
  },
  "default-runtime": "runc",
  "runtimes": {
    "runc": {
      "path": "/usr/bin/runc"
    }
  }
}
EOF

# Test multi-architecture
docker run --rm --platform linux/amd64 alpine uname -m
docker run --rm --platform linux/arm64 alpine uname -m
SCRIPT

chmod +x ~/docker-m1-config.sh

echo "✨ Installation terminée!"
echo ""
echo "Actions suivantes:"
echo "1. Exécuter: ~/docker-m1-config.sh"
echo "2. Redémarrer le Mac (recommandé)"
echo "3. Tester: cd Metalyzr && docker-compose up"
echo ""
echo "📊 Rapport sauvegardé dans ~/docker-backup/" 