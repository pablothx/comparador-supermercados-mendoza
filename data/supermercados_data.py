"""
Base de datos de supermercados en Mendoza
"""
from typing import List
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.models import Supermercado


def obtener_supermercados_mendoza() -> List[Supermercado]:
    """
    Retorna lista de supermercados en Mendoza con ubicaciones reales
    """
    return [
        # ATOMO
        Supermercado(
            nombre="Atomo Guaymallén",
            direccion="Av. San Martín 2450, Guaymallén, Mendoza",
            latitud=-32.8895,
            longitud=-68.8458,
            telefono="0261 429-5000"
        ),
        Supermercado(
            nombre="Atomo Las Heras",
            direccion="Álvarez Condarco 740, Las Heras, Mendoza",
            latitud=-32.8513,
            longitud=-68.8273,
            telefono="0261 429-5000"
        ),
        Supermercado(
            nombre="Atomo Godoy Cruz",
            direccion="Av. San Martín 1850, Godoy Cruz, Mendoza",
            latitud=-32.9145,
            longitud=-68.8497,
            telefono="0261 429-5000"
        ),
        
        # CARREFOUR
        Supermercado(
            nombre="Carrefour Express Guaymallén",
            direccion="Av. Mitre 1200, Guaymallén, Mendoza",
            latitud=-32.8923,
            longitud=-68.8512,
            telefono="0810-444-8000"
        ),
        Supermercado(
            nombre="Carrefour Mendoza Centro",
            direccion="San Martín 1150, Mendoza Capital",
            latitud=-32.8908,
            longitud=-68.8428,
            telefono="0810-444-8000"
        ),
        
        # COTO
        Supermercado(
            nombre="Coto Mendoza",
            direccion="Av. Acceso Este 3450, Guaymallén, Mendoza",
            latitud=-32.8756,
            longitud=-68.8234,
            telefono="0810-222-2686"
        ),
        
        # VEA
        Supermercado(
            nombre="Vea Guaymallén",
            direccion="Urquiza 2150, Guaymallén, Mendoza",
            latitud=-32.8867,
            longitud=-68.8523,
            telefono="0810-122-0832"
        ),
        Supermercado(
            nombre="Vea Godoy Cruz",
            direccion="San Martín 2300, Godoy Cruz, Mendoza",
            latitud=-32.9234,
            longitud=-68.8556,
            telefono="0810-122-0832"
        ),
        
        # TADICOR
        Supermercado(
            nombre="Tadicor Mayorista",
            direccion="Ruta 7 Km 1056, Guaymallén, Mendoza",
            latitud=-32.8678,
            longitud=-68.8123,
            telefono="0261-431-2000"
        ),
        
        # JUMBO
        Supermercado(
            nombre="Jumbo Mendoza",
            direccion="Av. Acceso Este 3050, Guaymallén, Mendoza",
            latitud=-32.8798,
            longitud=-68.8312,
            telefono="0810-999-5862"
        ),
    ]


def obtener_supermercado_por_nombre(nombre: str) -> List[Supermercado]:
    """
    Filtra supermercados por nombre/cadena
    
    Args:
        nombre: Nombre de la cadena (ej: "Atomo", "Carrefour")
        
    Returns:
        Lista de supermercados de esa cadena
    """
    todos = obtener_supermercados_mendoza()
    nombre_lower = nombre.lower()
    
    return [s for s in todos if nombre_lower in s.nombre.lower()]
