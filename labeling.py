import json
import cv2
import os
import threading
import queue
import time
from typing import List, Dict, Any
from datetime import datetime


class ImageDisplayThread(threading.Thread):
    def __init__(self, command_queue: queue.Queue):
        super().__init__()
        self.command_queue = command_queue
        self.window_name = "OCR Validation"
        self.running = True

    def run(self):
        while self.running:
            try:
                # Check for new commands with timeout
                try:
                    command = self.command_queue.get(timeout=0.1)
                    if command["type"] == "display":
                        self._display_image(command["image_path"])
                    elif command["type"] == "quit":
                        self.running = False
                except queue.Empty:
                    pass

                # Small delay to prevent high CPU usage
                cv2.waitKey(100)

            except Exception as e:
                print(f"Error in display thread: {str(e)}")

        cv2.destroyAllWindows()

    def _display_image(self, image_path: str):
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not load image: {image_path}")
                return
            cv2.imshow(self.window_name, image)

        except Exception as e:
            print(f"Error displaying image: {str(e)}")


class LabelValidator:
    def __init__(self, image_folder: str, label_file: str, output_file: str):
        self.image_folder = image_folder
        self.label_file = label_file
        self.output_file = output_file
        self.backup_dir = os.path.join(os.path.dirname(output_file), "backups")
        self.validated_labels: List[Dict[str, Any]] = []

        # Initialize queue for display thread
        self.command_queue = queue.Queue()

        # Start display thread
        self.display_thread = ImageDisplayThread(self.command_queue)
        self.display_thread.daemon = (
            True  # Make thread daemon so it exits when main program exits
        )
        self.display_thread.start()

    def load_labels(self) -> List[Dict[str, Any]]:
        try:
            with open(self.label_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Label file not found: {self.label_file}")
            return []
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {self.label_file}")
            return []

    def save_progress(
        self, labels_data: List[Dict[str, Any]], is_backup: bool = False
    ) -> None:
        try:
            save_path = self.output_file
            if is_backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(self.backup_dir, f"backup_{timestamp}.json")

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(labels_data, f, indent=4, ensure_ascii=False)
            print(f"\nProgress saved to {save_path}")
        except Exception as e:
            print(f"Error saving progress: {str(e)}")

    def validate_labels(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)

            labels = self.load_labels()
            if not labels:
                return

            total_images = len(labels)
            current_idx = 0

            print(f"\nStarting validation of {total_images} images...")
            print("\nInstructions:")
            print(
                "- Enter new label text and press Enter to update and move to next image"
            )
            print(
                "- Press Enter without text to keep current label and move to next image"
            )
            print("- Type 'back' to go to previous image")
            print("- Type 'save' to save progress")
            print("- Type 'quit' to exit\n")

            while current_idx < total_images:
                entry = labels[current_idx]
                image_path = os.path.join(self.image_folder, entry["image_path"])
                current_label = entry["label"]

                if not os.path.exists(image_path):
                    print(f"Image not found: {image_path}")
                    current_idx += 1
                    continue

                # Display current image
                self.command_queue.put({"type": "display", "image_path": image_path})

                # Show image information
                print(f"\nImage {current_idx + 1}/{total_images}")
                print(f"File: {entry['image_path']}")
                print(f"Current Label: {current_label}")

                # Get user input
                user_input = input("Enter new label (or command): ").strip()

                # Process user input
                if user_input.lower() == "quit":
                    break
                elif user_input.lower() == "back":
                    if current_idx > 0:
                        current_idx -= 1
                    else:
                        print("Already at first image")
                    continue
                elif user_input.lower() == "save":
                    self.save_progress(self.validated_labels)
                    self.save_progress(self.validated_labels, is_backup=True)
                    continue

                # Update label if user entered new text
                label = user_input if user_input else current_label

                # Update validated labels
                if current_idx >= len(self.validated_labels):
                    self.validated_labels.append(
                        {"image_path": entry["image_path"], "label": label}
                    )
                else:
                    self.validated_labels[current_idx] = {
                        "image_path": entry["image_path"],
                        "label": label,
                    }

                # Auto-save every 10 images
                if (current_idx + 1) % 10 == 0:
                    self.save_progress(self.validated_labels, is_backup=True)

                current_idx += 1

            # self.save_progress(self.validated_labels)
            print(f"\nProcessed {len(self.validated_labels)} of {total_images} images")

        except Exception as e:
            print(f"Error in validate_labels: {str(e)}")
        finally:
            # Signal display thread to quit
            self.command_queue.put({"type": "quit"})
            self.display_thread.join(timeout=1)


def main():
    try:
        # Configuration
        name_bbox = "damage"
        base_path = "./datasets"
        image_folder = os.path.join(base_path, "sample", name_bbox)
        label_file = os.path.join(base_path, "sample_labels", f"{name_bbox}.json")
        output_file = os.path.join(base_path, "validated_labels", f"{name_bbox}.json")

        validator = LabelValidator(image_folder, label_file, output_file)
        validator.validate_labels()
    except Exception as e:
        print(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()
