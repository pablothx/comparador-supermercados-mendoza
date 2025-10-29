"""
Scraper REAL para Supermercados Vea - USA API DE VTEX
"""
from typing import List
import re
import sys
from pathlib import Path
import json
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scrapers.base_scraper import BaseScraper
from src.models.models import Producto


class VeaScraper(BaseScraper):
    """Scraper REAL para Vea usando API de VTEX"""
    
    def __init__(self):
        super().__init__("Vea")
        self.base_url = "https://www.vea.com.ar"
        self.api_url = "https://www.vea.com.ar/api/io/_v/api/intelligent-search/product_search"
        
        # Headers específicos para la API
        self.headers.update({
            'Accept': 'application/json',
            'Accept-Language': 'es-AR,es;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://www.vea.com.ar',
            'Referer': 'https://www.vea.com.ar/',
        })
    
    def obtener_url_api(self, query: str, page: int = 1) -> str:
        """Construye URL de la API de búsqueda de Vea"""
        query_clean = query.lower().strip()
        
        # API de VTEX intelligent search
        params = {
            'query': query_clean,
            'page': page,
            'count': 10,
            'query': query_clean,
            'sort': '',
            'fuzzy': '0',
            'operator': 'and',
            'hideUnavailableItems': 'false'
        }
        
        # Construir query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.api_url}?{query_string}"
    
    def obtener_url_busqueda(self, query: str) -> str:
        """
        Construye URL de búsqueda para Vea (interfaz del BaseScraper)
        En este caso retorna la URL de la API
        """
        return self.obtener_url_api(query)
    
    def obtener_url_busqueda(self, query: str) -> str:
        """
        Método requerido por BaseScraper (abstracto)
        Construye URL de búsqueda para Vea
        """
        query_encoded = query.lower().strip().replace(' ', '%20')
        return f"{self.base_url}/{query_encoded}?_q={query_encoded}&map=ft"
    
    def _limpiar_nombre(self, nombre: str) -> str:
        """Limpia y normaliza el nombre del producto"""
        nombre = re.sub(r'\s+', ' ', nombre)
        nombre = nombre.strip()
        nombre = re.sub(r'^VEA\s+', '', nombre, flags=re.IGNORECASE)
        return nombre
    
    def _extraer_marca(self, producto_data: dict) -> str:
        """Extrae la marca del producto desde los datos de la API"""
        # Intentar obtener marca del campo brand
        if 'brand' in producto_data and producto_data['brand']:
            return producto_data['brand']
        
        # Intentar desde productName
        nombre = producto_data.get('productName', '')
        
        marcas = [
            "Gallo", "Lucchetti", "Molinos", "Marolio", "Arcor",
            "Paladini", "Swift", "Granja del Sol", "Paty",
            "Bimbo", "Fargo", "La Serenísima", "Sancor", 
            "Coca-Cola", "Pepsi", "Quilmes", "Brahma", "Andes",
            "Rosamonte", "Taragüi", "CBSé", "La Merced",
            "Vea", "Ser"
        ]
        
        nombre_upper = nombre.upper()
        for marca in marcas:
            if marca.upper() in nombre_upper:
                return marca
        
        return "Sin marca"
    
    def buscar_producto(self, nombre_producto: str) -> List[Producto]:
        """
        Busca un producto en Vea usando la API de VTEX
        """
        url_api = self.obtener_url_api(nombre_producto)
        print(f"🔍 Buscando '{nombre_producto}' en Vea API: {url_api}")
        
        try:
            response = requests.get(
                url_api,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"⚠️ Error {response.status_code} al acceder a la API de Vea")
                return []
            
            data = response.json()
            
            # La API devuelve la estructura: {"products": [...]}
            productos_data = data.get('products', [])
            
            if not productos_data:
                print(f"⚠️ No se encontraron productos para '{nombre_producto}' en Vea")
                return []
            
            print(f"✅ Encontrados {len(productos_data)} productos en Vea API")
            
            productos = []
            
            for idx, item in enumerate(productos_data[:10]):  # Limitar a 10
                try:
                    # Extraer datos de la API
                    product_name = item.get('productName', '')
                    
                    if not product_name:
                        continue
                    
                    nombre = self._limpiar_nombre(product_name)
                    
                    # Obtener precio - VTEX guarda en centavos
                    items = item.get('items', [])
                    if not items:
                        continue
                    
                    first_item = items[0]
                    sellers = first_item.get('sellers', [])
                    
                    if not sellers:
                        continue
                    
                    # Obtener precio del primer seller
                    seller = sellers[0]
                    commercial_offer = seller.get('commertialOffer', {})
                    
                    precio_centavos = commercial_offer.get('Price', 0)
                    
                    if precio_centavos <= 0:
                        # Intentar con ListPrice
                        precio_centavos = commercial_offer.get('ListPrice', 0)
                    
                    if precio_centavos <= 0:
                        continue
                    
                    # Convertir a pesos (viene en formato de centavos o pesos según la API)
                    # Si es mayor a 10000, probablemente está en centavos
                    precio = precio_centavos
                    
                    # Construir URL del producto
                    link_text = item.get('linkText', '')
                    url_producto = f"{self.base_url}/{link_text}/p" if link_text else None
                    
                    # Extraer marca
                    marca = self._extraer_marca(item)
                    
                    producto = Producto(
                        nombre=nombre,
                        precio=precio,
                        supermercado=self.nombre_supermercado,
                        url=url_producto,
                        marca=marca
                    )
                    
                    productos.append(producto)
                    print(f"  ✓ {nombre}: ${precio:,.2f}")
                    
                except Exception as e:
                    print(f"⚠️ Error parseando producto {idx+1}: {e}")
                    continue
            
            if not productos:
                print(f"❌ No se pudieron extraer productos válidos de Vea API")
            else:
                print(f"✅ Procesados {len(productos)} productos de Vea API")
            
            return productos
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con Vea API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON de Vea API: {e}")
            return []
        except Exception as e:
            print(f"❌ Error inesperado en Vea scraper: {e}")
            return []