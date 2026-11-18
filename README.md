# Que faire à Paris maintenant ?

Application web qui liste les événements de Paris (concerts, expositions, ateliers...) avec la météo,
un itinéraire Google Maps et un lien de réservation. On peut chercher par jour, thème, prix, lieu et distance.

Données : [Que faire à Paris](https://opendata.paris.fr) (open data de la Ville de Paris) et [Open-Meteo](https://open-meteo.com).

## Organisation

| Dossier | Rôle | Langage |
|---|---|---|
| `data_collector` | télécharge les données avec curl (API) | bash |
| `data_integrator` | nettoie les données avec pandas, archive le fichier brut | Python |
| `webapp` | site web (Flask) | Python |
| `bin` | lance tout : mise à jour des données toutes les heures + site | bash |

## Lancer l'application

Avec Docker (ou Podman) :

    bash deployer.sh          # puis ouvrir http://localhost:5000
    bash deployer.sh stop     # pour arrêter

Sans Docker (Linux avec python3 et curl) :

    bash lancer.sh            # puis ouvrir http://localhost:5000

Le premier démarrage télécharge les données (environ 30 secondes).
Les logs sont dans `log/`, les anciens fichiers bruts dans `archived/raw/`.
