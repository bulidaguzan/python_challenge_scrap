# src/utils/image_processor.py

import os
from PIL import Image
from io import BytesIO
import requests
from typing import Tuple, List


class ImageProcessor:
    def __init__(
        self, raw_folder: str, processed_folder: str, session: requests.Session
    ):
        self.raw_folder = raw_folder
        self.processed_folder = processed_folder
        self.session = session

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize the filename by removing/replacing invalid characters."""
        sanitized = filename.strip()
        sanitized = sanitized.replace(" ", "_")
        sanitized = sanitized.replace("/", "_")
        sanitized = sanitized.replace("\\", "_")
        sanitized = sanitized.replace(":", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "_-")
        return sanitized

    def download_image(
        self, image_url: str, category: str, product_id: str, headers: dict
    ) -> str:
        """Download image and return the path where it was saved."""
        try:
            print(f"Downloading image from: {image_url}")
            response = self.session.get(image_url, headers=headers)
            response.raise_for_status()

            os.makedirs(self.raw_folder, exist_ok=True)
            safe_category = self.sanitize_filename(category)

            # Handle SVG images
            if (
                "svg" in response.headers.get("content-type", "").lower()
                or response.content.startswith(b"<?xml")
                or response.content.startswith(b"<svg")
            ):

                filename = f"{safe_category}_{product_id}.svg"
                filepath = os.path.join(self.raw_folder, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return filepath

            # Handle regular images
            filename = f"{safe_category}_{product_id}_original"
            filepath = os.path.join(self.raw_folder, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath

        except Exception as e:
            print(f"Error downloading image for product {product_id}: {str(e)}")
            return ""

    def process_image(
        self,
        image_path: str,
        category: str,
        product_id: str,
        sizes: List[Tuple[int, int]],
    ):
        """Process downloaded image into required sizes."""
        try:
            if not image_path or image_path.endswith(".svg"):
                return

            img = Image.open(image_path)
            safe_category = self.sanitize_filename(category)
            os.makedirs(self.processed_folder, exist_ok=True)

            for size in sizes:
                img_copy = img.copy()
                if img_copy.mode != "RGB":
                    img_copy = img_copy.convert("RGB")

                # Resize maintaining aspect ratio
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)

                # Create new image with exact dimensions
                new_img = Image.new("RGB", size, (255, 255, 255))
                x = (size[0] - img_copy.size[0]) // 2
                y = (size[1] - img_copy.size[1]) // 2
                new_img.paste(img_copy, (x, y))

                filename = f"{safe_category}_{product_id}_{size[0]}x{size[1]}.jpg"
                filepath = os.path.join(self.processed_folder, filename)
                new_img.save(filepath, "JPEG", quality=85)

        except Exception as e:
            print(f"Error processing image for product {product_id}: {str(e)}")
