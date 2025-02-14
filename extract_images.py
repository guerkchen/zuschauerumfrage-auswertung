from pdf2image import convert_from_path
import os
import random
import string
from datetime import datetime

# PDF-Datei einlesen
pdf_path = "input/test02.pdf"  # Pfad zur PDF-Datei
output_folder = "input"  # Ordner für die JPGs

# Sicherstellen, dass der Ausgabeordner existiert
os.makedirs(output_folder, exist_ok=True)

# PDF in Bilder umwandeln
images = convert_from_path(pdf_path, dpi=300)  # DPI kann angepasst werden

# Heutiges Datum
date_str = datetime.today().strftime('%Y-%m-%d')

# Jede Seite als JPG speichern
for i, image in enumerate(images):
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    filename = f"{date_str}_{random_str}.jpg"
    filepath = os.path.join(output_folder, filename)
    
    image.save(filepath, "JPEG")
    print(f"Gespeichert: {filepath}")
