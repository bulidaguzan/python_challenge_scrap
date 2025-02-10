# src/main.py

import os
import time
from scraper.product_scraper import ProductScraper
from database.db_manager import DatabaseManager
from utils.image_processor import ImageProcessor
import config


def main():
    # Check if database exists
    if os.path.exists(config.DB_NAME):
        print(f"Database {config.DB_NAME} already exists. Skipping execution.")
        return

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
            # Store in database
            db_manager.store_product(product)

            # Process images if categories exist
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
    db_manager.query_and_print_products()


if __name__ == "__main__":
    main()
