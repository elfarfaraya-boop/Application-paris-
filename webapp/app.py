import pandas as pd
from flask import Flask, render_template, request
from filtres import charger, filtrer, lister_themes
from geo import distance_km, centre_cp
from meteo import charger_meteo, texte_meteo

app = Flask(__name__)
PARIS = "Europe/Paris"


def lien_itineraire(depart, lat, lon):
    url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}&travelmode=transit"
    if depart:
        url += f"&origin={depart[0]},{depart[1]}"
    return url


def fenetre(jour_txt):
    maintenant = pd.Timestamp.now(tz=PARIS)
    jour = pd.to_datetime(jour_txt, errors="coerce")
    if pd.isna(jour):
        return maintenant, maintenant + pd.DateOffset(days=7), "les 7 prochains jours"
    jour = jour.tz_localize(PARIS)
    fin = jour + pd.DateOffset(days=1) - pd.Timedelta(seconds=1)
    return max(jour, maintenant), fin, f"le {jour:%d/%m/%Y}"


def txt(x):
    return x.strip() if isinstance(x, str) else ""


def lien_reservation(r):
    lien = txt(r.get("access_link"))
    if lien.startswith("http"):
        return lien
    type_acces = txt(r.get("access_type")).lower()
    if "réserv" in type_acces or "reserv" in type_acces:
        return txt(r.get("url"))
    return ""


def en_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def lignes(d, meteo, depart=None, limite=100):
    out = []
    for _, r in d.head(limite).iterrows():
        dist = ""
        if "distance" in d.columns:
            dist = f"{r['distance']:.1f} km".replace(".", ",")
        out.append({
            "title": r["title"],
            "url": r["url"],
            "horaire": r["seance_debut"].strftime("%d/%m %H:%M"),
            "en_cours": bool(r["en_cours"]),
            "cp": "" if str(r["address_zipcode"]) == "nan" else r["address_zipcode"],
            "prix": r["price_type"],
            "distance": dist,
            "image": r["cover_url"] if isinstance(r["cover_url"], str) else "",
            "meteo": texte_meteo(meteo, r["a_partir_de"]),
            "exterieur": int(r["event_indoor"]) == 0,
            "itineraire": lien_itineraire(depart, r["lat"], r["lon"]),
            "reservation": lien_reservation(r),
        })
    return out


@app.route("/")
def index():
    try:
        DF = charger()
    except FileNotFoundError:
        return "Données en cours de chargement, réessayez dans un instant.", 503
    THEMES = [t for t in lister_themes(DF).index if t != "Expo"]
    prix = request.args.get("prix") or None
    lieu = request.args.get("lieu") or ""
    theme = request.args.get("theme") or None
    interieur = {"interieur": True, "exterieur": False}.get(lieu)

    lat = en_float(request.args.get("lat"))
    lon = en_float(request.args.get("lon"))
    cp = (request.args.get("cp") or "").strip()
    rayon_txt = request.args.get("rayon") or ""
    rayon = en_float(rayon_txt)

    origine = ""
    if cp:
        centre = centre_cp(DF, cp)
        if centre:
            lat, lon = centre
            origine = f"Centre du {cp}"
        else:
            origine = f"Code postal {cp} introuvable"
    if not origine and lat is not None and lon is not None:
        origine = "Ta position"
    avec_position = lat is not None and lon is not None
    depart = (lat, lon) if avec_position else None

    jour = request.args.get("jour") or ""
    debut, fin, periode_txt = fenetre(jour)

    res = filtrer(DF, debut=debut, fin=fin, theme=theme, prix=prix, interieur=interieur)

    if not res.empty and avec_position:
        res = res.copy()
        res["distance"] = distance_km(lat, lon, res["lat"].values, res["lon"].values)
        if rayon:
            res = res[res["distance"] <= rayon]
        res = res.sort_values("distance")

    meteo = charger_meteo()

    sorties, expos = [], []
    nb_sorties = nb_expos = 0
    if not res.empty:
        est_expo = res["qfap_tags"].fillna("").str.contains("Expo", case=False, regex=False)
        nb_sorties, nb_expos = int((~est_expo).sum()), int(est_expo.sum())
        sorties = lignes(res[~est_expo], meteo, depart)
        expos = lignes(res[est_expo], meteo, depart)

    return render_template(
        "index.html", sorties=sorties, expos=expos,
        nb_sorties=nb_sorties, nb_expos=nb_expos,
        themes=THEMES, prix=prix or "", lieu=lieu, theme=theme or "",
        lat=lat if (avec_position and not cp) else "",
        lon=lon if (avec_position and not cp) else "",
        cp=cp, rayon=rayon_txt, origine=origine,
        jour=jour, periode_txt=periode_txt,
        aujourdhui=pd.Timestamp.now(tz=PARIS).strftime('%Y-%m-%d'),
    )
