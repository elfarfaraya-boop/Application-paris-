#!/bin/bash
# Lance l'appli sans Docker, sur n'importe quelle distribution Linux.
# Usage : bash lancer.sh [port]      (5000 par défaut)
cd "$(dirname "$0")"
export PORT=${1:-5000}

if ! command -v python3 > /dev/null || ! command -v curl > /dev/null; then
  echo "Il manque python3 ou curl. Installez-les avec :"
  echo "  Debian/Ubuntu : sudo apt-get install -y python3 python3-venv python3-pip curl"
  echo "  Fedora        : sudo dnf install -y python3 python3-pip curl"
  echo "  Arch          : sudo pacman -S python python-pip curl"
  echo "  openSUSE      : sudo zypper install -y python3 python3-pip curl"
  echo "  Alpine        : sudo apk add python3 py3-pip curl bash"
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv || { rm -rf .venv; echo "Installez le module venv (Debian/Ubuntu : sudo apt-get install python3-venv)"; exit 1; }
fi
source .venv/bin/activate
pip install -q -r requirements.txt

bash install.sh
bash bin/run.sh
