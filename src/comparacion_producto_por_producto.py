"""
Lógica mejorada: Comparación PRODUCTO POR PRODUCTO entre supermercados
Muestra tabla comparativa y recomienda dónde comprar cada cosa
"""
import streamlit as st
from typing import Dict, List, Tuple
import math

def comparar_productos_entre_supermercados(
    productos_ia: List[dict],
    supermercados_cercanos: List,
    scrapers: Dict,
    supermercados_seleccionados: List[str],
    geocoding
) -> Tuple[Dict, float, str]:
    """
    Compara cada producto entre todos los supermercados
    
    Returns:
        (comparacion_por_producto, total_optimizado, recomendacion_compra)
    """
    
    comparacion = {}
    productos_nombres = [p.get('nombre') for p in productos_ia if isinstance(p, dict)]
    
    st.markdown("### 🔍 Buscando en cada supermercado...")
    
    # Contenedor para mensajes de progreso
    progress_container = st.empty()
    
    # 1. Buscar cada producto en cada supermercado
    for idx, prod_ia in enumerate(productos_ia):
        if not isinstance(prod_ia, dict):
            continue
            
        nombre_prod = prod_ia.get('nombre')
        cantidad_necesaria = prod_ia.get('cantidad_estimada', 1)
        unidad = prod_ia.get('unidad', 'unidades')
        
        # Mostrar progreso
        progress_container.markdown(f"🔎 Buscando **{nombre_prod}**...")
        
        comparacion[nombre_prod] = {
            'cantidad_necesaria': cantidad_necesaria,
            'unidad': unidad,
            'supermercados': {}
        }
        
        # Buscar en cada supermercado
        for supermercado in supermercados_cercanos:
            cadena = next((n for n in supermercados_seleccionados if n in supermercado.nombre), None)
            
            if not cadena or cadena not in scrapers:
                continue
            
            scraper = scrapers[cadena]
            
            # Buscar el producto
            productos_encontrados = scraper.buscar_producto(nombre_prod)
            
            if productos_encontrados:
                # Tomar el más barato
                mejor_producto = min(productos_encontrados, key=lambda p: p.precio)
                
                # Calcular unidades necesarias
                import re
                numeros = re.findall(r'\d+\.?\d*', mejor_producto.nombre)
                tamano_presentacion = 1.0
                
                if numeros:
                    tamano_presentacion = float(numeros[0])
                    
                    if 'CC' in mejor_producto.nombre.upper() or 'ML' in mejor_producto.nombre.upper():
                        tamano_presentacion = tamano_presentacion / 1000
                    
                    if 'GR' in mejor_producto.nombre.upper() and tamano_presentacion > 50:
                        tamano_presentacion = tamano_presentacion / 1000
                
                # Calcular unidades a comprar
                if unidad == 'litros' and tamano_presentacion < 10:
                    unidades = max(1, math.ceil(cantidad_necesaria / tamano_presentacion))
                elif unidad == 'kg' and tamano_presentacion < 5:
                    unidades = max(1, math.ceil(cantidad_necesaria / tamano_presentacion))
                else:
                    unidades = max(1, int(cantidad_necesaria))
                
                unidades = min(unidades, 200)
                
                # Guardar en comparación
                comparacion[nombre_prod]['supermercados'][supermercado.nombre] = {
                    'producto': mejor_producto,
                    'unidades': unidades,
                    'precio_unitario': mejor_producto.precio,
                    'subtotal': mejor_producto.precio * unidades,
                    'distancia_km': supermercado.distancia_km,
                    'tiempo_min': geocoding.estimar_tiempo_viaje(supermercado.distancia_km),
                    'url': mejor_producto.url  # Agregar URL del producto
                }
            else:
                # No encontrado
                comparacion[nombre_prod]['supermercados'][supermercado.nombre] = None
        
        # Actualizar con check
        progress_container.markdown(f"✅ **{nombre_prod}** encontrado")
    
    # Limpiar contenedor
    progress_container.empty()
    st.success("✅ Búsqueda completada")
    
    return comparacion


