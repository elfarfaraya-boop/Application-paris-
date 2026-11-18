#!/bin/bash
cd "$(dirname "$0")"

while true
  do
    echo "Téléchargement des données"
    (cd ../data_collector/bin && bash get_data.sh) \
      && echo "Intégration des données" \
      && (cd ../data_integrator/bin && bash workflow.sh) \
      && echo "Données à jour : $(date)" \
      || echo "Échec, on garde les anciennes données"
    sleep ${INTERVALLE:-3600}
  done
