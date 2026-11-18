import os
import pandas as pd

PARIS = "Europe/Paris"
FICHIER = os.path.join(os.path.dirname(__file__), "..", "data", "evenements_propres.csv")


def charger():
    df = pd.read_csv(FICHIER)
    for c in ["date_start", "date_end"]:
        df[c] = pd.to_datetime(df[c], utc=True).dt.tz_convert(PARIS)
    return df


def lister_themes(df):
    themes = df["qfap_tags"].dropna().str.split(";").explode().str.strip()
    return themes.value_counts()


def seances(ligne):
    res = []
    occ = ligne["occurrences"]
    if isinstance(occ, str):
        for morceau in occ.split(";"):
            try:
                d, f = morceau.split("_")
                res.append((pd.Timestamp(d).tz_convert(PARIS), pd.Timestamp(f).tz_convert(PARIS)))
            except (ValueError, TypeError):
                continue
    if not res:
        res = [(ligne["date_start"], ligne["date_end"])]
    return res


def prochaine_seance(ligne, debut, fin):
    for d, f in sorted(seances(ligne)):
        if f < debut or d > fin:
            continue
        if (f - d).total_seconds() > 24 * 3600:
            continue
        return d, f
    return None


def filtrer(df, debut, fin, theme=None, prix=None, interieur=None):
    maintenant = pd.Timestamp.now(tz=PARIS)
    debut = max(debut, maintenant)

    res = df
    if theme:
        res = res[res["qfap_tags"].fillna("").str.contains(theme, case=False, regex=False)]
    if prix:
        res = res[res["price_type"] == prix]
    if interieur is not None:
        res = res[res["event_indoor"] == (1 if interieur else 0)]
    if res.empty:
        return res

    prochaines = res.apply(lambda ligne: prochaine_seance(ligne, debut, fin), axis=1)
    res = res[prochaines.notna()].copy()
    if res.empty:
        return res
    res["seance_debut"] = [p[0] for p in prochaines[prochaines.notna()]]

    res["en_cours"] = res["seance_debut"] <= maintenant
    res["a_partir_de"] = res["seance_debut"].where(res["seance_debut"] > debut, debut)
    return res.sort_values(["a_partir_de", "seance_debut"])