def mostrar_tabla_comparativa(comparacion: Dict):
    """
    Muestra tabla comparativa producto por producto
    """
    st.markdown("---")
    st.markdown("## 📊 Comparación Producto por Producto")
    
    for nombre_prod, info in comparacion.items():
        st.markdown(f"### 🛒 {nombre_prod.title()}")
        st.markdown(f"*Necesitás: {info['cantidad_necesaria']} {info['unidad']}*")
        
        supermercados_info = info['supermercados']
        
        if not supermercados_info or all(v is None for v in supermercados_info.values()):
            st.error(f"❌ No se encontró **{nombre_prod}** en ningún supermercado")
            continue
        
        # Crear columnas para comparar
        supers_con_producto = {k: v for k, v in supermercados_info.items() if v is not None}
        
        if not supers_con_producto:
            st.error(f"❌ No se encontró **{nombre_prod}** en ningún supermercado")
            continue
        
        # Encontrar el más barato
        mejor_super = min(supers_con_producto.keys(), 
                         key=lambda s: supers_con_producto[s]['subtotal'])
        
        # Agrupar por CADENA (no por sucursal específica)
        supers_agrupados = {}
        for super_nombre, datos in supers_con_producto.items():
            # Extraer solo la cadena (Atomo, Vea, etc)
            cadena = super_nombre.split()[0]
            
            # Si ya existe esta cadena, mantener el más barato
            if cadena not in supers_agrupados:
                supers_agrupados[cadena] = {
                    'nombre_completo': super_nombre,
                    'datos': datos,
                    'es_mejor': (super_nombre == mejor_super)
                }
            else:
                # Comparar y quedarse con el más barato de esta cadena
                if datos['subtotal'] < supers_agrupados[cadena]['datos']['subtotal']:
                    supers_agrupados[cadena] = {
                        'nombre_completo': super_nombre,
                        'datos': datos,
                        'es_mejor': (super_nombre == mejor_super)
                    }
        
        # Limitar a máximo 2 supermercados diferentes para comparar
        supers_a_mostrar = list(supers_agrupados.values())[:2]
        
        # Mostrar tabla
        cols = st.columns(len(supers_a_mostrar))
        
        for idx, info_super in enumerate(supers_a_mostrar):
            super_nombre = info_super['nombre_completo']
            datos = info_super['datos']
            es_mejor = info_super['es_mejor']
            
            with cols[idx]:
                es_mejor = (super_nombre == mejor_super)
                
                # Card para cada supermercado
                border_color = "#4ade80" if es_mejor else "#666"
                bg_color = "#1a3a1a" if es_mejor else "#2a2a2a"
                
                # Nombre del producto truncado
                nombre_truncado = datos['producto'].nombre[:50]
                if len(datos['producto'].nombre) > 50:
                    nombre_truncado += "..."
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 1rem;
                    border-radius: 10px;
                    border: 3px solid {border_color};
                    text-align: center;
                    min-height: 250px;
                ">
                    <div style="font-size: 1.2rem; font-weight: bold; color: #fff; margin-bottom: 0.5rem;">
                        {super_nombre.split()[0]}
                    </div>
                    {f'<div style="color: #4ade80; font-weight: bold; margin-bottom: 0.5rem;">✅ MÁS BARATO</div>' if es_mejor else '<div style="height: 28px;"></div>'}
                    <div style="font-size: 0.85rem; color: #aaa; margin-bottom: 0.5rem; min-height: 40px;">
                        {datos['unidades']}x {nombre_truncado}
                    </div>
                    <div style="font-size: 0.9rem; color: #999; margin-bottom: 0.5rem;">
                        ${datos['precio_unitario']:,.2f} c/u
                    </div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: {'#4ade80' if es_mejor else '#fff'}; margin-bottom: 0.5rem;">
                        ${datos['subtotal']:,.2f}
                    </div>
                    <div style="font-size: 0.75rem; color: #666; margin-bottom: 0.5rem;">
                        📍 {datos['distancia_km']} km • {datos['tiempo_min']} min
                    </div>
                    <a href="{datos.get('url', '#')}" target="_blank" style="
                        display: inline-block;
                        background: #667eea;
                        color: white;
                        padding: 0.5rem 1rem;
                        border-radius: 5px;
                        text-decoration: none;
                        font-size: 0.85rem;
                        margin-top: 0.5rem;
                    ">🔗 Ver producto</a>
                </div>
                """, unsafe_allow_html=True)
        
        # Mostrar supermercados sin el producto
        sin_producto = [k for k, v in supermercados_info.items() if v is None]
        if sin_producto:
            st.caption(f"⚠️ No disponible en: {', '.join(sin_producto)}")
        
        st.markdown("---")


def generar_recomendacion_compra(comparacion: Dict) -> Tuple[Dict, float, Dict, float]:
    """
    Genera recomendación de dónde comprar cada cosa
    
    Returns:
        (lista_compra_optimizada, total_optimizado, mejor_supermercado_unico, total_unico)
    """
    # 1. Lista optimizada (cada producto donde está más barato)
    lista_compra_optimizada = {}
    total_optimizado = 0
    
    for nombre_prod, info in comparacion.items():
        supermercados_info = info['supermercados']
        supers_con_producto = {k: v for k, v in supermercados_info.items() if v is not None}
        
        if not supers_con_producto:
            continue
        
        # Encontrar el más barato
        mejor_super = min(supers_con_producto.keys(), 
                         key=lambda s: supers_con_producto[s]['subtotal'])
        
        datos_mejor = supers_con_producto[mejor_super]
        
        # Agregar a lista de compra
        if mejor_super not in lista_compra_optimizada:
            lista_compra_optimizada[mejor_super] = {
                'productos': [],
                'total': 0,
                'distancia_km': datos_mejor['distancia_km'],
                'tiempo_min': datos_mejor['tiempo_min']
            }
        
        lista_compra_optimizada[mejor_super]['productos'].append({
            'nombre': nombre_prod,
            'producto_real': datos_mejor['producto'].nombre,
            'unidades': datos_mejor['unidades'],
            'precio_unitario': datos_mejor['precio_unitario'],
            'subtotal': datos_mejor['subtotal'],
            'url': datos_mejor.get('url', '#')
        })
        
        lista_compra_optimizada[mejor_super]['total'] += datos_mejor['subtotal']
        total_optimizado += datos_mejor['subtotal']
    
    # 2. Mejor supermercado único (comprar todo en uno)
    supermercados_totales = {}
    
    for nombre_prod, info in comparacion.items():
        supermercados_info = info['supermercados']
        
        for super_nombre, datos in supermercados_info.items():
            if datos is None:
                # Si no tiene el producto, penalizamos
                if super_nombre not in supermercados_totales:
                    supermercados_totales[super_nombre] = {
                        'productos': [],
                        'total': float('inf'),  # Infinito si no tiene todos
                        'productos_faltantes': [],
                        'distancia_km': 0,
                        'tiempo_min': 0
                    }
                supermercados_totales[super_nombre]['productos_faltantes'].append(nombre_prod)
            else:
                if super_nombre not in supermercados_totales:
                    supermercados_totales[super_nombre] = {
                        'productos': [],
                        'total': 0,
                        'productos_faltantes': [],
                        'distancia_km': datos['distancia_km'],
                        'tiempo_min': datos['tiempo_min']
                    }
                
                if supermercados_totales[super_nombre]['total'] != float('inf'):
                    supermercados_totales[super_nombre]['productos'].append({
                        'nombre': nombre_prod,
                        'producto_real': datos['producto'].nombre,
                        'unidades': datos['unidades'],
                        'precio_unitario': datos['precio_unitario'],
                        'subtotal': datos['subtotal'],
                        'url': datos.get('url', '#')
                    })
                    supermercados_totales[super_nombre]['total'] += datos['subtotal']
    
    # Filtrar solo los que tienen todos los productos
    supers_completos = {k: v for k, v in supermercados_totales.items() 
                       if v['total'] != float('inf') and len(v['productos_faltantes']) == 0}
    
    if supers_completos:
        mejor_super_unico = min(supers_completos.keys(), 
                               key=lambda s: supers_completos[s]['total'])
        datos_mejor_unico = supers_completos[mejor_super_unico]
        total_unico = datos_mejor_unico['total']
    else:
        # Si ninguno tiene todos, tomar el que tenga más productos
        mejor_super_unico = min(supermercados_totales.keys(),
                               key=lambda s: len(supermercados_totales[s]['productos_faltantes']))
        datos_mejor_unico = supermercados_totales[mejor_super_unico]
        total_unico = datos_mejor_unico['total']
    
    return lista_compra_optimizada, total_optimizado, {mejor_super_unico: datos_mejor_unico}, total_unico


def mostrar_lista_compra_optimizada(
    lista_compra_opt: Dict, 
    total_opt: float,
    super_unico: Dict,
    total_unico: float
):
    """
    Muestra la lista de compra con DOS opciones: optimizada vs un solo super
    """
    st.markdown("---")
    st.markdown("## 🎯 ¿Dónde Comprás?")
    
    # Selector de estrategia
    estrategia = st.radio(
        "Elegí tu estrategia de compra:",
        ["🚗 Todo en un solo supermercado (más cómodo)", 
         "💰 Optimizado por precio (visitás varios)"],
        index=0,  # Por defecto: un solo super
        key="estrategia_compra"  # Key para session_state
    )
    
    # Guardar en session_state para usar en otras partes
    st.session_state.estrategia_seleccionada = estrategia
    
    st.markdown("---")
    
    if "un solo" in estrategia.lower():
        # OPCIÓN 1: Todo en un supermercado
        st.markdown("### 🏪 Comprá Todo en Un Solo Lugar")
        
        super_nombre, datos = list(super_unico.items())[0]
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total", f"${datos['total']:,.2f}")
        with col2:
            st.metric("📦 Productos", len(datos['productos']))
        with col3:
            st.metric("📍 Distancia", f"{datos['distancia_km']} km")
        with col4:
            ahorro = total_unico - total_opt
            st.metric("💸 vs Optimizado", f"+${ahorro:,.2f}", delta_color="inverse")
        
        st.markdown(f"### 🛒 {super_nombre}")
        
        # Productos con links
        for prod in datos['productos']:
            st.markdown(f"""
            <div style="
                background: #2a2a2a;
                padding: 0.8rem;
                border-radius: 5px;
                margin: 0.5rem 0;
                border-left: 3px solid #667eea;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <strong>{prod['unidades']}x {prod['nombre'].title()}</strong><br>
                        <small style="color: #999;">{prod['producto_real'][:60]}...</small><br>
                        <span style="color: #4ade80; font-weight: bold;">${prod['subtotal']:,.2f}</span>
                        <span style="color: #666;"> (${prod['precio_unitario']:,.2f} c/u)</span>
                    </div>
                    <a href="{prod.get('url', '#')}" target="_blank" style="
                        background: #667eea;
                        color: white;
                        padding: 0.5rem 1rem;
                        border-radius: 5px;
                        text-decoration: none;
                        font-size: 0.85rem;
                        white-space: nowrap;
                    ">🔗 Ver</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Advertencia si faltan productos
        if datos.get('productos_faltantes'):
            st.warning(f"⚠️ **Productos no disponibles:** {', '.join(datos['productos_faltantes'])}")
        
        # Total
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            text-align: center;
        ">
            <div style="font-size: 1.2rem; color: #fff; opacity: 0.9; margin-bottom: 0.5rem;">
                💰 TOTAL EN {super_nombre.upper()}
            </div>
            <div style="font-size: 3rem; font-weight: bold; color: #fff;">
                ${datos['total']:,.2f}
            </div>
            <div style="font-size: 0.9rem; color: #fff; opacity: 0.8; margin-top: 1rem;">
                🚗 Un solo viaje • 📍 {datos['distancia_km']} km
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.success(f"🎉 **¡Súper práctico!** Hacés una sola compra en un lugar.")
    
    else:
        # OPCIÓN 2: Optimizado por precio
        st.markdown("### 💰 Compra Optimizada (Mejor Precio)")
        
        # Ordenar por cantidad de productos
        lista_ordenada = sorted(lista_compra_opt.items(), 
                               key=lambda x: len(x[1]['productos']), 
                               reverse=True)
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total", f"${total_opt:,.2f}")
        with col2:
            st.metric("🏪 Supermercados", len(lista_compra_opt))
        with col3:
            ahorro = total_unico - total_opt
            st.metric("💸 Ahorrás", f"${ahorro:,.2f}")
        with col4:
            ahorro_pct = (ahorro / total_unico * 100) if total_unico > 0 else 0
            st.metric("📊 % Ahorro", f"{ahorro_pct:.1f}%")
        
        for super_nombre, datos in lista_ordenada:
            st.markdown(f"### 🏪 {super_nombre}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Subtotal", f"${datos['total']:,.2f}")
            with col2:
                st.metric("📦 Productos", len(datos['productos']))
            with col3:
                st.metric("📍 Distancia", f"{datos['distancia_km']} km")
            
            # Productos con links
            for prod in datos['productos']:
                st.markdown(f"""
                <div style="
                    background: #2a2a2a;
                    padding: 0.8rem;
                    border-radius: 5px;
                    margin: 0.5rem 0;
                    border-left: 3px solid #667eea;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <strong>{prod['unidades']}x {prod['nombre'].title()}</strong><br>
                            <small style="color: #999;">{prod['producto_real'][:60]}...</small><br>
                            <span style="color: #4ade80; font-weight: bold;">${prod['subtotal']:,.2f}</span>
                            <span style="color: #666;"> (${prod['precio_unitario']:,.2f} c/u)</span>
                        </div>
                        <a href="{prod.get('url', '#')}" target="_blank" style="
                            background: #667eea;
                            color: white;
                            padding: 0.5rem 1rem;
                            border-radius: 5px;
                            text-decoration: none;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">🔗 Ver</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Total final
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            text-align: center;
        ">
            <div style="font-size: 1.2rem; color: #fff; opacity: 0.9; margin-bottom: 0.5rem;">
                💰 TOTAL OPTIMIZADO
            </div>
            <div style="font-size: 3rem; font-weight: bold; color: #fff;">
                ${total_opt:,.2f}
            </div>
            <div style="font-size: 0.9rem; color: #fff; opacity: 0.8; margin-top: 1rem;">
                Comprando cada producto donde está más barato
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Resumen
        if len(lista_compra_opt) > 1:
            st.info(f"💡 **Estrategia:** Tenés que visitar {len(lista_compra_opt)} supermercados para obtener el mejor precio.")
        else:
            st.success(f"🎉 **¡Perfecto!** Todos los productos están más baratos en el mismo supermercado.")