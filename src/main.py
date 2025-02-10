# src/main.py

import os
import time
from scraper.product_scraper import ProductScraper
from database.db_manager import DatabaseManager
from database.report import query_products
from utils.image_processor import ImageProcessor
import config


def should_process_images(db_manager: DatabaseManager, product: dict) -> bool:
    """
    Determina si las imágenes de un producto deben ser procesadas.
    """
    existing_product = db_manager.get_existing_product(product["product_id"])
    if not existing_product:
        return True
    return existing_product["image_url"] != product["image_url"]


def main():
    # Initialize components
    scraper = ProductScraper(config.BASE_URL)
    db_manager = DatabaseManager(config.DB_NAME)
    image_processor = ImageProcessor(
        config.RAW_IMAGES_FOLDER, config.PROCESSED_IMAGES_FOLDER, scraper.session
    )

    # Setup database
    db_manager.setup_database()

    # Fetch and process all pages
    page = 1
    while True:
        products = scraper.fetch_products(page)
        if not products:
            break

        for product in products:
            # Check if product needs to be updated
            existing_product = db_manager.get_existing_product(product["product_id"])

            if existing_product and db_manager.are_products_equal(
                existing_product, product
            ):
                print(f"Skipping unchanged product: {product['product_id']}")
                continue
            else:
                # Store in database
                db_manager.store_product(product)

                # Process images if categories exist and images need processing
                if product["categories"] and product["image_url"]:
                    categories = product["categories"].split(",")
                    for category in categories:
                        category = category.strip()
                        if not category:
                            continue

                    # Download raw image
                    image_path = image_processor.download_image(
                        product["image_url"],
                        category,
                        product["product_id"],
                        config.HEADERS,
                    )

                    # Process image into different sizes
                    if image_path:
                        image_processor.process_image(
                            image_path,
                            category,
                            product["product_id"],
                            config.IMAGE_SIZES,
                        )

        print(f"Processed page {page}")
        page += 1
        time.sleep(config.REQUEST_DELAY)  # Be nice to the server

    # Query and display results
    query_products()


if __name__ == "__main__":
    main()
