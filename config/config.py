"""
Configuración principal del proyecto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas del proyecto
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

# AWS Bedrock
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
#BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"  # Ajustar según disponibilidad
BEDROCK_MODEL_ID = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Parámetros de búsqueda
MAX_DISTANCE_KM = 10  # Radio máximo de búsqueda
DEFAULT_LOCATION = "Guaymallén, Mendoza, Argentina"

# Supermercados soportados
SUPERMERCADOS = [
    "Carrefour",
    "Coto", 
    "Atomo",
    "Vea",
    "Tadicor",
    "Jumbo"
]

# User agents para scraping (rotar para evitar bloqueos)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Timeouts
REQUEST_TIMEOUT = 10  # segundos
SCRAPING_DELAY = 2  # segundos entre requests

# Cache
CACHE_TTL = 3600  # 1 hora (tiempo de vida del cache de precios)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
