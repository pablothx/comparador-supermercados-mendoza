"""
Aplicación Streamlit - Comparador Inteligente de Supermercados
CANTIDADES CALCULADAS 100% POR IA (Bedrock/Claude)
"""
import streamlit as st
import sys
from pathlib import Path
import math
import re

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.bedrock_service import BedrockService
from src.services.geocoding_service import GeocodingService
from src.scrapers.atomo_scraper import AtomoScraper
from src.scrapers.vea_scraper import VeaScraper
from src.scrapers.mock_scrapers import (
    CarrefourScraper, CotoScraper, 
    TadicorScraper, JumboScraper
)
from data.supermercados_data import obtener_supermercados_mendoza, obtener_supermercado_por_nombre
from src.models.models import ComparacionPrecios
from config.config import MAX_DISTANCE_KM

# Importar nueva lógica de comparación producto por producto
import sys
sys.path.insert(0, '/mnt/user-data/outputs')
from comparacion_producto_por_producto import (
    comparar_productos_entre_supermercados,
    mostrar_tabla_comparativa,
    generar_recomendacion_compra,
    mostrar_lista_compra_optimizada
)

import folium
from streamlit_folium import folium_static


# Configuración de la página
st.set_page_config(
    page_title="Comparador de Supermercados",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .supermercado-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: black;
        margin: 1rem 0;
    }
    .mejor-opcion {
        background: #46763a;
        border-left: 5px solid #28a745;
    }
    .precio-total {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
    }
    .ia-badge {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-left: 0.5rem;
    }
    .cantidad-ia {
        background: #2c3e50;
        padding: 0.8rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
    }
    /* Estilo para pills/botones de ejemplo */
    div[data-testid="column"] > div > div > button[kind="secondary"] {
        border-radius: 20px !important;
        border: 2px solid #e0e0e0 !important;
        background: white !important;
        color: #333 !important;
        font-size: 0.85rem !important;
        padding: 0.4rem 0.8rem !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="column"] > div > div > button[kind="secondary"]:hover {
        border-color: #667eea !important;
        background: #f0f0ff !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2) !important;
    }
    /* Mantener estilo normal para botón principal */
    button[kind="primary"] {
        border-radius: 5px !important;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


# Inicializar servicios en session_state
@st.cache_resource
def init_services():
    """Inicializa los servicios (se cachean para no recrearlos)"""
    return {
        'bedrock': BedrockService(),
        'geocoding': GeocodingService(),
        'scrapers': {
            'Atomo': AtomoScraper(),
            'Vea': VeaScraper(),
            # 'Carrefour': CarrefourScraper(),
            # 'Coto': CotoScraper(),
            # 'Tadicor': TadicorScraper(),
            # 'Jumbo': JumboScraper()
        }
    }


def ajustar_cantidades_ia(productos_encontrados, productos_ia):
    """
    Ajusta cantidades usando las estimaciones de la IA
    
    Args:
        productos_encontrados: Lista de productos únicos encontrados
        productos_ia: Lista de productos con cantidades de la IA
        
    Returns:
        (productos_ajustados, info_cantidades)
    """
    productos_ajustados = []
    info_cantidades = {}
    
    print(f"\n🤖 Usando cantidades calculadas por IA")
    
    for prod_encontrado in productos_encontrados:
        # Buscar el producto correspondiente en la respuesta de IA
        prod_ia = None
        for p_ia in productos_ia:
            if isinstance(p_ia, dict):
                nombre_ia = p_ia.get('nombre', '').lower()
                if nombre_ia in prod_encontrado.nombre.lower():
                    prod_ia = p_ia
                    break
        
        # Si no encontró match directo, buscar palabras clave
        if not prod_ia:
            for p_ia in productos_ia:
                if isinstance(p_ia, dict):
                    nombre_ia = p_ia.get('nombre', '').lower()
                    # Match parcial
                    if any(palabra in prod_encontrado.nombre.lower() for palabra in nombre_ia.split()):
                        prod_ia = p_ia
                        break
        
        if not prod_ia:
            # Si no hay match, agregar 1 unidad
            productos_ajustados.append(prod_encontrado)
            print(f"  ⚠️ No se encontró match de IA para {prod_encontrado.nombre}, usando 1 unidad")
            continue
        
        # Extraer info de la IA
        cantidad_ia = prod_ia.get('cantidad_estimada', 1)
        unidad_ia = prod_ia.get('unidad', 'unidades')
        razonamiento = prod_ia.get('razonamiento', '')
        
        # Extraer tamaño de presentación del producto real
        numeros = re.findall(r'\d+\.?\d*', prod_encontrado.nombre)
        tamano_presentacion = 1.0
        
        if numeros:
            tamano_presentacion = float(numeros[0])
            
            # Convertir ml/cc a litros
            if 'CC' in prod_encontrado.nombre.upper() or 'ML' in prod_encontrado.nombre.upper():
                tamano_presentacion = tamano_presentacion / 1000
            
            # Si es peso y está en gramos, convertir a kg
            if 'GR' in prod_encontrado.nombre.upper() and tamano_presentacion > 50:
                tamano_presentacion = tamano_presentacion / 1000
        
        # Calcular unidades a comprar
        if unidad_ia == 'litros' and tamano_presentacion < 10:
            # Es una bebida
            unidades = max(1, math.ceil(cantidad_ia / tamano_presentacion))
        elif unidad_ia == 'kg' and tamano_presentacion < 5:
            # Es carne o similar
            unidades = max(1, math.ceil(cantidad_ia / tamano_presentacion))
        else:
            # Son unidades directas
            unidades = max(1, int(cantidad_ia))
        
        # Limitar a máximo razonable
        unidades = min(unidades, 200)
        
        # Agregar N veces el producto
        for _ in range(unidades):
            productos_ajustados.append(prod_encontrado)
        
        # Guardar info
        info_cantidades[prod_ia.get('nombre')] = {
            'producto': prod_encontrado.nombre,
            'precio_unitario': prod_encontrado.precio,
            'unidades': unidades,
            'total': prod_encontrado.precio * unidades,
            'cantidad_ia': cantidad_ia,
            'unidad_ia': unidad_ia,
            'razonamiento': razonamiento
        }
        
        print(f"  ✓ {prod_ia.get('nombre')}: {unidades}x {prod_encontrado.nombre} = ${prod_encontrado.precio * unidades:,.2f}")
        print(f"    💡 IA: {cantidad_ia} {unidad_ia} - {razonamiento}")
    
    return productos_ajustados, info_cantidades


def main():
    """Función principal de la app"""
    
    # Header
    st.markdown('<div class="main-header">🛒 Comparador Inteligente de Supermercados<span class="ia-badge">🤖 IA</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Encontrá los mejores precios cerca tuyo en Mendoza<br><small>Cantidades calculadas inteligentemente por IA</small></div>', unsafe_allow_html=True)
    
    # ========== AWS CREDENTIALS ==========
    st.markdown("---")
    st.markdown("### 🔑 Configuración AWS (Requerido)")
    
    # Verificar si ya están en session_state
    if 'aws_configured' not in st.session_state:
        st.session_state.aws_configured = False
    
    if not st.session_state.aws_configured:
        with st.form("aws_credentials_form"):
            st.info("⚠️ **Necesitás tus credenciales de AWS** para usar la IA de Bedrock (Claude)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                aws_access_key = st.text_input(
                    "AWS Access Key ID",
                    type="password",
                    placeholder="AKIA...",
                    help="Tu AWS Access Key ID para Bedrock"
                )
            
            with col2:
                aws_secret_key = st.text_input(
                    "AWS Secret Access Key",
                    type="password",
                    placeholder="wJalrXUtn...",
                    help="Tu AWS Secret Access Key"
                )
            
            aws_region = st.text_input(
                "AWS Region",
                value="us-east-1",
                help="Región de AWS donde está habilitado Bedrock"
            )
            
            submitted = st.form_submit_button("✅ Configurar AWS", type="primary", use_container_width=True)
            
            if submitted:
                if not aws_access_key or not aws_secret_key:
                    st.error("❌ Debés ingresar ambas credenciales de AWS")
                    return
                
                # Guardar en session_state
                st.session_state.aws_access_key_id = aws_access_key
                st.session_state.aws_secret_access_key = aws_secret_key
                st.session_state.aws_region = aws_region
                st.session_state.aws_configured = True
                st.rerun()
        
        # Mostrar mensaje y detener ejecución
        st.warning("👆 Configurá tus credenciales de AWS para continuar")
        st.markdown("---")
        st.markdown("### 📚 ¿Dónde consigo mis credenciales?")
        st.markdown("""
        1. Ingresá a [AWS Console](https://console.aws.amazon.com)
        2. IAM → Users → Tu usuario → Security credentials
        3. Creá un Access Key si no tenés uno
        4. Asegurate de tener permisos para **AWS Bedrock**
        """)
        return
    
    # Mostrar credenciales configuradas
    st.success(f"✅ AWS configurado correctamente (Región: {st.session_state.aws_region})")
    
    if st.button("🔄 Cambiar credenciales"):
        st.session_state.aws_configured = False
        st.rerun()
    
    st.markdown("---")
    
    # ========== INICIALIZAR SERVICIOS CON CREDENCIALES ==========
    try:
        bedrock = BedrockService(
            aws_access_key_id=st.session_state.aws_access_key_id,
            aws_secret_access_key=st.session_state.aws_secret_access_key,
            aws_region=st.session_state.aws_region
        )
        geocoding = GeocodingService()
        scrapers = {
            'Atomo': AtomoScraper(),
            'Vea': VeaScraper(),
        }
    except Exception as e:
        st.error(f"❌ Error al conectar con AWS: {str(e)}")
        st.error("Verificá que tus credenciales sean correctas y tengas acceso a Bedrock")
        if st.button("🔄 Reintentar"):
            st.session_state.aws_configured = False
            st.rerun()
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        ubicacion_input = st.text_input(
            "📍 Tu ubicación",
            value="Guaymallén, Mendoza",
            help="Ingresá tu ubicación o punto de referencia"
        )
        
        radio_km = st.slider(
            "📏 Radio de búsqueda (km)",
            min_value=1,
            max_value=20,
            value=MAX_DISTANCE_KM,
            help=f"Buscamos supermercados en un radio de hasta {MAX_DISTANCE_KM}km"
        )
        
        st.markdown("---")
        
        st.markdown("### 🏪 Supermercados")
        supermercados_seleccionados = []
        for nombre in ['Atomo', 'Carrefour', 'Coto', 'Vea', 'Tadicor', 'Jumbo']:
            if st.checkbox(nombre, value=True):
                supermercados_seleccionados.append(nombre)
        
        st.markdown("---")
        st.info("💡 **Tip:** Probá con 'cumpleaños para 30 personas' o 'asado para 10'")
        st.markdown("---")
        st.markdown("🤖 **Powered by:**\n- AWS Bedrock (Claude)\n- Cantidades calculadas por IA")
    
    # Inicializar session state
    if 'input_consulta' not in st.session_state:
        st.session_state.input_consulta = ""
    
    # Pills con ejemplos predeterminados
    st.markdown("#### 💡 Ejemplos rápidos:")
    
    ejemplos = [
        "🎂 Cumpleaños para 30 niños",
        "🥩 Asado para 14 personas",
        "🧉 Comparar yerba",
        "🍕 Picada para 8 personas",
        "💑 Cena romántica para 2",
        "🏠 Lista semanal para 4",
        "☕ Desayuno completo",
        "🍝 Fideos, salsa y queso"
    ]
    
    cols = st.columns(4)
    for idx, ejemplo in enumerate(ejemplos):
        with cols[idx % 4]:
            # Limpiar emoji del texto
            texto_limpio = ejemplo.split(" ", 1)[1] if " " in ejemplo else ejemplo
            if st.button(ejemplo, key=f"pill_{idx}", use_container_width=True):
                st.session_state.input_consulta = texto_limpio
    
    st.markdown("---")
    
    # Usar form para capturar Enter nativamente
    with st.form(key="search_form", clear_on_submit=False):
        consulta = st.text_input(
            "🔍 ¿Qué querés comprar?",
            value=st.session_state.input_consulta,
            placeholder="Escribí tu consulta o usá los ejemplos de arriba ⤴️ • Presioná Enter para buscar",
            help="Podés ingresar productos específicos o un evento. Presioná Enter para buscar automáticamente.",
            key="input_text"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            buscar_btn = st.form_submit_button("🚀 Buscar Mejores Precios", type="primary", use_container_width=True)
        
        with col2:
            limpiar_btn = st.form_submit_button("🔄 Limpiar", use_container_width=True)
    
    # Actualizar session state con lo que escribió el usuario
    st.session_state.input_consulta = consulta
    
    # Limpiar si se presionó el botón limpiar
    if limpiar_btn:
        st.session_state.input_consulta = ""
        st.rerun()
    
    # Ejecutar búsqueda si hay texto y se presionó Enter o botón
    ejecutar = buscar_btn and consulta and consulta.strip()
    
    # Procesar búsqueda (por Enter o botón)
    if ejecutar:
        with st.spinner("🤖 IA analizando tu consulta y calculando cantidades..."):
            # 1. Interpretar consulta con Bedrock (ahora incluye cantidades)
            interpretacion = bedrock.interpretar_consulta(consulta)
            
            if "error" in interpretacion:
                st.error(f"❌ {interpretacion['error']}")
                return
            
            st.success("✅ Consulta interpretada correctamente por IA")
            
            # Extraer información
            productos_ia = interpretacion.get("productos", [])
            personas = interpretacion.get("personas", 1)
            evento = interpretacion.get("evento")
            
            # Extraer solo nombres para buscar
            if productos_ia and isinstance(productos_ia[0], dict):
                productos_nombres = [p.get('nombre') for p in productos_ia]
            else:
                productos_nombres = productos_ia
            
            if not productos_nombres:
                st.warning("No se pudieron identificar productos. Intentá ser más específico.")
                return
            
            # Mostrar interpretación
            with st.expander("📋 Lo que entendió la IA"):
                st.json(interpretacion)
            
            # Mostrar cantidades calculadas por IA
            if personas and personas > 1:
                st.markdown("### 🤖 Cantidades Calculadas por IA")
                for prod in productos_ia:
                    if isinstance(prod, dict):
                        st.markdown(f"""
                        <div class="cantidad-ia">
                            <strong>{prod.get('nombre').title()}</strong>: {prod.get('cantidad_estimada')} {prod.get('unidad')}<br>
                            <small>💡 {prod.get('razonamiento', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
        
        with st.spinner("📍 Ubicando supermercados cercanos..."):
            # 2. Geocodificar ubicación
            ubicacion = geocoding.obtener_coordenadas(ubicacion_input)
            
            if not ubicacion:
                st.error("❌ No se pudo encontrar la ubicación. Intentá con otra dirección.")
                return
            
            st.success(f"✅ Ubicación: {ubicacion.direccion}")
            
            # 3. Filtrar supermercados por distancia
            todos_supermercados = obtener_supermercados_mendoza()
            supermercados_cercanos = geocoding.filtrar_por_distancia(
                ubicacion,
                todos_supermercados,
                max_distancia_km=radio_km
            )
            
            # Filtrar por selección del usuario
            supermercados_cercanos = [
                s for s in supermercados_cercanos 
                if any(nombre in s.nombre for nombre in supermercados_seleccionados)
            ]
            
            if not supermercados_cercanos:
                st.warning(f"⚠️ No se encontraron supermercados en un radio de {radio_km}km")
                return
            
            st.info(f"🏪 Encontrados {len(supermercados_cercanos)} supermercados cercanos")
        
        with st.spinner("💰 Comparando precios producto por producto..."):
            # 4. NUEVA LÓGICA: Comparar cada producto entre todos los supermercados
            comparacion = comparar_productos_entre_supermercados(
                productos_ia,
                supermercados_cercanos,
                scrapers,
                supermercados_seleccionados,
                geocoding
            )
            
            # 5. Mostrar tabla comparativa
            mostrar_tabla_comparativa(comparacion)
            
            # 6. Generar y mostrar lista de compra optimizada
            lista_compra_opt, total_opt, super_unico, total_unico = generar_recomendacion_compra(comparacion)
            
            if not lista_compra_opt:
                st.error("❌ No se encontraron productos en ningún supermercado")
                return
            
            mostrar_lista_compra_optimizada(lista_compra_opt, total_opt, super_unico, total_unico)
        
        # Mapa
        st.markdown("---")
        st.header("🗺️ Mapa de Supermercados")
        
        # Crear mapa centrado en ubicación del usuario
        mapa = folium.Map(
            location=[ubicacion.latitud, ubicacion.longitud],
            zoom_start=13
        )
        
        # Marcar ubicación del usuario
        folium.Marker(
            [ubicacion.latitud, ubicacion.longitud],
            popup="Tu ubicación",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(mapa)
        
        # Determinar qué lista usar para el mapa
        estrategia = st.session_state.get('estrategia_seleccionada', '🚗 Todo en un solo supermercado (más cómodo)')
        
        if "un solo" in estrategia.lower():
            lista_mapa = super_unico
        else:
            lista_mapa = lista_compra_opt
        
        # Marcar supermercados de la lista de compra
        for super_nombre, datos in lista_mapa.items():
            super_obj = next((s for s in supermercados_cercanos if s.nombre == super_nombre), None)
            
            if super_obj:
                # Verde si tiene más productos, azul si tiene menos
                num_productos = len(datos['productos'])
                max_productos = max(len(d['productos']) for d in lista_mapa.values())
                color = 'green' if num_productos == max_productos else 'blue'
                
                folium.Marker(
                    [super_obj.latitud, super_obj.longitud],
                    popup=f"{super_nombre}<br>{num_productos} productos<br>${datos['total']:,.2f}<br>{datos['distancia_km']} km",
                    icon=folium.Icon(color=color, icon='shopping-cart')
                ).add_to(mapa)
        
        folium_static(mapa, width=1200, height=600)


if __name__ == "__main__":
    main()