import math
import cv2
import numpy as np

def compute_center(x, y, w, h):
    center_x = x + w / 2
    center_y = y + h / 2
    return [center_x, center_y]

def handle_multiple_choice(gray_img, orig_img, frage, data, center_aruco_1):
    result = {
        "frage": frage["wert"],
        "antwort": []
    }

    for checkbox in frage["checkboxes"]:
        # Nachdem es ein Rechteck ist, reichen je zwei x- und y-Werte
        center_1 = compute_center(data["markers"]["1"]["x"], data["markers"]["1"]["y"],data["markers"]["1"]["w"],data["markers"]["1"]["h"]) # aruco Marker 1
        offset_x = center_aruco_1[0] - checkbox["x"] - center_1[0]
        offset_y = center_aruco_1[1] - checkbox["y"] - center_1[1]
        print(f"center_1 {center_1}, center_aruco_1 {center_aruco_1}")
        print(f"x: {offset_x} y: {offset_y}")

        xl = math.floor(checkbox["x"] + offset_x) # x Links
        xr = math.floor(checkbox["x"] + frage["checkboxsize"] + offset_x) # x rechts
        yo = math.floor(checkbox["y"] + offset_y) # y oben
        yu = math.floor(checkbox["y"] + frage["checkboxsize"] + offset_y) # y unten
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

def handle_single_choice(bw_img, orig_img, frage, data, center_aruco_1):
    result, orig_img = handle_multiple_choice(bw_img, orig_img, frage, data, center_aruco_1)
    
    # Konsistenzprüfung
    count_true = sum(1 for checkbox in result["antwort"] if checkbox["checked"])
    if count_true != 1:
        raise Exception(f"Falsche Anzahl von Kreuzen: {count_true}")
    
    return result, orig_img