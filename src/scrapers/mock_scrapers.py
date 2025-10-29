"""
Scrapers simulados para demo (reemplazar con scrapers reales en producción)
"""
from typing import List
import random
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scrapers.base_scraper import BaseScraper
from src.models.models import Producto


class MockScraper(BaseScraper):
    """Scraper simulado para demo"""
    
    def __init__(self, nombre_supermercado: str, factor_precio: float = 1.0):
        super().__init__(nombre_supermercado)
        self.factor_precio = factor_precio  # Multiplicador de precio base
        
        # Precios base simulados (Argentina, Oct 2025)
        self.precios_base = {
            "arroz": 1200,
            "aceite": 2500,
            "yerba": 3500,
            "azucar": 1100,
            "leche": 900,
            "pan": 800,
            "fideos": 850,
            "harina": 950,
            "sal": 400,
            "cafe": 4500,
            "te": 1200,
            "galletitas": 1500,
            "manteca": 2000,
            "queso": 5500,
            "jamon": 4800,
            "huevos": 3200,
            "pollo": 3500,
            "carne": 8500,
            "hamburguesa": 5500,
            "salchicha": 1300,
            "pancho": 1200,
            "gaseosa": 2800,
            "cerveza": 1500,
            "vino": 4500,
            "agua": 600,
            "jugo": 1800,
            "papas": 950,
            "tomate": 1200,
            "lechuga": 800,
            "cebolla": 650,
            "zanahoria": 700,
            "manzana": 1100,
            "banana": 850,
            "naranja": 950,
            "limpieza": 2200,
            "detergente": 2500,
            "jabon": 1400,
            "shampoo": 3200,
            "pasta_dental": 1900,
            "papel_higienico": 3500,
        }
    
    def obtener_url_busqueda(self, query: str) -> str:
        """Mock URL"""
        return f"https://{self.nombre_supermercado.lower()}.com.ar/search?q={query}"
    
    def buscar_producto(self, nombre_producto: str) -> List[Producto]:
        """
        Simula búsqueda de producto con precios aleatorios realistas
        """
        nombre_lower = nombre_producto.lower()
        
        # Buscar coincidencias en precios base
        resultados = []
        
        for producto_key, precio_base in self.precios_base.items():
            if producto_key in nombre_lower or nombre_lower in producto_key:
                # Aplicar variación aleatoria ±10% y factor del supermercado
                variacion = random.uniform(0.90, 1.10)
                precio_final = precio_base * self.factor_precio * variacion
                
                # Generar variantes (distintas marcas/presentaciones)
                marcas = ["Marca A", "Marca B", "Marca C"]
                
                for i, marca in enumerate(marcas[:2]):  # Solo 2 variantes por producto
                    producto = Producto(
                        nombre=f"{producto_key.title()} {marca}",
                        precio=round(precio_final * (1 + i * 0.05), 2),
                        supermercado=self.nombre_supermercado,
                        marca=marca,
                        url=f"https://{self.nombre_supermercado.lower()}.com.ar/producto/{producto_key}"
                    )
                    resultados.append(producto)
                
                break  # Solo el primer match
        
        return resultados


# Instancias de scrapers simulados con diferentes factores de precio
class CarrefourScraper(MockScraper):
    def __init__(self):
        super().__init__("Carrefour", factor_precio=1.05)  # 5% más caro


class CotoScraper(MockScraper):
    def __init__(self):
        super().__init__("Coto", factor_precio=0.98)  # 2% más barato


class VeaScraper(MockScraper):
    def __init__(self):
        super().__init__("Vea", factor_precio=0.95)  # 5% más barato


class TadicorScraper(MockScraper):
    def __init__(self):
        super().__init__("Tadicor", factor_precio=0.92)  # 8% más barato (mayorista)


class JumboScraper(MockScraper):
    def __init__(self):
        super().__init__("Jumbo", factor_precio=1.08)  # 8% más caro (premium)
