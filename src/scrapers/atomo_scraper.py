"""
Scraper para Atomo Supermercado - MEJORADO
"""
from typing import List
import re
import sys
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scrapers.base_scraper import BaseScraper
from src.models.models import Producto


class AtomoScraper(BaseScraper):
    """Scraper específico para Atomo"""
    
    def __init__(self):
        super().__init__("Atomo")
        self.base_url = "https://atomoconviene.com/atomo-ecommerce"
        
        # Headers mejorados para Atomo
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://atomoconviene.com/'
        }
    
    def obtener_url_busqueda(self, query: str) -> str:
        """Construye URL de búsqueda para Atomo"""
        # Reemplazar espacios con +
        query_encoded = query.replace(' ', '+')
        
        # URL de búsqueda de Atomo
        return f"{self.base_url}/module/ambjolisearch/jolisearch?s={query_encoded}"
    
    def _get_page_atomo(self, url: str):
        """Obtiene página de Atomo con headers apropiados"""
        try:
            print(f"🔍 Buscando en Atomo: {url}")
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 403:
                print(f"⚠️ Atomo bloqueó la petición (403 Forbidden)")
                return None
            
            if response.status_code != 200:
                print(f"⚠️ Error {response.status_code} al acceder a Atomo")
                return None
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con Atomo: {e}")
            return None
        except Exception as e:
            print(f"❌ Error obteniendo página de Atomo: {e}")
            return None
    
    def buscar_producto(self, nombre_producto: str) -> List[Producto]:
        """
        Busca un producto en Atomo
        
        Args:
            nombre_producto: Nombre del producto
            
        Returns:
            Lista de productos encontrados
        """
        url = self.obtener_url_busqueda(nombre_producto)
        soup = self._get_page_atomo(url)
        
        if not soup:
            print(f"⚠️ No se pudo acceder a Atomo para '{nombre_producto}'")
            return []
        
        productos = []
        
        # Buscar productos en la página - PrestaShop structure
        product_items = soup.find_all('article', class_='product-miniature')
        
        if not product_items:
            # Intentar estructura alternativa
            product_items = soup.find_all('div', class_='product-container')
        
        if not product_items:
            # Buscar por atributo itemtype (schema.org)
            product_items = soup.find_all(attrs={'itemtype': 'http://schema.org/Product'})
        
        if not product_items:
            print(f"⚠️ No se encontraron productos para '{nombre_producto}' en Atomo")
            # Debug
            print(f"📊 HTML tiene {len(soup.find_all('div'))} divs")
            return []
        
        print(f"✅ Encontrados {len(product_items)} productos en Atomo")
        
        for idx, item in enumerate(product_items[:10]):  # Limitar a 10 resultados
            try:
                # Extraer nombre - múltiples selectores
                nombre_tag = None
                
                # Intentar con h3 > a
                h3 = item.find('h3', class_='product-title')
                if h3:
                    nombre_tag = h3.find('a') or h3
                
                # Otros selectores
                if not nombre_tag:
                    nombre_tag = (
                        item.find('h2', class_='product-title') or
                        item.find('a', class_='product-title') or
                        item.find('h3') or
                        item.find(attrs={'itemprop': 'name'})
                    )
                
                # Último recurso - cualquier a con texto largo
                if not nombre_tag:
                    links = item.find_all('a', href=True)
                    for link in links:
                        text = link.get_text(strip=True)
                        if len(text) > 10:  # Nombre debe tener >10 chars
                            nombre_tag = link
                            break
                
                if not nombre_tag:
                    if idx < 3:  # Debug solo primeros 3
                        print(f"  ⚠️ Producto {idx+1}: No se encontró nombre")
                        print(f"     HTML preview: {str(item)[:200]}")
                    continue
                
                nombre = nombre_tag.get_text(strip=True)
                
                if not nombre or len(nombre) < 3:
                    continue
                
                # Extraer precio - múltiples selectores
                precio_tag = None
                
                # Selectores comunes de PrestaShop
                precio_tag = (
                    item.find('span', class_='price') or
                    item.find('span', class_='product-price') or
                    item.find('div', class_='product-price-and-shipping') or
                    item.find(attrs={'itemprop': 'price'}) or
                    item.find('span', attrs={'content': True})  # Precio en atributo content
                )
                
                # Buscar en data-price
                if not precio_tag:
                    precio_attr = item.get('data-price')
                    if precio_attr:
                        try:
                            precio = float(precio_attr)
                            if precio > 0:
                                # Crear URL
                                link_tag = item.find('a', href=True)
                                url_producto = link_tag['href'] if link_tag else None
                                
                                if url_producto and not url_producto.startswith('http'):
                                    url_producto = f"https://atomoconviene.com{url_producto}"
                                
                                producto = Producto(
                                    nombre=nombre,
                                    precio=precio,
                                    supermercado=self.nombre_supermercado,
                                    url=url_producto
                                )
                                productos.append(producto)
                                print(f"  ✓ {nombre[:60]}: ${precio:,.2f}")
                                continue
                        except:
                            pass
                
                # Buscar cualquier texto con $
                if not precio_tag:
                    price_texts = item.find_all(string=re.compile(r'\$'))
                    if price_texts:
                        # Tomar el primero que tenga números
                        for pt in price_texts:
                            if re.search(r'\d', pt):
                                precio_tag = pt.find_parent()
                                break
                
                if not precio_tag:
                    if idx < 3:  # Debug solo primeros 3
                        print(f"  ⚠️ Producto {idx+1} ({nombre[:30]}...): No se encontró precio")
                        # Mostrar spans disponibles
                        spans = item.find_all('span')
                        print(f"     Spans disponibles: {len(spans)}")
                        for s in spans[:3]:
                            print(f"       - class={s.get('class')}: {s.get_text(strip=True)[:40]}")
                    continue
                
                precio_text = precio_tag.get_text(strip=True)
                
                # Si es un atributo content
                if not precio_text and precio_tag.get('content'):
                    precio_text = precio_tag.get('content')
                
                if not precio_text:
                    continue
                
                # Limpiar precio - formato argentino
                # Ejemplo: "$2.150,00" o "$2150" o "$ 2.150"
                precio_limpio = re.sub(r'[^\d,.]', '', precio_text)
                
                if not precio_limpio:
                    continue
                
                # Convertir formato argentino a float
                # Si tiene punto Y coma: 2.150,00 -> 2150.00
                if ',' in precio_limpio and '.' in precio_limpio:
                    precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
                # Si solo tiene coma: 2150,00 -> 2150.00
                elif ',' in precio_limpio:
                    precio_limpio = precio_limpio.replace(',', '.')
                # Si solo tiene punto: verificar si es separador de miles o decimal
                elif '.' in precio_limpio:
                    parts = precio_limpio.split('.')
                    # Si la última parte tiene 2 dígitos, es decimal
                    if len(parts[-1]) == 2:
                        # Es decimal: 99.50
                        pass
                    else:
                        # Es miles: 2.150 -> 2150
                        precio_limpio = precio_limpio.replace('.', '')
                
                try:
                    precio = float(precio_limpio)
                except ValueError:
                    if idx < 3:
                        print(f"  ⚠️ No se pudo convertir precio: '{precio_text}'")
                    continue
                
                # Extraer URL del producto
                link_tag = item.find('a', href=True)
                url_producto = link_tag['href'] if link_tag else None
                
                if url_producto and not url_producto.startswith('http'):
                    url_producto = f"https://atomoconviene.com{url_producto}"
                
                if precio > 0 and nombre:
                    producto = Producto(
                        nombre=nombre,
                        precio=precio,
                        supermercado=self.nombre_supermercado,
                        url=url_producto
                    )
                    productos.append(producto)
                    print(f"  ✓ {nombre[:60]}: ${precio:,.2f}")
                    
            except Exception as e:
                if idx < 3:
                    print(f"⚠️ Error parseando producto {idx+1} en Atomo: {e}")
                continue
        
        if not productos:
            print(f"❌ No se encontraron productos válidos en Atomo")
        else:
            print(f"✅ Procesados {len(productos)} productos de Atomo")
        
        return productos