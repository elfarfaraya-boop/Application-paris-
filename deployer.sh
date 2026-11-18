#!/usr/bin/env bash
# Déploie l'appli dans un conteneur (Docker ou Podman) sur n'importe quelle distribution Linux.
# Usage : bash deployer.sh [port|stop]   (port 5000 par défaut)
# Variable facultative : RESEAU=host ./deployer.sh   (si la page ne répond pas, ex. Podman sous WSL)
set -euo pipefail
cd "$(dirname "$0")"

NOM="que-faire-paris"
ARG="${1:-5000}"

if   command -v docker >/dev/null 2>&1; then CTR=docker
elif command -v podman >/dev/null 2>&1; then CTR=podman
else
  echo "ERREUR : ni docker ni podman n'est installé." >&2
  echo "  Debian/Ubuntu : sudo apt-get install -y docker.io    Fedora : sudo dnf install -y podman" >&2
  echo "  Arch : sudo pacman -S docker    openSUSE : sudo zypper install -y docker" >&2
  echo "Ou lancez sans conteneur : ./lancer.sh" >&2
  exit 1
fi
echo "Outil de conteneurs : $CTR"

if [ "$ARG" = "stop" ]; then
  "$CTR" rm -f "$NOM" >/dev/null 2>&1 || true
  echo "Conteneur $NOM arrêté."
  exit 0
fi

if ! [[ "$ARG" =~ ^[0-9]+$ ]]; then
  echo "ERREUR : '$ARG' n'est pas un numéro de port. Usage : ./deployer.sh [port|stop]" >&2
  exit 1
fi
PORT="$ARG"

echo "1/3 Construction de l'image"
"$CTR" build -t "$NOM" .

echo "2/3 Lancement du conteneur sur le port $PORT"
"$CTR" rm -f "$NOM" >/dev/null 2>&1 || true
if [ "${RESEAU:-}" = "host" ]; then
  "$CTR" run -d --name "$NOM" --restart unless-stopped --network host -e PORT="$PORT" "$NOM"
else
  "$CTR" run -d --name "$NOM" --restart unless-stopped -p "${PORT}:5000" "$NOM"
fi

echo "3/3 Attente du démarrage (téléchargement des données, jusqu'à 3 minutes)"
for i in $(seq 1 90); do
  if curl --silent --fail --output /dev/null "http://localhost:${PORT}/"; then
    echo "OK : l'appli répond sur http://localhost:${PORT}"
    echo "Arrêter : ./deployer.sh stop      Voir les logs : $CTR logs $NOM"
    exit 0
  fi
  sleep 2
done

echo "ERREUR : l'appli ne répond pas. Dernières lignes des logs :" >&2
"$CTR" logs --tail 15 "$NOM" >&2 || true
echo "Si le conteneur tourne mais que la page ne s'ouvre pas : RESEAU=host ./deployer.sh" >&2
exit 1
