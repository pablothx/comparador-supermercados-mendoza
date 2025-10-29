# 🛒 Comparador Inteligente de Supermercados - POC

Bot inteligente que compara precios entre supermercados en Mendoza, Argentina y recomienda la mejor opción de compra.

## 🎯 Características

- **Búsqueda inteligente**: Ingresá productos o eventos (cumpleaños, asado, etc.)
- **Comparación de precios**: Entre 6 supermercados principales de Mendoza
- **Optimización por distancia**: Solo muestra opciones en un radio de 10km
- **Recomendación inteligente**: Balance entre precio y distancia usando AWS Bedrock

## 🏪 Supermercados Soportados

- Carrefour
- Coto
- Atomo
- Vea
- Tadicor
- Jumbo

## 📁 Estructura del Proyecto

```
supermercado-comparador/
├── src/
│   ├── scrapers/          # Web scrapers para cada supermercado
│   ├── services/          # Servicios (Bedrock, geocoding, etc.)
│   ├── models/            # Modelos de datos
│   ├── utils/             # Utilidades
│   └── app.py            # Aplicación Streamlit
├── data/                  # Datos de supermercados y productos
├── config/               # Configuraciones
├── tests/                # Tests unitarios
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone [url]
cd supermercado-comparador

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de AWS
```

## ⚙️ Configuración

Crear archivo `.env` con:

```env
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
```

## 🎮 Uso

```bash
# Ejecutar la aplicación
streamlit run src/app.py
```

Luego abrir en el navegador: `http://localhost:8501`

## 📝 Ejemplos de Uso

### Por lista de productos:

```
arroz, aceite, yerba, azúcar
```

### Por evento:

```
cumpleaños para 50 personas
```

### Con ubicación:

```
Guaymallén, cerca del shopping Palmares
```

## 🧪 Tests

```bash
pytest tests/
```

## 🏗️ Arquitectura

- **Frontend**: Streamlit
- **Backend**: Python 3.9+
- **IA**: AWS Bedrock (Claude Sonnet 4.5)
- **Scraping**: BeautifulSoup4, Requests
- **Geocoding**: Geopy

## 📊 Flujo de Trabajo

1. Usuario ingresa productos/evento y ubicación
2. Bot identifica ubicación y busca supermercados cercanos (10km)
3. Scrapers obtienen precios actualizados
4. Bedrock analiza y recomienda mejor opción
5. Se muestra comparativa con precio total y distancia

## ⚠️ Limitaciones

- Solo funciona para Mendoza, Argentina
- Precios actualizados mediante scraping (pueden variar)
- Requiere conexión a internet
- Sujeto a cambios en sitios web de supermercados
