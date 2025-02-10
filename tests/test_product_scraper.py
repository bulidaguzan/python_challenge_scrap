# tests/test_product_scraper.py
import os
import sys
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scraper.product_scraper import ProductScraper


@pytest.fixture
def scraper():
    return ProductScraper("https://sandbox.oxylabs.io/products")


@pytest.fixture
def mock_response(mock_html_content):
    mock_resp = Mock()
    mock_resp.text = mock_html_content
    mock_resp.raise_for_status = Mock()
    return mock_resp


def test_parse_product_data(scraper, mock_html_content):
    """Test parsing of product data from HTML."""
    soup = BeautifulSoup(mock_html_content, "html.parser")
    product_elem = soup.find("div", class_="product-card")

    product_data = scraper.parse_product_data(product_elem)

    assert product_data is not None
    assert product_data["product_id"] == "test123"
    assert product_data["name"] == "Test Product"
    assert product_data["description"] == "Test Description"
    assert product_data["price"] == 99.99
    assert product_data["categories"] == "Electronics,Gadgets"
    assert product_data["image_url"] == "https://example.com/image.jpg"
