import sqlite3
import csv
import sys
import os


def get_project_root():
    """Get the path to the project root directory."""
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels to get to the project root
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return project_root


def get_db_path():
    """Get the full path to the products.db file in project root."""
    return os.path.join(get_project_root(), "products.db")


def query_products():
    """Query products by category and display them in CSV format."""
    db_path = get_db_path()

    if not os.path.exists(db_path):
        print(f"Error: Database does not exist at {db_path}")
        print(
            "Please run the main scraper script first to create and populate the database."
        )
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Get unique categories
        cursor.execute(
            """
            SELECT DISTINCT categories 
            FROM products 
            WHERE categories IS NOT NULL 
            AND categories != ''
        """
        )
        category_rows = cursor.fetchall()

        if not category_rows:
            print("No categories found in the database.")
            return

        # CSV writer setup
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

        # Process each category
        for category_row in category_rows:
            # Split categories as they might be comma-separated
            categories = category_row[0].split(",")

            for category in categories:
                category = category.strip()
                if not category:
                    continue

                print(f"\n\nProducts in category: {category}")
                print("-" * 50)

                # Write headers for this category
                writer.writerow(headers)

                # Query products for this category
                cursor.execute(
                    """
                    SELECT 
                        product_id,
                        name,
                        description,
                        price,
                        image_url,
                        sale_price,
                        out_of_stock,
                        categories,
                        source_url
                    FROM products 
                    WHERE categories LIKE ?
                    ORDER BY price DESC, name ASC
                """,
                    (f"%{category}%",),
                )

                products = cursor.fetchall()
                if not products:
                    print(f"No products found in category: {category}")
                    continue

                # Write product rows
                for product in products:
                    writer.writerow(product)

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}", file=sys.stderr)
    finally:
        conn.close()


if __name__ == "__main__":
    query_products()
