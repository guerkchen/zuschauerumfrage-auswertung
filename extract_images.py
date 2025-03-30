import argparse
from pdf2image import convert_from_path
import os
import random
import string
import re
import cv2
import numpy as np

def calculate_black_pixel_ratio(bw_img):
    black_pixels = np.sum(bw_img == 0)
    total_pixels = bw_img.size
    black_pixel_ratio = black_pixels / total_pixels
    return black_pixel_ratio

def extract_date_from_filename(filename):
    # Beispiel: Extrahieren des Datums im Format YYYY-MM-DD aus dem Dateinamen
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    if match:
        return match.group(0)
    raise Exception("Datum nicht im Dateinamen gefunden")

# Kommandozeilenargumente parsen
parser = argparse.ArgumentParser(description='PDF in Bilder umwandeln')
parser.add_argument('pdf_path', type=str, help='Pfad zur PDF-Datei')
args = parser.parse_args()

# PDF-Datei einlesen
pdf_path = args.pdf_path  # Pfad zur PDF-Datei
output_folder = "input"  # Ordner für die JPGs

# Sicherstellen, dass der Ausgabeordner existiert
os.makedirs(output_folder, exist_ok=True)

# Datum aus dem Dateinamen extrahieren
date_str = extract_date_from_filename(pdf_path)

# Unterordner für das Datum erstellen
date_folder = os.path.join(output_folder, date_str)
os.makedirs(date_folder, exist_ok=True)

# PDF in Bilder umwandeln
images = convert_from_path(pdf_path, dpi=300)  # DPI kann angepasst werden

total_pages = len(images)
saved_pages = 0
skipped_pages = 0

# Jede Seite als JPG speichern
for i, image in enumerate(images):
    # Bild in Graustufen konvertieren
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    black_pixel_ratio = calculate_black_pixel_ratio(gray_image)
    
    if black_pixel_ratio >= 0.00000001:
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        filename = f"{date_str}_{random_str}.jpg"
        filepath = os.path.join(date_folder, filename)
        
        image.save(filepath, "JPEG")
        saved_pages += 1
        print(f"Gespeichert: {filepath}")
    else:
        skipped_pages += 1

print(f"Gesamtseiten: {total_pages}")
print(f"Ausgegebene Seiten: {saved_pages}")
print(f"Übersprungene Seiten: {skipped_pages}")
