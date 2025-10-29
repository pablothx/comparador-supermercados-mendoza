"""
Servicio de geocodificación y cálculo de distancias
"""
from typing import Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.models import Ubicacion, Supermercado


class GeocodingService:
    """Servicio para geocodificación y cálculo de distancias"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="supermercado_comparador")
        self._cache = {}
    
    def obtener_coordenadas(self, direccion: str) -> Optional[Ubicacion]:
        """
        Obtiene las coordenadas de una dirección
        
        Args:
            direccion: Dirección a geocodificar
            
        Returns:
            Ubicacion con coordenadas o None si falla
        """
        # Verificar cache
        if direccion in self._cache:
            return self._cache[direccion]
        
        try:
            # Normalizar direcciones de Mendoza
            direccion_normalizada = direccion
            
            # Si es una ubicación conocida de Mendoza, usar coordenadas fijas
            ubicaciones_mendoza = {
                "guaymallen": (-32.8895, -68.8458),
                "guaymallén": (-32.8895, -68.8458),
                "godoy cruz": (-32.9270, -68.8420),
                "las heras": (-32.8513, -68.8273),
                "mendoza": (-32.8908, -68.8272),
                "mendoza capital": (-32.8908, -68.8272),
                "lujan de cuyo": (-33.0329, -68.8769),
                "maipu": (-32.9833, -68.7833),
                "maipú": (-32.9833, -68.7833),
            }
            
            direccion_lower = direccion.lower().strip()
            
            # Buscar coincidencia en ubicaciones conocidas
            for lugar, coords in ubicaciones_mendoza.items():
                if lugar in direccion_lower:
                    ubicacion = Ubicacion(
                        direccion=f"{lugar.title()}, Mendoza, Argentina",
                        latitud=coords[0],
                        longitud=coords[1],
                        ciudad="Mendoza",
                        provincia="Mendoza"
                    )
                    self._cache[direccion] = ubicacion
                    return ubicacion
            
            # Si no es ubicación conocida, intentar con geopy
            # Agregar "Mendoza, Argentina" si no está presente
            if "mendoza" not in direccion_lower and "argentina" not in direccion_lower:
                direccion_completa = f"{direccion}, Mendoza, Argentina"
            else:
                direccion_completa = direccion
            
            location = self.geolocator.geocode(direccion_completa, timeout=10)
            
            if location:
                ubicacion = Ubicacion(
                    direccion=location.address,
                    latitud=location.latitude,
                    longitud=location.longitude,
                    ciudad="Mendoza",
                    provincia="Mendoza"
                )
                
                # Guardar en cache
                self._cache[direccion] = ubicacion
                return ubicacion
            
            # Si todo falla, usar Guaymallén por defecto
            ubicacion = Ubicacion(
                direccion="Guaymallén, Mendoza, Argentina",
                latitud=-32.8895,
                longitud=-68.8458,
                ciudad="Mendoza",
                provincia="Mendoza"
            )
            self._cache[direccion] = ubicacion
            return ubicacion
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error en geocodificación: {e}")
            # Retornar Guaymallén por defecto en caso de error
            ubicacion = Ubicacion(
                direccion="Guaymallén, Mendoza, Argentina (ubicación por defecto)",
                latitud=-32.8895,
                longitud=-68.8458,
                ciudad="Mendoza",
                provincia="Mendoza"
            )
            return ubicacion
    
    def calcular_distancia(
        self, 
        origen: Tuple[float, float], 
        destino: Tuple[float, float]
    ) -> float:
        """
        Calcula la distancia entre dos puntos en km
        
        Args:
            origen: Tupla (latitud, longitud)
            destino: Tupla (latitud, longitud)
            
        Returns:
            Distancia en kilómetros
        """
        return geodesic(origen, destino).kilometers
    
    def filtrar_por_distancia(
        self,
        ubicacion_usuario: Ubicacion,
        supermercados: list[Supermercado],
        max_distancia_km: float = 10.0
    ) -> list[Supermercado]:
        """
        Filtra supermercados por distancia máxima
        
        Args:
            ubicacion_usuario: Ubicación del usuario
            supermercados: Lista de supermercados
            max_distancia_km: Distancia máxima en km
            
        Returns:
            Lista de supermercados dentro del radio
        """
        origen = (ubicacion_usuario.latitud, ubicacion_usuario.longitud)
        supermercados_cercanos = []
        
        for super in supermercados:
            destino = (super.latitud, super.longitud)
            distancia = self.calcular_distancia(origen, destino)
            
            if distancia <= max_distancia_km:
                super.distancia_km = round(distancia, 2)
                supermercados_cercanos.append(super)
        
        # Ordenar por distancia
        supermercados_cercanos.sort(key=lambda x: x.distancia_km)
        
        return supermercados_cercanos
    
    def estimar_tiempo_viaje(self, distancia_km: float) -> int:
        """
        Estima el tiempo de viaje en minutos
        Asume velocidad promedio de 30 km/h en ciudad
        
        Args:
            distancia_km: Distancia en kilómetros
            
        Returns:
            Tiempo estimado en minutos
        """
        velocidad_promedio_kmh = 30
        tiempo_horas = distancia_km / velocidad_promedio_kmh
        return int(tiempo_horas * 60)