# Manual Labeling Tool for OCR Dataset

This repository contains a Python-based manual labeling tool for refining OCR-extracted text data. The tool uses EasyOCR to extract text from images and provides an interface for manual validation, making it suitable for fine-tuning recognation OCR models such as PaddleOCR.

## Features

- Extract text from images using EasyOCR
- Store extracted labels in JSON format
- Manually validate and edit OCR results
- Generate a clean dataset for fine-tuning recognation OCR models

## Installation & Setup

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Extract Text Labels from Images

Run the following command to extract text from images and store them in JSON format:

```bash
python ocr_extract.py
```

This will process images from datasets/sample/name_bbox/image and generate label files in datasets/sample_labels/name_bbox.json.

### 2. Manually Validate and Edit Labels

To manually review and adjust OCR results:

```bash
python labeling.py
```

This will open an interactive tool allowing you to edit incorrect labels before saving the final dataset.

## Output Format

The labeled dataset is stored in JSON files with the following structure:

```json
[
  {
    "image_path": "file_name.jpg",
    "label": "predicted_text"
  }
]
```

These files will be used as ground truth for fine-tuning OCR models.

## Folder Structure

```
project_root/
│── datasets/
│   ├── sample/
│   │   ├── name_bbox/
│   │   │   ├── image1.jpg
│   │   │   ├── image2.jpg
│   ├── sample_labels/
│   │   ├── name_bbox.json
│── ocr_extract.py
│── labeling.py
│── requirements.txt
│── README.md
```

## Notes

- Ensure all images are placed in the correct folder before running ocr_extract.py.
- The labeling tool supports interactive corrections to improve dataset accuracy
- The final dataset can be used to train a custom OCR model in PaddleOCR.

## License

This project is open-source and can be modified as needed.
