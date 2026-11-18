#!/bin/bash

FILE=../../data/evenements.csv
dt=$(date +%Y-%m-%d-%H-%M-%S)

if test -f "$FILE"; then
  echo "$FILE existe. Lancement de l'intégration"
  bash run.sh
  echo "Intégration terminée"
  cp $FILE ../../archived/raw/evenements.csv.$dt
  gzip ../../archived/raw/evenements.csv.$dt
  find ../../archived/raw -mtime +2 -delete
else
  echo "Pas de fichier brut"
fi
