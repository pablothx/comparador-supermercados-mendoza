# 📚 Documentación Técnica

## Arquitectura del Proyecto

### 🏗️ Stack Tecnológico

- **Frontend**: Streamlit
- **Backend**: Python 3.9+
- **IA/LLM**: AWS Bedrock (Claude Sonnet 4.5)
- **Web Scraping**: BeautifulSoup4, Requests
- **Geocoding**: Geopy (Nominatim)
- **Mapas**: Folium
- **Validación**: Pydantic

### 📂 Estructura de Carpetas

```
supermercado-comparador/
├── src/
│   ├── models/              # Modelos de datos (Pydantic)
│   │   └── models.py        # Producto, Supermercado, etc.
│   ├── scrapers/            # Web scrapers
│   │   ├── base_scraper.py  # Clase base abstracta
│   │   ├── atomo_scraper.py # Scraper de Atomo (real)
│   │   └── mock_scrapers.py # Scrapers simulados
│   ├── services/            # Servicios
│   │   ├── bedrock_service.py    # AWS Bedrock
│   │   └── geocoding_service.py  # Geocodificación
│   ├── utils/               # Utilidades
│   └── app.py              # Aplicación Streamlit
├── data/
│   └── supermercados_data.py # BD de supermercados
├── config/
│   └── config.py            # Configuración global
├── tests/
│   └── test_basic.py        # Tests básicos
└── requirements.txt         # Dependencias
```

## 🔄 Flujo de Trabajo

### 1. Usuario ingresa consulta

```
Input: "cumpleaños para 50 personas" + "Guaymallén, Mendoza"
```

### 2. Bedrock interpreta la consulta

```python
{
  "productos": ["gaseosas", "panchos", "hamburguesas", ...],
  "evento": "cumpleaños",
  "personas": 50
}
```

### 3. Geocodificación

```python
ubicacion = geocoding.obtener_coordenadas("Guaymallén, Mendoza")
# -> Ubicacion(lat=-32.8895, lon=-68.8458)
```

### 4. Filtrado de supermercados

```python
supermercados_cercanos = geocoding.filtrar_por_distancia(
    ubicacion, 
    todos_supermercados,
    max_distancia_km=10
)
```

### 5. Web Scraping

```python
for supermercado in supermercados_cercanos:
    scraper = scrapers[supermercado.nombre]
    productos = scraper.buscar_multiples_productos(productos_lista)
```

### 6. Comparación y ranking

```python
comparaciones.sort(key=lambda x: x.calcular_score())
# Score = (0.7 * precio) + (0.3 * distancia * 1000)
```

### 7. Recomendación con IA

```python
recomendacion = bedrock.generar_recomendacion(
    comparaciones,
    ubicacion
)
```

### 8. Visualización en Streamlit

- Tabla comparativa
- Métricas
- Mapa interactivo
- Detalles de productos

## 🧩 Componentes Clave

### BedrockService

Interactúa con AWS Bedrock para:
- Interpretar consultas en lenguaje natural
- Extraer productos y eventos
- Generar recomendaciones inteligentes
- Validar dominio de consultas

**Métodos principales:**
```python
def interpretar_consulta(mensaje: str) -> Dict
def generar_recomendacion(comparaciones: List, ubicacion: str) -> str
def _validar_dominio(mensaje: str) -> bool
```

### GeocodingService

Maneja geolocalización y distancias:
- Convierte direcciones en coordenadas
- Calcula distancias entre puntos
- Filtra por radio
- Estima tiempos de viaje

**Métodos principales:**
```python
def obtener_coordenadas(direccion: str) -> Ubicacion
def calcular_distancia(origen, destino) -> float
def filtrar_por_distancia(ubicacion, supermercados, max_km) -> List
```

### BaseScraper (Abstracto)

Clase base para todos los scrapers con:
- Manejo de sesiones HTTP
- Headers rotativos
- Rate limiting
- Error handling

**Métodos abstractos:**
```python
def buscar_producto(nombre: str) -> List[Producto]
def obtener_url_busqueda(query: str) -> str
```

### Scrapers Específicos

#### AtomoScraper (Real)
- Scraping de atomoconviene.com
- Mapeo de categorías
- Parsing de HTML real

#### Mock Scrapers (Simulados)
- Precios realistas generados algorítmicamente
- Variación por supermercado (factores de precio)
- Útiles para demo y testing

## 🔐 Seguridad y Buenas Prácticas

### Variables de Entorno
```bash
# .env
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
```

### Rate Limiting
- Delay de 2 segundos entre requests
- User-agent rotativo
- Session pooling

### Validación de Datos
- Modelos Pydantic para type safety
- Validación de dominio en consultas
- Sanitización de inputs

## 🧪 Testing

### Tests Básicos
```bash
python tests/test_basic.py
```

Incluye:
- Test de scrapers
- Test de geocoding
- Test de datos
- Test de flujo completo

### Tests Unitarios (TODO)
```bash
pytest tests/
```

## 🚀 Despliegue

### Opción 1: Streamlit Cloud
1. Push a GitHub
2. Conectar con Streamlit Cloud
3. Configurar secrets (AWS credentials)

### Opción 2: Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/app.py"]
```

### Opción 3: Servidor Local
```bash
streamlit run src/app.py --server.port 8501
```

## 📊 Performance

### Optimizaciones
- Caching de geocodificación
- Paralelización de scrapers (TODO)
- Cache de precios (TTL 1 hora)

### Tiempos Esperados
- Geocodificación: ~1s
- Scraping por supermercado: 2-5s
- Total (5 supermercados): 10-25s

## 🔮 Mejoras Futuras

1. **Scrapers Reales**
   - Implementar scrapers para todos los supermercados
   - Usar Selenium para sitios dinámicos

2. **Base de Datos**
   - PostgreSQL para histórico de precios
   - Redis para caching

3. **Paralelización**
   - Asyncio para scrapers concurrentes
   - Reduce tiempo total de búsqueda

4. **Notificaciones**
   - Alertas de precio
   - Ofertas especiales

5. **Móvil**
   - PWA con Streamlit
   - App nativa (Flutter/React Native)

6. **ML/Analytics**
   - Predicción de precios
   - Análisis de tendencias
   - Recomendaciones personalizadas

## 🐛 Troubleshooting

### Error: "No module named 'boto3'"
```bash
pip install -r requirements.txt
```

### Error: "Bedrock credentials not found"
```bash
# Verificar .env
cat .env
# Debe tener AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY
```

### Error: "Can't connect to atomoconviene.com"
- Verificar conexión a internet
- El sitio puede estar bloqueando scrapers
- Usar mock scrapers para testing

### Streamlit no se ejecuta
```bash
# Verificar instalación
streamlit --version

# Reinstalar si es necesario
pip install streamlit --upgrade
```

## 📞 Soporte

Para bugs o sugerencias:
- GitHub Issues: [repo]/issues
- Email: tu@email.com

## 📄 Licencia

MIT License - Ver LICENSE file
