import json
import re
from math import radians, sin, cos, sqrt, atan2

def berechne_distanz(lon1, lat1, lon2, lat2):
    # Radius der Erde in Kilometern
    R = 6371.0

    # Koordinaten in Bogenmaß umrechnen
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Unterschiede berechnen
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine-Formel anwenden
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Entfernung berechnen
    entfernung = R * c
    return entfernung

# Datei mit JSON-Daten
file_path = "/mnt/c/Users/Matze/Downloads/gemeinden_Lgz.geojson"

# Regex-Muster
pattern = re.compile(r"^9[01]\d{3}$")

# Zentrum Langenzenn
lgz_2d = [10.7824864428, 49.4892812257]

# GeoJSON aus Datei laden
with open(file_path, "r", encoding="utf-8") as file:
    geojson = json.load(file)

# "features" filtern
print(len(geojson["features"]))
filtered_features = []
for feature in geojson.get("features", []):
    geo_point = feature.get('properties', {}).get("geo_point_2d", {})
    lon = geo_point.get("lon")
    lat = geo_point.get("lat")
    if lon is not None and lat is not None:
        dist = berechne_distanz(lgz_2d[0], lgz_2d[1], lon, lat)
        if dist <= 20.0:
            filtered_features.append(feature)
            print(f"{feature.get('properties', {}).get('plz_name', '')} {dist} km")

geojson["features"] = filtered_features

# Gefiltertes GeoJSON zurück in die Datei schreiben
with open(file_path, "w", encoding="utf-8") as file:
    json.dump(geojson, file, indent=2)

print("Gefilterte GeoJSON-Daten wurden gespeichert.")
