# E-commerce Product Scraper

A Python application that scrapes product data from an e-commerce website, stores it in a SQLite database, and processes product images in multiple sizes.

## Features

- Scrapes product data from https://sandbox.oxylabs.io/products including:
  - Product ID
  - Name
  - Description
  - Price
  - Images
  - Sale price (when available)
  - Out of stock status (when available)
  - Categories
  - Source URL
- Stores all product data in a SQLite database
- Downloads product images (image processing functionality coming soon)
- Supports incremental updates (only processes changed products)
- Generates CSV reports of products by category
- Handles SVG and regular image formats
- Includes rate limiting to be respectful to the target server

## Project Structure

```
├── src/
│   ├── database/
│   │   ├── db_manager.py    # Database operations
│   │   └── report.py        # Product reporting functionality
│   ├── scraper/
│   │   └── product_scraper.py   # Web scraping logic
│   ├── utils/
│   │   └── image_processor.py   # Image processing utilities
│   └── config.py            # Configuration settings
├── main.py                  # Main application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bulidaguzan/python_challenge_scrap
   cd python_challenge_scrap
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python3 main.py
```

## Configuration

The application's behavior can be customized by modifying `config.py`:

- `BASE_URL`: Target e-commerce website URL
- `DB_NAME`: SQLite database filename
- `RAW_IMAGES_FOLDER`: Directory for storing original downloaded images
- `PROCESSED_IMAGES_FOLDER`: Directory for storing processed images (cooming soon)
- `REQUEST_DELAY`: Delay between requests to the server (in seconds)

## Output

After running the application, you'll find:

1. A SQLite database (`products.db`) containing all product information
2. A `product_images` folder containing downloaded images
3. Console output showing:
   - Scraping progress
   - Product processing status
   - CSV-formatted product reports grouped by category

## Error Handling

The application includes robust error handling for:
- Network issues
- Image processing failures
- Database operations
- File system operations

Failed operations are logged to the console but don't stop the application's execution.

## Performance Considerations

- Uses session management for efficient HTTP connections
- Implements incremental updates to avoid reprocessing unchanged products
- Includes rate limiting to prevent server overload

## Dependencies

- `requests`: HTTP client for web scraping
- `Pillow`: Image processing library
- `beautifulsoup4`: HTML parsing and data extraction
- `sqlite3`: Database management (included in Python standard library)
