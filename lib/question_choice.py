import math
import cv2
import numpy as np

def find_circle(img, diameter):
    radius = diameter / 2
    h, w = img.shape[:2] # ist fuer orig_img identisch
    if math.ceil(diameter) > h or math.ceil(diameter) > w:
        raise Exception("Durchmesser ist groeser als Hoehe oder Weite des Bildes")
    
    for x_center in range(math.floor(radius), w - math.ceil(radius)):
        for y_center in range(math.floor(radius), h - math.ceil(radius)):
            notBlack = 0
            for degree in range(0, 359):
                theta = math.radians(degree)
                x = round(x_center + radius * math.cos(theta))
                y = round(y_center + radius * math.sin(theta))
                if img[y, x] != 0:
                    notBlack += 1

            if notBlack < 10:
                return x_center, y_center
    
    raise Exception("Kreis nicht gefunden")

def get_black_ratio_in_circle(img, x_center, y_center, radius):
    # Maske erstellen (schwarz = 0, weiß = 255)
    mask = np.zeros_like(img, dtype=np.uint8)
    cv2.circle(mask, (x_center, y_center), radius, 255, -1)

    # Nur die Pixel innerhalb der Maske betrachten
    masked_image = cv2.bitwise_and(img, img, mask=mask)

    # Anzahl der schwarzen Pixel zählen (Pixelwert 0)
    black_pixels = np.sum((masked_image == 0) & (mask == 255))

    # Gesamte Pixelzahl berechnen
    pixel_count = round(math.pi * radius**2)

    return black_pixels / pixel_count

def handle_multiple_choice(gray_img, orig_img, frage):
    result = {
        "frage": frage["wert"],
        "antwort": []
    }

    for checkbox in frage["checkboxes"]:
        # Nachdem es ein Rechteck ist, reichen je zwei x- und y-Werte
        outer_diameter = frage["checkboxsize"]
        offset = round(outer_diameter) // 4
        xl = math.floor(checkbox["x"] - offset) # x Links
        xr = math.floor(checkbox["x"] + round(outer_diameter) + offset) # x rechts
        yo = math.floor(checkbox["y"] - offset) # y oben
        yu = math.floor(checkbox["y"] + round(outer_diameter) + offset) # y unten
        checkbox_part = gray_img[yo:yu, xl:xr]
       
        _, bw_img = cv2.threshold(checkbox_part, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        x_center, y_center = find_circle(bw_img, outer_diameter)

        inner_radius = math.floor((outer_diameter - (outer_diameter / 10)) / 2)
        black_pixel_ratio = get_black_ratio_in_circle(bw_img, x_center, y_center, inner_radius)
        if black_pixel_ratio > 0.4:
            orig_img = cv2.circle(orig_img, (x_center + xl, y_center + yo), inner_radius, (255, 0, 0), 2)
            result["antwort"].append({"wert": checkbox["wert"], "checked": True})
            print("Checkbox \"" + checkbox["wert"] + "\" hat einen sehr hohen Schwarzanteil")
        elif black_pixel_ratio > 0.1:
            # checked
            result["antwort"].append({"wert": checkbox["wert"], "checked": True})
            orig_img = cv2.circle(orig_img, (x_center + xl, y_center + yo), inner_radius, (0, 255, 0), 2)
        else:
            # not checked
            result["antwort"].append({"wert": checkbox["wert"], "checked": False})
            orig_img = cv2.circle(orig_img, (x_center + xl, y_center + yo), inner_radius, (0, 0, 255), 2)

    return result, orig_img  

def handle_single_choice(bw_img, orig_img, frage):
    result, orig_img = handle_multiple_choice(bw_img, orig_img, frage)
    
    # Konsistenzprüfung
    count_true = sum(1 for checkbox in result["antwort"] if checkbox["checked"])
    if count_true != 1:
        raise Exception(f"Falsche Anzahl von Kreuzen: {count_true}")
    
    return result, orig_img