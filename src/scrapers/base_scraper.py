"""
Scraper base para todos los supermercados
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import time
import random
import sys
from pathlib import Path
import unicodedata  # para normalizar acentos, etc.

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import USER_AGENTS, REQUEST_TIMEOUT, SCRAPING_DELAY
from src.models.models import Producto

__all__ = ["BaseScraper", "_matches", "_norm"]  # útil si lo importás desde app.py


# =========================
# Helpers de matching
# =========================
ALIAS = {
    "pasta": ["pasta", "fideos", "spaghetti", "tallarines", "moños", "mostacholes"],
    "salsa": ["salsa", "tuco", "salsa de tomate", "filetto", "pomarola", "boloñesa", "bolognesa"],
    "queso": ["queso", "parmesano", "sardo", "reggianito", "rallado"],
    "pan": ["pan", "baguette", "pan frances", "pan francés", "figazza", "panes"],
    "vino": ["vino", "malbec", "cabernet", "merlot", "tinto", "blanco"],
    "gaseosas": ["gaseosa", "gaseosas", "coca", "sprite", "fanta", "pepsi", "cola"],
    "cerveza": ["cerveza", "lata cerveza", "botella cerveza"],
    "postre": ["postre", "helado", "flan", "budin", "budín", "chocolate", "alfajor", "helados"],
    "aceite": ["aceite", "girasol", "oliva", "extra virgen"],
    "ensalada": ["ensalada", "lechuga", "tomate", "rucula", "rúcula", "mix verde"],
    "carne": ["carne", "asado", "vacío", "vacio", "bife", "milanesa", "milanesas"],
    "pollo": ["pollo", "suprema", "pechuga"],
    "velas": ["vela", "velas"],
    "desayuno": ["desayuno", "medialunas", "facturas", "mermelada", "dulce", "cafe", "café", "té", "mate cocido", "jugo"],
}


def _norm(s: str) -> str:
    s = (s or "").lower()
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return s


def _expand_terms(term: str):
    t = _norm(term.strip())
    cands = [t, t[:-1]] if t.endswith("s") else [t, t + "s"]
    cands += [_norm(x) for x in ALIAS.get(t, [])]
    return list(dict.fromkeys(cands))


def _matches(name: str, term: str) -> bool:
    n = _norm(name)
    for cand in _expand_terms(term):
        if cand and cand in n:
            return True
    return False


# =========================
# Clase BaseScraper
# =========================
class BaseScraper(ABC):
    """Clase base abstracta para todos los scrapers"""

    def __init__(self, nombre_supermercado: str):
        self.nombre_supermercado = nombre_supermercado
        self.session = requests.Session()
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-AR,es;q=0.9",
        }

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Obtiene y parsea una página web"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            time.sleep(SCRAPING_DELAY)
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo {url}: {e}")
            return None

    @abstractmethod
    def buscar_producto(self, nombre_producto: str) -> List[Producto]:
        """Busca un producto específico"""
        pass

    @abstractmethod
    def obtener_url_busqueda(self, query: str) -> str:
        """Construye la URL de búsqueda"""
        pass

    def buscar_multiples_productos(self, productos: List[str]) -> List[Producto]:
        """
        Devuelve a lo sumo UN producto por término (el más barato) usando matching con sinónimos.
        Evita inflar el total sumando muchos SKUs por término.
        """
        resultados: List[Producto] = []
        for termino in productos or []:
            if not termino:
                continue

            candidatos = self.buscar_producto(termino)
            if not candidatos:
                continue

            filtrados = [p for p in candidatos if _matches(p.nombre or "", termino)]
            pool = filtrados if filtrados else candidatos

            elegido = min(pool, key=lambda p: p.precio)
            resultados.append(elegido)
            print(f"  ✓ Elegido para '{termino}': {elegido.nombre} - ${elegido.precio:,.2f}")

        return resultados
