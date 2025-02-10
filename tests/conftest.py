import pytest
import os
import sqlite3
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create a temporary database for testing."""
    db_dir = tmp_path_factory.mktemp("db")
    return str(db_dir / "test_products.db")


@pytest.fixture(scope="session")
def test_image_dirs(tmp_path_factory):
    """Create temporary directories for raw and processed images."""
    base_dir = tmp_path_factory.mktemp("images")
    raw_dir = base_dir / "raw"
    processed_dir = base_dir / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    return str(raw_dir), str(processed_dir)


@pytest.fixture
def mock_product_data():
    """Sample product data for testing."""
    return {
        "product_id": "test123",
        "name": "Test Product",
        "description": "Test Description",
        "price": 99.99,
        "image_url": "https://example.com/image.jpg",
        "sale_price": None,
        "out_of_stock": False,
        "categories": "Electronics,Gadgets",
        "source_url": "https://example.com/product/test123",
    }


@pytest.fixture
def mock_html_content():
    """Sample HTML content for testing the scraper."""
    return """
    <div class="product-card">
        <a class="card-header" href="/products/test123">
            <h4 class="title">Test Product</h4>
        </a>
        <p class="description">Test Description</p>
        <div class="price-wrapper">99.99€</div>
        <span class="css-1pewyd6">Electronics</span>
        <span class="css-1pewyd6">Gadgets</span>
        <noscript>
            <img src="https://example.com/image.jpg" alt="Test Product">
        </noscript>
    </div>
    """
