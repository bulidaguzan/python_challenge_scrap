# src/scraper/product_scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time


class ProductScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def parse_product_data(self, product_elem) -> Optional[Dict]:
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
            price = float(price_text.replace("€", "").replace(",", ".").strip())

            # Extract categories
            categories = []
            category_spans = product_elem.find_all("span", class_="css-1pewyd6")
            for span in category_spans:
                categories.append(span.text.strip())

            # Extract image URL
            noscript = product_elem.find("noscript")
            if noscript:
                img_noscript = noscript.find("img")
                if img_noscript:
                    image_url = img_noscript.get("src")
                    if not image_url.startswith("http"):
                        image_url = f"https://sandbox.oxylabs.io{image_url}"

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
                "out_of_stock": False,  # Not available in current data
                "categories": ",".join(categories),
                "source_url": source_url,
            }
        except Exception as e:
            print(f"Error parsing product: {str(e)}")
            return None

    def fetch_products(self, page: int = 1) -> List[Dict]:
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
