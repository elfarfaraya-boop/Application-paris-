#!/bin/bash
source ../conf/collector.conf

echo "Téléchargement des événements"
curl -XGET -s -f -L "${url}" > ${target_path}/evenements.tmp

if [[ -s ${target_path}/evenements.tmp ]]; then
  mv ${target_path}/evenements.tmp ${target_path}/evenements.csv
else
  echo "Erreur : fichier vide"
  exit 1
fi

echo "Téléchargement de la météo"
curl -XGET -s -f "${meteo_url}" > ${target_path}/meteo.tmp
if [[ -s ${target_path}/meteo.tmp ]]; then
  mv ${target_path}/meteo.tmp ${target_path}/meteo.json
fi
