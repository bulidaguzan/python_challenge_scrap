# tests/test_db_manager.py
import os
import sys
import pytest
import sqlite3

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.database.db_manager import DatabaseManager


@pytest.fixture
def db_manager(test_db_path):
    manager = DatabaseManager(test_db_path)
    manager.setup_database()
    return manager


def test_setup_database(db_manager):
    """Test database initialization."""
    conn = sqlite3.connect(db_manager.db_name)
    cursor = conn.cursor()

    # Check if products table exists
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='products'
    """
    )

    assert cursor.fetchone() is not None
    conn.close()


def test_store_and_get_product(db_manager, mock_product_data):
    """Test storing and retrieving a product."""
    # Store product
    success = db_manager.store_product(mock_product_data)
    assert success is True

    # Retrieve product
    stored_product = db_manager.get_existing_product(mock_product_data["product_id"])
    assert stored_product is not None
    assert stored_product["name"] == mock_product_data["name"]
    assert stored_product["price"] == mock_product_data["price"]
