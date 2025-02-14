import math
import cv2
import numpy as np

def handle_multiple_choice(gray_img, orig_img, frage, offset_x, offset_y, scale_factor):
    result = {
        "frage": frage["wert"],
        "antwort": []
    }

    for checkbox in frage["checkboxes"]:
        x1 = math.floor(offset_x + checkbox["x"] * scale_factor)
        x2 = math.floor(offset_x + (checkbox["x"] + frage["checkboxsize"]) * scale_factor)
        y1 = math.floor(offset_y + checkbox["y"] * scale_factor)
        y2 = math.floor(offset_y + (checkbox["y"] + frage["checkboxsize"]) * scale_factor)
        checkbox_part = gray_img[y1:y2, x1:x2]

        #mean_brightness = np.mean(checkbox_part)
        #if mean_brightness < 100 or mean_brightness > 245:
        #    raise Exception(f"Checkbox " + checkbox["wert"] + ": mean_brightness " + str(mean_brightness))
        
        _, bw_img = cv2.threshold(checkbox_part, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # _, bw_img = cv2.threshold(checkbox_part, mean_brightness, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        black_pixel_ratio = np.sum(bw_img == 0) / bw_img.size
        print(black_pixel_ratio)
        if black_pixel_ratio > 0.20:
            # checked
            result["antwort"].append({"wert": checkbox["wert"], "checked": True})
            orig_img = cv2.rectangle(orig_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            # not checked
            result["antwort"].append({"wert": checkbox["wert"], "checked": False})
            orig_img = cv2.rectangle(orig_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    return result, orig_img  

def handle_single_choice(bw_img, orig_img, frage, offset_x, offset_y, scale_factor):
    result, orig_img = handle_multiple_choice(bw_img, orig_img, frage, offset_x, offset_y, scale_factor)
    
    # Konsistenzprüfung
    count_true = sum(1 for checkbox in result["antwort"] if checkbox["checked"])
    if count_true != 1:
        raise Exception(f"Falsche Anzahl von Kreuzen: {count_true}")
    
    return result, orig_img