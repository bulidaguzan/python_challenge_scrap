# src/config.py

# URLs y endpoints
BASE_URL = "https://sandbox.oxylabs.io/products"

# Configuración de la base de datos
DB_NAME = "products.db"

# Configuración de carpetas
RAW_IMAGES_FOLDER = "product_raw_images"
PROCESSED_IMAGES_FOLDER = "product_images"

# Tamaños de imagen
IMAGE_SIZES = [(100, 100), (500, 500), (2000, 2000)]

# Headers para requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Tiempo de espera entre requests
REQUEST_DELAY = 1  # segundos
