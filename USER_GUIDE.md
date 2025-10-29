# 🎯 Guía de Uso - Comparador de Supermercados

## 🚀 Inicio Rápido

### Instalación

```bash
# 1. Clonar el repositorio
git clone [url-del-repo]
cd supermercado-comparador

# 2. Ejecutar script de instalación
chmod +x install.sh
./install.sh

# 3. Configurar AWS credentials
nano .env  # Agregar tus credenciales
```

### Configuración de AWS Bedrock

1. Ir a AWS Console
2. Navegar a AWS Bedrock
3. Habilitar modelo Claude Sonnet 4.5
4. Crear access keys en IAM
5. Copiar credentials a `.env`

### Ejecutar la App

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar Streamlit
streamlit run src/app.py
```

La app se abrirá en `http://localhost:8501`

## 📱 Cómo Usar la App

### 1. Configurar tu Ubicación

En el sidebar izquierdo:
- Ingresá tu dirección o punto de referencia
- Ejemplos:
  - "Guaymallén, Mendoza"
  - "cerca del shopping Palmares"
  - "Av. San Martín 2450"

### 2. Ajustar Radio de Búsqueda

Usá el slider para definir qué tan lejos estás dispuesto a ir:
- Mínimo: 1 km (solo lo más cercano)
- Máximo: 20 km (más opciones)
- Recomendado: 10 km (balance)

### 3. Seleccionar Supermercados

Marcá los supermercados que querés incluir en la comparación:
- ✅ Atomo
- ✅ Carrefour
- ✅ Coto
- ✅ Vea
- ✅ Tadicor
- ✅ Jumbo

💡 **Tip:** Todos están seleccionados por defecto

### 4. Ingresar tu Consulta

Hay varias formas de buscar:

#### Por Lista de Productos
```
arroz, aceite, yerba, azúcar, sal
```

#### Por Evento
```
cumpleaños para 50 personas
asado para 10
cena romántica para 2
semana de compras
```

#### Combinado
```
cumpleaños para 30: gaseosas, hamburguesas, panchos, papas fritas
```

### 5. Obtener Resultados

Click en **"🚀 Buscar Mejores Precios"**

La app mostrará:

#### 🎯 Recomendación Principal
```
🏆 Atomo Guaymallén es tu mejor opción
💰 Total: $45,230 - Ahorrás $3,450 vs Jumbo
📍 A 2.5 km (8 minutos)
```

#### 📊 Detalle de la Mejor Opción
- Total a pagar
- Distancia en km
- Tiempo estimado
- Lista de productos con precios

#### 🔄 Alternativas
Ver otras opciones ordenadas por score:
- Precio total
- Distancia
- Diferencia vs mejor opción
- Productos encontrados

#### 🗺️ Mapa Interactivo
- Tu ubicación (marcador rojo)
- Mejor opción (marcador verde)
- Otras opciones (marcadores azules)
- Click en marcadores para más info

## 💡 Ejemplos de Uso

### Ejemplo 1: Compra Semanal

**Consulta:**
```
arroz, aceite, yerba, leche, pan, huevos, pollo, papas, tomate, lechuga
```

**Ubicación:**
```
Guaymallén, Mendoza
```

**Resultado:**
- Bot busca cada producto en 6 supermercados
- Muestra el total por supermercado
- Recomienda el más económico cerca tuyo

### Ejemplo 2: Cumpleaños

**Consulta:**
```
cumpleaños para 50 personas
```

**Resultado:**
El bot automáticamente infiere:
- Gaseosas (Coca, Sprite, Fanta)
- Panchos y salchichas
- Hamburguesas
- Panes
- Papas fritas
- Salsas
- Servilletas

### Ejemplo 3: Asado

**Consulta:**
```
asado para 10 personas
```

**Resultado:**
El bot incluye:
- Carne (vacío, asado, etc.)
- Chorizo
- Morcilla
- Carbón
- Chimichurri
- Pan
- Ensalada
- Vino/Cerveza

## 🎨 Interfaz de Usuario

### Sidebar (Izquierda)
- **Ubicación:** Tu punto de partida
- **Radio:** Distancia máxima
- **Supermercados:** Cuáles incluir
- **Tips:** Sugerencias de uso

### Área Principal
- **Campo de búsqueda:** Ingresá productos/evento
- **Botones:** Buscar o Limpiar
- **Resultados:** Comparación y recomendación
- **Mapa:** Visualización geográfica

### Expansores
- **"📋 Lo que entendí":** Ver interpretación del bot
- **"📦 Ver productos":** Lista detallada
- **Alternativas:** Click para expandir detalles

## ⚡ Consejos Pro

### Para Mejores Resultados

1. **Sé específico con ubicación**
   ❌ "Mendoza"
   ✅ "Guaymallén centro, cerca del shopping"

2. **Usa nombres comunes de productos**
   ❌ "Arroz grano largo fino marca Gallo"
   ✅ "arroz"

3. **Para eventos, menciona cantidad de personas**
   ❌ "cumpleaños"
   ✅ "cumpleaños para 30 personas"

4. **Combina productos y evento**
   ✅ "asado para 6: carne, chorizo, ensalada, vino"

### Optimización de Búsqueda

- **Menos productos = más rápido**
  - Si buscás muchos items, la búsqueda puede tardar
  - Dividí en categorías (almacén, carnes, etc.)

- **Radio ajustado**
  - Menos km = menos opciones pero más rápido
  - Más km = más opciones pero más tiempo

- **Selectivo con supermercados**
  - Si solo te interesa Atomo y Carrefour, desmarcá el resto

## 🔧 Solución de Problemas

### "No se encontraron supermercados cercanos"
- Aumentá el radio de búsqueda
- Verificá que la ubicación esté bien escrita
- Probá con "Mendoza" si tu barrio es muy específico

### "No se encontraron precios"
- Algunos productos pueden no estar disponibles
- Intentá con sinónimos (ej: "gaseosa" → "bebida")
- Verificá ortografía

### "Error al procesar consulta"
- Verificá que AWS credentials estén configuradas
- Revisá conexión a internet
- Consultá logs en terminal

### La app va lenta
- Normal con muchos productos (10+)
- Reducí cantidad de supermercados seleccionados
- Reducí radio de búsqueda

## 📞 Ayuda

### Dominio del Bot

El bot **SOLO** responde sobre:
- ✅ Precios de productos
- ✅ Ubicaciones de supermercados
- ✅ Comparaciones de compras
- ✅ Recomendaciones de dónde comprar

El bot **NO** responde sobre:
- ❌ Recetas de cocina
- ❌ Noticias
- ❌ Temas generales
- ❌ Otros comercios que no sean supermercados

### Soporte

Si encontrás bugs o tenés sugerencias:
- GitHub Issues: [tu-repo]/issues
- Email: tu@email.com

## 🎓 Próximos Pasos

Una vez que domines lo básico:

1. **Explorá el código**
   - `src/app.py` - App principal
   - `src/scrapers/` - Cómo se obtienen precios
   - `src/services/bedrock_service.py` - IA

2. **Personalizá**
   - Agregá tus propios supermercados
   - Ajustá factores de score (precio vs distancia)
   - Cambiá estilos CSS

3. **Extendé funcionalidad**
   - Guardá listas de compra
   - Exportá a PDF
   - Notificaciones de ofertas

## 🎉 ¡Listo!

Ya estás preparado para usar el Comparador de Supermercados.

¡Ahorrá tiempo y dinero en tus compras! 🛒💰
