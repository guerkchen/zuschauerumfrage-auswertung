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

    gray_img, orig_img = rotate_img(gray_img, orig_img)

    # Open and read the JSON file
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON into a Python dictionary

    scale_factor, offset_x, offset_y = get_scale_and_offset(gray_img, data)

    result = []
    for frage in data["fragen"]:
        try:
            if frage["type"] == "single-choice":
                frage_result, orig_img = handle_single_choice(gray_img, orig_img, frage, offset_x, offset_y, scale_factor)
                result.append(frage_result)
            elif frage["type"] == "multiple-choice":
                frage_result, orig_img = handle_multiple_choice(gray_img, orig_img, frage, offset_x, offset_y, scale_factor)
                result.append(frage_result)
            elif frage["type"] == "text":
                #frage_result, orig_img = handle_text(gray_img, orig_img, frage, offset_x, offset_y, scale_factor)
                #result.append(frage_result)
                print("skip text")
            else:
                print("type " + frage["type"] + " not implemented yet")
        except Exception as e:
            print(f"ImgPath: " + img_path + " Frage: " + frage["wert"] + ": " + str(e))

    (h, w) = gray_img.shape[:2]
    for step in range(1, w, math.floor(w / 20)):
        orig_img = cv2.line(orig_img, (step, 0), (step, h), 0, 2)
    cv2.imwrite(os.path.join("debug/", img_path), orig_img)
    return result

def handle_folder(input_path, output_path):
    jpg_files = glob.glob(os.path.join(input_path, "*.jpg"))
    result = {}
    for img_path in jpg_files:
        result_img = handle_image(img_path, "umfrageboegen/umfragebogen1.json")
        result[img_path] = result_img

    # JSON in eine Datei schreiben
    date_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(output_path, f"auswertung_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

def main():
    handle_folder("input/", "output/")
    #handle_image("input/2025-02-13_54tv4QEa.jpg", "umfragebogen1.json")

main()