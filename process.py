#!/usr/local/bin/python3
import json
import os
import glob
from datetime import datetime
from lib.preprocess import *
from lib.question_text import *
from lib.question_choice import *

def handle_image(img_path, json_path):
    # Bild einlesen
    gray_img, orig_img = read_img(img_path)

    # Open and read the JSON file
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON into a Python dictionary

    matrix, orig_img = get_affine_transform_matrix(gray_img, data, orig_img)
    gray_img, orig_img = transform_images(gray_img, orig_img, matrix)

    result = []
    for frage in data["fragen"]:
        try:
            if frage["type"] == "single-choice":
                frage_result, orig_img = handle_single_choice(gray_img, orig_img, frage)
                result.append(frage_result)
            elif frage["type"] == "multiple-choice":
                frage_result, orig_img = handle_multiple_choice(gray_img, orig_img, frage)
                result.append(frage_result)
            elif frage["type"] == "text":
                frage_result, orig_img = handle_text(gray_img, orig_img, frage)
                result.append(frage_result)
            else:
                print("type " + frage["type"] + " not implemented yet")
        except Exception as e:
            print(f"ImgPath: " + img_path + " Frage: " + frage["wert"] + ": " + str(e))

    cv2.imwrite(os.path.join("debug/", img_path), orig_img)
    return result

def handle_folder(input_path, output_path):
    jpg_files = glob.glob(os.path.join(input_path, "*.jpg"))
    result = {}
    for img_path in jpg_files:
        result_img = handle_image(img_path, "umfrageboegen/umfragebogen2.json")
        result[img_path] = result_img

    # JSON in eine Datei schreiben
    date_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(output_path, f"auswertung_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

def main():
    handle_folder("input/", "output/")
    #handle_image("input/2025-02-13_YHPYqxWP.jpg", "umfrageboegen/umfragebogen1.json")

main()