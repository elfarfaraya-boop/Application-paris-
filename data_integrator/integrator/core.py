import os
import pandas as pd

raw_file_path = "../../data/evenements.csv"
staged_file_path = "../../data/evenements_propres.csv"

print("Lecture de " + raw_file_path)
df = pd.read_csv(raw_file_path, sep=";")

for c in ["date_start", "date_end"]:
    df[c] = pd.to_datetime(df[c], utc=True, errors="coerce").dt.tz_convert("Europe/Paris")

coords = df["lat_lon"].str.split(",", expand=True)
df["lat"] = pd.to_numeric(coords[0], errors="coerce")
df["lon"] = pd.to_numeric(coords[1], errors="coerce")
df.loc[(df["lat"] == 0) | (df["lon"] == 0), ["lat", "lon"]] = float("nan")

df = df.dropna(subset=["date_end", "lat", "lon"])

df = df[df["date_end"] >= pd.Timestamp.now(tz="Europe/Paris")]

cols = ["id", "title", "lead_text", "url", "date_start", "date_end",
        "date_description", "occurrences", "address_name", "address_street",
        "address_zipcode", "lat", "lon", "cover_url", "price_type", "qfap_tags",
        "event_indoor", "access_type", "access_link", "access_link_text",
        "price_detail", "contact_url"]
for c in cols:
    if c not in df.columns:
        df[c] = None
df = df[cols].sort_values("date_start")

print("Écriture de " + staged_file_path)
df.to_csv(staged_file_path + ".tmp", index=False)
os.replace(staged_file_path + ".tmp", staged_file_path)
print(str(len(df)) + " événements écrits")
