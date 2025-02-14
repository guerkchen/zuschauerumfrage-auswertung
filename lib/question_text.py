from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from dotenv import load_dotenv
import os
import cv2
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

def handle_text(gray_img, orig_img, frage, offset_x, offset_y, scale_factor):
    x1 = math.floor(offset_x + frage["x"] * scale_factor)
    x2 = math.floor(offset_x + (frage["x"] + frage["w"]) * scale_factor)
    y1 = math.floor(offset_y + frage["y"] * scale_factor)
    y2 = math.floor(offset_y + (frage["y"] + frage["h"]) * scale_factor)
    cv2.rectangle(gray_img, (x1, y1), (x2, y2), 0, 2)
    textfeld = gray_img[y1:y2, x1:x2]
    orig_img = cv2.rectangle(orig_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    text = ocr(textfeld).strip()
    if re.match(frage["regex"], text):
        return {"frage": frage["wert"], "antwort": text}, orig_img
    else:
        raise Exception(f"Fehlerhafte Texterkennung: {text}")