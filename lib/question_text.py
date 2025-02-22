from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
import os
import cv2
import numpy as np
import io
import time
import math
import re

load_dotenv()

# Azure initialisierung
AZURE_ENDPOINT = "https://ocr-zuschauerumfrage.cognitiveservices.azure.com/"
AZURE_KEY = os.getenv("AZURE_KEY")
client = ComputerVisionClient(AZURE_ENDPOINT, CognitiveServicesCredentials(AZURE_KEY))

def ocr(bw_img):
    # In ein Byte-Array konvertieren
    _, encoded_image = cv2.imencode('.jpg', bw_img)
    image_bytes = io.BytesIO(encoded_image.tobytes())
    # OCR-Anfrage mit Bild-Variable
    response = client.read_in_stream(image_bytes, raw=True)
    # Verarbeitungs-URL extrahieren
    operation_url = response.headers["Operation-Location"]

    # Warten, bis das OCR fertig ist
    timeout = 0
    while timeout < 10:
        result = client.get_read_result(operation_url.split("/")[-1])
        if result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
            break
        time.sleep(1)
        timeout += 1

    if timeout >= 10:
        raise Exception("Timeout bei Texterkennung") 

    # Ergebnis ausgeben
    if result.status == OperationStatusCodes.succeeded:
        for page in result.analyze_result.read_results:
            result = ""
            for line in page.lines:
                result += line.text + " "
            return result
    else:
        raise Exception("Texterkennung nicht möglich")
    
def maskieren(img, orig_img, img_x, img_y, mask):
    x = round(mask["x"])
    y = round(mask["y"])
    w = round(mask["w"])
    h = round(mask["h"])
    actual_x = x - img_x
    actual_y = y - img_y

    # Maske erstellen (schwarz = 0, weiß = 255)
    mask = np.zeros_like(img, dtype=np.uint8)
    cv2.rectangle(mask, (actual_x, actual_y), (actual_x + w, actual_y + h), 255, -1)
    orig_img = cv2.rectangle(orig_img, (x, y), (x + w, y + h), (0, 0, 0), 2)

    # Pixel der Maske weiß faerben
    masked_img = cv2.bitwise_or(img, mask)
    cv2.imwrite("debug/masked.jpg", masked_img)

    return masked_img, orig_img

def handle_text(gray_img, orig_img, frage):
    x1 = math.floor(frage["x"])
    x2 = math.floor(frage["x"] + frage["w"])
    y1 = math.floor(frage["y"])
    y2 = math.floor(frage["y"] + frage["h"])
    textfeld = gray_img[y1:y2, x1:x2]
    orig_img = cv2.rectangle(orig_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if "mask" in frage:
        for mask in frage["mask"]:
            textfeld, orig_img = maskieren(textfeld, orig_img, x1, y1, mask)

    text = ocr(textfeld).strip()
    orig_img = cv2.putText(orig_img, text, (x1, y2), cv2.FONT_HERSHEY_SIMPLEX, (y2 - y1) // 50, (255, 0, 0), 2, cv2.LINE_AA)
    if re.match(frage["regex"], text):
        return {"frage": frage["wert"], "antwort": text}, orig_img
    else:
        raise Exception(f"Fehlerhafte Texterkennung: {text}")