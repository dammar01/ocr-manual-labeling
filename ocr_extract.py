import easyocr
import json
from pathlib import Path


def ocr_folder_for_paddleocr(folder_path: str, output_path: str):
    reader = easyocr.Reader(["en"])
    folder = Path(folder_path)
    output_file = Path(output_path) / f"{folder.name}.json"
    results = []
    for image_path in folder.glob("*.jpg"):
        ocr_result = reader.readtext(str(image_path))
        label = ocr_result[0][1] if ocr_result else ""
        results.append({"image_path": image_path.name, "label": label})
        print(f"{image_path.name} predicted as {label}")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"OCR results saved to {output_file}")


folder_sample = "total_damage"
datasets_path = f"./datasets/sample/{folder_sample}"
output_path = "./datasets/sample_labels/"
ocr_folder_for_paddleocr(datasets_path, output_path)
