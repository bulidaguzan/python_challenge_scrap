# src/database/db_manager.py

import sqlite3
import csv
import sys
from typing import List, Dict, Any


class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name

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

    def store_product(self, product: Dict[str, Any]):
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

                    cursor.execute(
                        """
                        SELECT * FROM products 
                        WHERE categories LIKE ?
                        ORDER BY price DESC, name ASC
                    """,
                        (f"%{category}%",),
                    )

                    products = cursor.fetchall()

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
