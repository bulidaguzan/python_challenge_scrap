from setuptools import setup, find_packages

setup(
    name="product_scraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "Pillow>=10.2.0",
        "beautifulsoup4>=4.12.3",
        "pytest>=8.0.0",
        "pytest-cov>=4.1.0",
    ],
)
