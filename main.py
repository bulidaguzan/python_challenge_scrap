import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import json
import csv
import sys
import time


class ProductScraper:
    def __init__(self, base_url: str, db_name: str = "products.db"):
        self.base_url = base_url
        self.db_name = db_name
        self.session = requests.Session()
        self.image_folder = "product_images"

    def setup_database(self):
        """Create SQLite database and tables if they don't exist."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                image_url TEXT,
                sale_price REAL,
                out_of_stock INTEGER,
                categories TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def parse_product_data(self, product_elem):
        """Extract product data from HTML element."""
        try:
            # Get product ID from href
            product_link = product_elem.find("a", class_="card-header")
            product_id = product_link["href"].split("/")[-1] if product_link else None

            # Extract product name
            name_elem = product_elem.find("h4", class_="title")
            name = name_elem.text.strip() if name_elem else ""

            # Extract description
            desc_elem = product_elem.find("p", class_="description")
            description = desc_elem.text.strip() if desc_elem else ""

            # Extract price
            price_elem = product_elem.find("div", class_="price-wrapper")
            price_text = price_elem.text.strip() if price_elem else "0"
            # Convert European price format (91,99 €) to float (91.99)
            price = float(price_text.replace("€", "").replace(",", ".").strip())

            # Extract categories
            categories = []
            category_spans = product_elem.find_all("span", class_="css-1pewyd6")
            for span in category_spans:
                categories.append(span.text.strip())

            # Extract image URL from noscript srcset
            noscript = product_elem.find("noscript")
            if noscript:
                img_noscript = noscript.find("img")
                if img_noscript:
                    image_url = img_noscript.get("src")
                    if not image_url.startswith("http"):
                        image_url = f"https://sandbox.oxylabs.io{image_url}"

            # Check if out of stock
            stock_status = False  # We'll need to update this based on actual data

            # Build source URL
            source_url = (
                f"{self.base_url}/{product_id}" if product_id else self.base_url
            )

            return {
                "product_id": product_id,
                "name": name,
                "description": description,
                "price": price,
                "image_url": image_url,
                "sale_price": None,  # Not available in current data
                "out_of_stock": stock_status,
                "categories": ",".join(categories),
                "source_url": source_url,
            }
        except Exception as e:
            print(f"Error parsing product: {str(e)}")
            return None

    def fetch_products(self, page=1):
        """Fetch products from a specific page."""
        try:
            url = f"{self.base_url}?page={page}"
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            product_cards = soup.find_all("div", class_="product-card")

            products = []
            for card in product_cards:
                product_data = self.parse_product_data(card)
                if product_data:
                    products.append(product_data)

            return products

        except requests.RequestException as e:
            print(f"Error fetching page {page}: {str(e)}")
            return []

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize the filename by removing/replacing invalid characters."""
        # Replace spaces, slashes and other problematic characters
        sanitized = filename.strip()
        sanitized = sanitized.replace(" ", "_")
        sanitized = sanitized.replace("/", "_")
        sanitized = sanitized.replace("\\", "_")
        sanitized = sanitized.replace(":", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "_-")
        return sanitized

    def process_image(self, image_url: str, category: str, product_id: str):
        """Download and process image in required sizes."""
        try:
            response = self.session.get(image_url)
            response.raise_for_status()

            # Create image folder if it doesn't exist
            os.makedirs(self.image_folder, exist_ok=True)
            safe_category = self.sanitize_filename(category)

            # Check if content is SVG
            is_svg = "svg" in response.headers.get(
                "content-type", ""
            ).lower() or response.text.strip().startswith(("<?xml", "<svg"))

            if is_svg:
                # Save SVG directly
                filename = f"{safe_category}_{product_id}.svg"
                filepath = os.path.join(self.image_folder, filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return

            # Process regular images
            img = Image.open(BytesIO(response.content))

            # Process for all required sizes
            sizes = [(100, 100), (500, 500), (2000, 2000)]
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
                filepath = os.path.join(self.image_folder, filename)
                new_img.save(filepath, "JPEG", quality=85)

        except Exception as e:
            print(f"Error processing image for product {product_id}: {str(e)}")

    def store_product(self, product: dict):
        """Store a single product in the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO products 
                (product_id, name, description, price, image_url, 
                sale_price, out_of_stock, categories, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    product["product_id"],
                    product["name"],
                    product["description"],
                    product["price"],
                    product["image_url"],
                    product.get("sale_price"),
                    product["out_of_stock"],
                    product["categories"],
                    product["source_url"],
                ),
            )

            conn.commit()

        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")

        finally:
            conn.close()

    def query_and_print_products(self):
        """Query products by category and print in CSV format."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Get unique categories
            cursor.execute("SELECT DISTINCT categories FROM products")
            category_rows = cursor.fetchall()

            for category_row in category_rows:
                categories = category_row[0].split(",")
                for category in categories:
                    if not category.strip():
                        continue

                    print(f"\nProducts in category: {category}")

                    # Query products for this category, sorted by price and name
                    cursor.execute(
                        """
                        SELECT * FROM products 
                        WHERE categories LIKE ?
                        ORDER BY price DESC, name ASC
                    """,
                        (f"%{category}%",),
                    )

                    products = cursor.fetchall()

                    # Write to CSV
                    writer = csv.writer(sys.stdout)
                    headers = [
                        "ID",
                        "Name",
                        "Description",
                        "Price",
                        "Image URL",
                        "Sale Price",
                        "Out of Stock",
                        "Categories",
                        "Source URL",
                    ]
                    writer.writerow(headers)

                    for product in products:
                        writer.writerow(product[:-1])  # Exclude timestamp

        except sqlite3.Error as e:
            print(f"Error querying database: {str(e)}")

        finally:
            conn.close()

    def run(self):
        """Main execution method."""
        # Check if database exists
        if os.path.exists(self.db_name):
            print(f"Database {self.db_name} already exists. Skipping execution.")
            return

        # Setup database
        self.setup_database()

        # Fetch and process all pages
        page = 1
        while True:
            products = self.fetch_products(page)
            if not products:
                break

            for product in products:
                # Store in database
                self.store_product(product)

                # Process images if categories exist
                if product["categories"]:
                    categories = product["categories"].split(",")
                    for category in categories:
                        if product["image_url"]:  # Only process if image URL exists
                            self.process_image(
                                product["image_url"],
                                category.strip(),
                                product["product_id"],
                            )

            print(f"Processed page {page}")
            page += 1
            time.sleep(1)  # Be nice to the server

        # Query and display results
        self.query_and_print_products()


if __name__ == "__main__":
    BASE_URL = "https://sandbox.oxylabs.io/products"
    scraper = ProductScraper(BASE_URL)
    scraper.run()
