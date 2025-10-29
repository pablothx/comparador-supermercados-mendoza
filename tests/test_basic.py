import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.atomo_scraper import AtomoScraper
from src.scrapers.vea_scraper import VeaScraper

# Test Atomo
atomo = AtomoScraper()
productos = atomo.buscar_producto("hamburguesa")
for p in productos:
    print(f"{p.nombre} - ${p.precio} - {p.marca}")

# Test Vea
vea = VeaScraper()
productos = vea.buscar_producto("gaseosa")
for p in productos:
    print(f"{p.nombre} - ${p.precio} - {p.marca}")