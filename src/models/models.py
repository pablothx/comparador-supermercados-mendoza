"""
Modelos de datos del proyecto usando Pydantic
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class Producto(BaseModel):
    """Modelo de un producto"""
    nombre: str
    precio: float
    supermercado: str
    url: Optional[str] = None
    marca: Optional[str] = None
    cantidad: Optional[str] = None
    unidad: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Arroz Largo Fino",
                "precio": 850.50,
                "supermercado": "Atomo",
                "marca": "Gallo",
                "cantidad": "1",
                "unidad": "kg"
            }
        }


class Supermercado(BaseModel):
    """Modelo de un supermercado"""
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    distancia_km: Optional[float] = None
    telefono: Optional[str] = None
    horarios: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Atomo Conviene",
                "direccion": "Av. San Martín 1234, Guaymallén",
                "latitud": -32.8895,
                "longitud": -68.8458,
                "distancia_km": 2.5
            }
        }


class ListaCompra(BaseModel):
    """Lista de productos a comprar"""
    productos: List[str]
    evento: Optional[str] = None
    personas: Optional[int] = None
    presupuesto_max: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "productos": ["arroz", "aceite", "yerba"],
                "evento": "cena familiar",
                "personas": 4
            }
        }


class Ubicacion(BaseModel):
    """Ubicación del usuario"""
    direccion: str
    latitud: float
    longitud: float
    ciudad: str = "Mendoza"
    provincia: str = "Mendoza"
    
    class Config:
        json_schema_extra = {
            "example": {
                "direccion": "Guaymallén, Mendoza",
                "latitud": -32.8895,
                "longitud": -68.8458
            }
        }


class ComparacionPrecios(BaseModel):
    """Resultado de comparación de precios"""
    supermercado: str
    productos: List[Producto]
    total: float
    distancia_km: float
    tiempo_estimado_min: int
    
    def calcular_score(self, peso_precio: float = 0.7, peso_distancia: float = 0.3) -> float:
        """
        Calcula un score ponderado entre precio y distancia
        Menor score = mejor opción
        """
        # Normalizar precio (menor es mejor)
        score_precio = self.total
        
        # Normalizar distancia (menor es mejor)
        score_distancia = self.distancia_km
        
        # Score final ponderado
        return (peso_precio * score_precio) + (peso_distancia * score_distancia * 1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "supermercado": "Atomo",
                "productos": [],
                "total": 5430.50,
                "distancia_km": 2.5,
                "tiempo_estimado_min": 8
            }
        }


class Recomendacion(BaseModel):
    """Recomendación final del bot"""
    mejor_opcion: ComparacionPrecios
    alternativas: List[ComparacionPrecios]
    ahorro_vs_mas_caro: float
    razon: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "mejor_opcion": {},
                "alternativas": [],
                "ahorro_vs_mas_caro": 1250.00,
                "razon": "Mejor balance entre precio y distancia"
            }
        }
