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
        print(f"Aruco Marker nicht gefunden")

    return corners, ids

def rotate_img(gray_img, orig_img):
    corners, _ = find_aruco(gray_img)

    # find rotation according to markers
    # all markers should be orientated to the right way, so the edges of the markers are used to reorientated the image
    angles_rad = []
    for corner in corners:
        idx = corner[0]
        #idx = corners[np.where(ids == i)[0][0]][0]
        angles_rad.append(math.atan2(idx[1][1] - idx[0][1], idx[1][0] - idx[0][0]))
        angles_rad.append(math.atan2(idx[1][0] - idx[2][0], idx[2][1] - idx[1][1]))
        angles_rad.append(math.atan2(idx[2][1] - idx[3][1], idx[2][0] - idx[3][0]))
        angles_rad.append(math.atan2(idx[0][0] - idx[3][0], idx[3][1] - idx[0][1]))

    # rotate image
    (old_h, old_w) = gray_img.shape[:2]
    center = (old_w // 2, old_h // 2)  # Calculate center of the image
    # Compute mean using vector approach
    angle_rad = np.arctan2(np.mean(np.sin(angles_rad)), np.mean(np.cos(angles_rad)))
    new_w = int(abs(old_w * math.cos(angle_rad)) + abs(old_h * math.sin(angle_rad)))
    new_h = int(abs(old_w * math.sin(angle_rad)) + abs(old_h * math.cos(angle_rad)))
    rotation_matrix = cv2.getRotationMatrix2D(center, math.degrees(angle_rad), 1.0)
    # Update der Transformationsmatrix für die neue Bildgröße
    rotation_matrix[0, 2] += (new_w - old_w) / 2
    rotation_matrix[1, 2] += (new_h - old_h) / 2

    bw_img_rotated = cv2.warpAffine(gray_img, rotation_matrix, (new_w, new_h))
    orig_img_rotated = cv2.warpAffine(orig_img, rotation_matrix, (new_w, new_h))
    return bw_img_rotated, orig_img_rotated

def get_scale_and_offset(gray_img, data):
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