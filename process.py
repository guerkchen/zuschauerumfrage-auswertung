#!/usr/local/bin/python3
import json
import os
import glob
import sys
import argparse
from datetime import datetime
from lib.preprocess import *
from lib.question_text import *
from lib.question_choice import *
from lib.json_to_csv import *

def handle_image(img_path, umfragebogen):
    # Bild einlesen
    gray_img, orig_img = read_img(img_path)

    try:
        matrix, orig_img = get_affine_transform_matrix(gray_img, umfragebogen, orig_img)
        gray_img, orig_img = transform_images(gray_img, orig_img, matrix)
    except Exception as e:
        print(f"ImgPath: " + img_path + ": " + str(e))

    result = []
    for frage in umfragebogen["fragen"]:
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

    # Debug output
    debug_file = os.path.join("debug/", img_path)
    debug_dir = os.path.dirname(debug_file)
    os.makedirs(debug_dir, exist_ok=True)
    cv2.imwrite(debug_file, orig_img)

    return result

def handle_folder(input_path, output_path, umfragebogen_path):
    # Open and read the JSON file
    with open(umfragebogen_path, "r", encoding="utf-8") as file:
        umfragebogen = json.load(file)  # Load JSON into a Python dictionary

    # Create Debug folder

    

    jpg_files = glob.glob(os.path.join(input_path, "*.jpg"))
    result = {}
    for img_path in jpg_files:
        result_img = handle_image(img_path, umfragebogen)
        result[img_path] = result_img

    # JSON in eine Datei schreiben
    date_str = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    filename = os.path.join(output_path, f"auswertung_{date_str}.json")
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    
    # Convert JSON to CSV
    json_to_csv(umfragebogen, result, output_path)

def main():
    parser = argparse.ArgumentParser(description="Process survey images.")
    parser.add_argument("input_path", help="Path to the input folder containing images")
    parser.add_argument("output_path", help="Path to the output folder for results")
    parser.add_argument("umfragebogen_path", help="Path to the JSON file with survey data")
    args = parser.parse_args()

    handle_folder(args.input_path, args.output_path, args.umfragebogen_path)

if __name__ == "__main__":
    main()