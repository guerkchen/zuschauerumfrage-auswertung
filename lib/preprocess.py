import cv2
import math
import numpy as np

# ArUco-Dictionary laden
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

def find_aruco(gray_img):
    # ArUco-Marker suchen
    corners, ids, _ = detector.detectMarkers(gray_img)

    if ids is None or not 0 in ids or not 1 in ids:
        raise Exception(f"Aruco Marker nicht gefunden {ids}")

    return corners, ids

def remove_transparency(png_image):
    if png_image.shape[2] == 4:  # Falls Alpha-Kanal existiert
        alpha = png_image[:, :, 3]  # Alpha-Kanal extrahieren
        gray = cv2.cvtColor(png_image[:, :, :3], cv2.COLOR_BGR2GRAY)
        gray[alpha == 0] = 255  # Transparente Bereiche weiß setzen
    else:
        gray = cv2.cvtColor(png_image, cv2.COLOR_BGR2GRAY)
    return gray

def find_png(gray_img, png_path):
    # read png
    template = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
    
    # Transparenz entfernen und in Graustufen umwandeln
    template_gray = remove_transparency(template)
    
    # SIFT-Feature-Extraktion
    sift = cv2.SIFT_create()
    kp_doc, des_doc = sift.detectAndCompute(gray_img, None)
    kp_temp, des_temp = sift.detectAndCompute(template_gray, None)
    
    # Matcher (FLANN-basierter Matcher für schnellere Suche)
    index_params = dict(algorithm=1, trees=5)  # FLANN-Parameter
    search_params = dict(checks=50)  # Anzahl der Prüfungen
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Features vergleichen
    matches = flann.knnMatch(des_temp, des_doc, k=2)
    
    # Gute Übereinstimmungen nach Lowe’s Ratio-Test filtern
    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
    
    if len(good_matches) > 4:  # Mindestens 4 Punkte für Homographie notwendig
        # Extrahierte Punkte für Homographie-Matrix
        src_pts = np.float32([kp_temp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_doc[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Homographie berechnen
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        # Eckpunkte des Musters transformieren
        h, w = template_gray.shape
        pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # Muster zurückgeben
        return dst[:, 0, :]
    else:
        raise Exception(f"Kein passendes Muster {png_path} gefunden.")
    
def compute_center(x, y, w, h):
    center_x = x + w / 2
    center_y = y + h / 2
    return [center_x, center_y]
    
def get_affine_transform_matrix(gray_img, data, orig_img):
    # SOLL
    markers = data["markers"]
    png = data["pngs"][0]

    pts_soll = np.array([
        compute_center(png["x"], png["y"], png["w"], png["h"]), # Png
        compute_center(markers["0"]["x"], markers["0"]["y"],markers["0"]["w"],markers["0"]["h"]), # aruco Marker 0
        compute_center(markers["1"]["x"], markers["1"]["y"],markers["1"]["w"],markers["1"]["h"]) # aruco Marker 1
    ], dtype=np.float32)

    # IST
    aruco_corners, aruco_ids = find_aruco(gray_img)
    png_corners = find_png(gray_img, png["filename"])

    cv2.polylines(orig_img, [np.int32(png_corners)], True, (255, 0, 0), 3)
    cv2.polylines(orig_img, [np.int32(aruco_corners[0])], True, (255, 0, 0), 3)
    cv2.polylines(orig_img, [np.int32(aruco_corners[1])], True, (255, 0, 0), 3)

    center_png = np.mean(png_corners, axis=0)
    center_aruco_0 = np.mean(aruco_corners[np.where(aruco_ids == 0)[0][0]][0], axis=0)
    center_aruco_1 = np.mean(aruco_corners[np.where(aruco_ids == 1)[0][0]][0], axis=0)

    cv2.circle(orig_img, center_png.astype(int), 2, (255, 255, 0), -1)
    cv2.circle(orig_img, center_aruco_0.astype(int), 2, (255, 255, 0), -1)
    cv2.circle(orig_img, center_aruco_1.astype(int), 2, (255, 255, 0), -1)

    pts_ist = np.array([
        center_png, # Png
        center_aruco_0, # aruco Marker 0
        center_aruco_1 # aruco Marker 1
    ], dtype=np.float32)

    # Matrix berechnen
    #matrix = cv2.getAffineTransform(pts_soll, pts_ist)
    matrix = cv2.getAffineTransform(pts_ist, pts_soll)
    return matrix, orig_img

def transform_images(gray_img, orig_img, matrix):
    # Neue Größe bestimmen
    h, w = gray_img.shape[:2] # ist fuer orig_img identisch
    corners = np.array([[0, 0], [w, 0], [0, h], [w, h]], dtype=np.float32)
    transformed_corners = cv2.transform(np.array([corners]), matrix)[0]
    min_x = np.min(transformed_corners[:, 0])
    max_x = np.max(transformed_corners[:, 0])
    min_y = np.min(transformed_corners[:, 1])
    max_y = np.max(transformed_corners[:, 1])
    new_width = int(max_x - min_x)
    new_height = int(max_y - min_y)

    # Transformation anwenden
    gray_img = cv2.warpAffine(gray_img, matrix, (new_width, new_height))
    orig_img = cv2.warpAffine(orig_img, matrix, (new_width, new_height))

    return gray_img, orig_img
    # compute scale factor for json values
    corners, ids = find_aruco(gray_img)

    idx0 = corners[np.where(ids == 0)[0][0]][0][0]
    idx1 = corners[np.where(ids == 1)[0][0]][0][0]

    scale_factor_x = abs((idx1[0] - idx0[0]) / (data["markers"]["1"]["x"] - data["markers"]["0"]["x"]))
    scale_factor_y = abs((idx1[1] - idx0[1]) / (data["markers"]["1"]["y"] - data["markers"]["0"]["y"]))
    scale_factor = (scale_factor_x + scale_factor_y) / 2

    offset_x = ((idx0[0] - (data["markers"]["0"]["x"] * scale_factor)) + (idx1[0] - (data["markers"]["1"]["x"] * scale_factor))) / 2
    offset_y = ((idx0[1] - (data["markers"]["0"]["y"] * scale_factor)) + (idx1[1] - (data["markers"]["1"]["y"] * scale_factor))) / 2
    return scale_factor, offset_x, offset_y

def read_img(img_path):
    img = cv2.imread(img_path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), img
