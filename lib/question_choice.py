import math
import cv2
import numpy as np

def handle_multiple_choice(gray_img, orig_img, frage):
    result = {
        "frage": frage["wert"],
        "antwort": []
    }

    for checkbox in frage["checkboxes"]:
        # Nachdem es ein Rechteck ist, reichen je zwei x- und y-Werte
        xl = math.floor(checkbox["x"]) # x Links
        xr = math.floor(checkbox["x"] + frage["checkboxsize"]) # x rechts
        yo = math.floor(checkbox["y"]) # y oben
        yu = math.floor(checkbox["y"] + frage["checkboxsize"]) # y unten
        checkbox_part = gray_img[yo:yu, xl:xr]
        
        _, bw_img = cv2.threshold(checkbox_part, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        black_pixel_ratio = np.sum(bw_img == 0) / bw_img.size
        if black_pixel_ratio > 0.6:
            raise Exception("Checkbox \"" + checkbox["wert"] + "\" hat einen zu hohen Schwarzanteil")
        elif black_pixel_ratio > 0.20:
            # checked
            result["antwort"].append({"wert": checkbox["wert"], "checked": True})
            orig_img = cv2.rectangle(orig_img, (xl, yo), (xr, yu), (0, 255, 0), 2)
        else:
            # not checked
            result["antwort"].append({"wert": checkbox["wert"], "checked": False})
            orig_img = cv2.rectangle(orig_img, (xl, yo), (xr, yu), (0, 0, 255), 2)

    return result, orig_img  

def handle_single_choice(bw_img, orig_img, frage):
    result, orig_img = handle_multiple_choice(bw_img, orig_img, frage)
    
    # Konsistenzprüfung
    count_true = sum(1 for checkbox in result["antwort"] if checkbox["checked"])
    if count_true != 1:
        raise Exception(f"Falsche Anzahl von Kreuzen: {count_true}")
    
    return result, orig_img