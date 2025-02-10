# src/database/db_manager.py

import sqlite3
import csv
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime


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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def get_existing_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an existing product from the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT 
                    product_id, name, description, price, image_url,
                    sale_price, out_of_stock, categories, source_url
                FROM products 
                WHERE product_id = ?
            """,
                (product_id,),
            )
            row = cursor.fetchone()

            if row:
                return {
                    "product_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "image_url": row[4],
                    "sale_price": row[5],
                    "out_of_stock": row[6],
                    "categories": row[7],
                    "source_url": row[8],
                }
            return None

        finally:
            conn.close()

    def are_products_equal(
        self, product1: Dict[str, Any], product2: Dict[str, Any]
    ) -> bool:
        """Compare two products to check if they are effectively the same."""
        # Lista de campos a comparar
        fields_to_compare = [
            "name",
            "description",
            "price",
            "image_url",
            "sale_price",
            "out_of_stock",
            "categories",
            "source_url",
        ]

        for field in fields_to_compare:
            val1 = product1.get(field)
            val2 = product2.get(field)

            # Manejo especial para campos numéricos
            if field in ["price", "sale_price"]:
                # Si ambos son None o 0, considerarlos iguales
                if (not val1 or val1 == 0) and (not val2 or val2 == 0):
                    continue
                # Si solo uno es None/0, son diferentes
                if not val1 or not val2:
                    return False
                # Comparar con tolerancia para números flotantes
                if abs(float(val1) - float(val2)) > 0.01:
                    return False
                continue

            # Para el resto de campos, comparación directa
            if val1 != val2:
                return False

        return True

    def store_product(self, product: Dict[str, Any]) -> bool:
        """
        Store a single product in the database.
        Returns True if product was stored/updated, False if it was skipped.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Verificar si el producto ya existe
            existing_product = self.get_existing_product(product["product_id"])

            # Si el producto existe y es igual, lo saltamos
            if existing_product and self.are_products_equal(existing_product, product):
                print(f"Skipping unchanged product: {product['product_id']}")
                return False

            # Si no existe o es diferente, lo actualizamos
            current_time = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT OR REPLACE INTO products 
                (product_id, name, description, price, image_url, 
                sale_price, out_of_stock, categories, source_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    current_time,
                ),
            )

            conn.commit()
            action = "Updated" if existing_product else "Inserted"
            print(f"{action} product: {product['product_id']}")
            return True

        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return False

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
                        SELECT 
                            product_id, name, description, price, image_url,
                            sale_price, out_of_stock, categories, source_url,
                            created_at, updated_at
                        FROM products 
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
                        "Created At",
                        "Updated At",
                    ]
                    writer.writerow(headers)

                    for product in products:
                        writer.writerow(product)

        except sqlite3.Error as e:
            print(f"Error querying database: {str(e)}")

        finally:
            conn.close()
