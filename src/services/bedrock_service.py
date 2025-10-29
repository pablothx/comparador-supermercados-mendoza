"""
Servicio de AWS Bedrock para IA conversacional
"""
import json
import boto3
from typing import List, Dict, Optional
from botocore.exceptions import ClientError

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    BEDROCK_MODEL_ID
)


class BedrockService:
    """Servicio para interactuar con AWS Bedrock (Claude)"""
    
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, aws_region=None):
        """
        Inicializa el cliente de Bedrock
        
        Args:
            aws_access_key_id: AWS Access Key (opcional, usa env si no se provee)
            aws_secret_access_key: AWS Secret Key (opcional, usa env si no se provee)
            aws_region: AWS Region (opcional, usa env si no se provee)
        """
        import os
        
        # Usar credenciales provistas o del entorno
        access_key = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID', AWS_ACCESS_KEY_ID)
        secret_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY', AWS_SECRET_ACCESS_KEY)
        region = aws_region or os.getenv('AWS_REGION', AWS_REGION)
        
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.model_id = BEDROCK_MODEL_ID
        self.conversation_history = []
    
    def _validar_dominio(self, mensaje: str) -> bool:
        """
        Valida que el mensaje esté dentro del dominio permitido
        
        Args:
            mensaje: Mensaje del usuario
            
        Returns:
            True si está en el dominio, False si no
        """
        # Palabras que indican que es consulta de supermercado
        palabras_clave_validas = [
            "precio", "compra", "supermercado", "producto", 
            "ubicación", "distancia", "cerca", "barato",
            "comparar", "lista", "evento", "cumpleaños", "cumple",
            "asado", "cena", "comida", "bebida", "quiero", "necesito",
            "picada", "desayuno", "almuerzo", "merienda", "comer",
            "cocinar", "preparar", "hacer", "fiesta", "reunión",
            "niños", "personas", "gente", "familia", "amigos",
            "semanal", "mensual", "diario", "compras", "romántica",
            "completo", "ingredientes", "receta"
        ]
        
        # Productos comunes de supermercado (más flexible)
        productos_supermercado = [
            "arroz", "aceite", "yerba", "azucar", "sal", "pan", "leche",
            "fideos", "pasta", "harina", "cafe", "te", "galletitas",
            "carne", "pollo", "pescado", "hamburguesa", "salchicha", "pancho",
            "chorizo", "gaseosa", "coca", "sprite", "cerveza", "vino",
            "agua", "jugo", "papa", "tomate", "lechuga", "cebolla",
            "huevo", "queso", "manteca", "jamon", "mortadela",
            "sopa", "caldo", "pure", "mayonesa", "ketchup", "mostaza",
            "detergente", "jabon", "shampoo", "papel", "servilleta",
            "salame", "aceitunas", "maní", "almendras", "frutas",
            "verduras", "snack", "chips", "galletas", "dulce"
        ]
        
        mensaje_lower = mensaje.lower()
        
        # Si tiene alguna palabra clave O algún producto, es válido
        return (any(palabra in mensaje_lower for palabra in palabras_clave_validas) or
                any(producto in mensaje_lower for producto in productos_supermercado))
    
    def interpretar_consulta(self, mensaje: str) -> Dict:
        """
        Interpreta la consulta del usuario y extrae información estructurada CON CANTIDADES
        
        Args:
            mensaje: Consulta del usuario
            
        Returns:
            Diccionario con productos (con cantidades estimadas), evento, personas, etc.
        """
        # Validar dominio
        if not self._validar_dominio(mensaje):
            return {
                "error": "🛒 Solo puedo ayudarte con compras de supermercado.\n\n"
                        "Puedo:\n"
                        "• Comparar precios entre supermercados\n"
                        "• Calcular cantidades para eventos (cumpleaños, asado, etc.)\n"
                        "• Armar listas de compras\n"
                        "• Recomendar el mejor super según precio y distancia\n\n"
                        "💡 Ejemplos: \"cumpleaños para 30 niños\", \"asado para 10\", \"yerba y café\"",
                "tipo": "fuera_de_dominio"
            }
        
        prompt = f"""Sos un asistente experto en compras de supermercado en Argentina. 

Tu tarea es extraer información estructurada de la consulta del usuario E INTELIGENTEMENTE calcular las cantidades necesarias.

CONSULTA DEL USUARIO: "{mensaje}"

Extrae la siguiente información en formato JSON:
{{
    "productos": [
        {{
            "nombre": "nombre del producto",
            "cantidad_estimada": número (cantidad total necesaria),
            "unidad": "litros/kg/unidades/paquetes",
            "razonamiento": "breve explicación del cálculo"
        }}
    ],
    "evento": "tipo de evento si lo menciona",
    "personas": número de personas,
    "preferencias": "preferencias especiales si las menciona"
}}

REGLAS PARA CALCULAR CANTIDADES:
- Para BEBIDAS: estimar ~0.5L por persona (más en eventos sociales)
- Para CARNES/HAMBURGUESAS: estimar ~200-250g por persona
- Para PAN: estimar 2-3 unidades por persona
- Para SNACKS: estimar ~100g por persona
- Para TORTA: estimar ~150g por porción
- Para EVENTOS: aumentar 20-30% por las dudas
- Si NO menciona personas, asumir 1 unidad de cada producto

Ejemplos:
1. "quiero comprar arroz, aceite y yerba"
{{
    "productos": [
        {{"nombre": "arroz", "cantidad_estimada": 1, "unidad": "kg", "razonamiento": "1 persona, consumo estándar"}},
        {{"nombre": "aceite", "cantidad_estimada": 1, "unidad": "litros", "razonamiento": "1 persona, consumo estándar"}},
        {{"nombre": "yerba", "cantidad_estimada": 1, "unidad": "kg", "razonamiento": "1 persona, consumo estándar"}}
    ],
    "evento": null,
    "personas": 1,
    "preferencias": null
}}

2. "cumpleaños para 30 personas"
{{
    "productos": [
        {{"nombre": "gaseosas", "cantidad_estimada": 20, "unidad": "litros", "razonamiento": "30 personas × 0.5L + 30% extra = ~20L"}},
        {{"nombre": "panchos", "cantidad_estimada": 40, "unidad": "unidades", "razonamiento": "30 personas × 1.3 = ~40 panchos"}},
        {{"nombre": "hamburguesas", "cantidad_estimada": 35, "unidad": "unidades", "razonamiento": "30 personas × 1.2 = ~35 hamburguesas"}},
        {{"nombre": "pan", "cantidad_estimada": 70, "unidad": "unidades", "razonamiento": "30 personas × 2.5 = ~70 panes"}},
        {{"nombre": "papas fritas", "cantidad_estimada": 3, "unidad": "kg", "razonamiento": "30 personas × 100g = 3kg"}},
        {{"nombre": "torta", "cantidad_estimada": 5, "unidad": "kg", "razonamiento": "30 personas × 150g = 4.5kg ≈ 5kg"}}
    ],
    "evento": "cumpleaños",
    "personas": 30,
    "preferencias": null
}}

3. "asado para 10 personas"
{{
    "productos": [
        {{"nombre": "carne", "cantidad_estimada": 3, "unidad": "kg", "razonamiento": "10 personas × 300g = 3kg"}},
        {{"nombre": "chorizo", "cantidad_estimada": 2, "unidad": "kg", "razonamiento": "10 personas × 200g = 2kg"}},
        {{"nombre": "pan", "cantidad_estimada": 20, "unidad": "unidades", "razonamiento": "10 personas × 2 = 20 panes"}},
        {{"nombre": "cerveza", "cantidad_estimada": 15, "unidad": "litros", "razonamiento": "10 personas × 1.5L (asado) = 15L"}},
        {{"nombre": "gaseosas", "cantidad_estimada": 5, "unidad": "litros", "razonamiento": "10 personas × 0.5L = 5L"}}
    ],
    "evento": "asado",
    "personas": 10,
    "preferencias": null
}}

4. "picada para 8 personas"
{{
    "productos": [
        {{"nombre": "queso", "cantidad_estimada": 1, "unidad": "kg", "razonamiento": "8 personas × 120g = 1kg aprox"}},
        {{"nombre": "salame", "cantidad_estimada": 0.5, "unidad": "kg", "razonamiento": "8 personas × 60g = 0.5kg"}},
        {{"nombre": "jamón", "cantidad_estimada": 0.4, "unidad": "kg", "razonamiento": "8 personas × 50g = 0.4kg"}},
        {{"nombre": "aceitunas", "cantidad_estimada": 0.5, "unidad": "kg", "razonamiento": "8 personas × 60g = 0.5kg"}},
        {{"nombre": "maní", "cantidad_estimada": 0.3, "unidad": "kg", "razonamiento": "8 personas × 40g = 0.3kg"}},
        {{"nombre": "papas fritas", "cantidad_estimada": 1, "unidad": "kg", "razonamiento": "8 personas × 120g = 1kg"}},
        {{"nombre": "vino", "cantidad_estimada": 3, "unidad": "litros", "razonamiento": "8 personas × 0.4L = 3L aprox"}},
        {{"nombre": "gaseosas", "cantidad_estimada": 4, "unidad": "litros", "razonamiento": "8 personas × 0.5L = 4L"}}
    ],
    "evento": "picada",
    "personas": 8,
    "preferencias": null
}}

SÉ INTELIGENTE: ajusta las cantidades según el contexto (tipo de evento, cultura argentina, etc.)

Respondé SOLO con el JSON, sin explicaciones adicionales."""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.9
                })
            )
            
            response_body = json.loads(response['body'].read())
            contenido = response_body['content'][0]['text']
            
            # Extraer JSON del contenido
            import re
            json_match = re.search(r'\{.*\}', contenido, re.DOTALL)
            if json_match:
                resultado = json.loads(json_match.group())
                return resultado
            
            return {"error": "No se pudo interpretar la consulta", "tipo": "error_parseo"}
            
        except ClientError as e:
            print(f"Error en Bedrock: {e}")
            return {"error": "Error al procesar la consulta", "tipo": "error_servicio"}
        except Exception as e:
            print(f"Error inesperado: {e}")
            return {"error": str(e), "tipo": "error_inesperado"}
    
    def generar_recomendacion(
        self, 
        comparaciones: List[Dict],
        ubicacion: str
    ) -> str:
        """
        Genera una recomendación basada en las comparaciones de precios
        
        Args:
            comparaciones: Lista de comparaciones por supermercado
            ubicacion: Ubicación del usuario
            
        Returns:
            Texto con la recomendación
        """
        prompt = f"""Sos un asistente de compras inteligente. Analizá los siguientes datos y generá una recomendación CONCISA y ACCIONABLE.

UBICACIÓN DEL USUARIO: {ubicacion}

COMPARACIÓN DE PRECIOS:
{json.dumps(comparaciones, indent=2, ensure_ascii=False)}

Tu respuesta debe:
1. Recomendar la MEJOR opción (balance precio/distancia)
2. Mencionar cuánto se ahorra vs la opción más cara
3. Si hay una opción muy barata pero muy lejos, mencionarla como alternativa
4. Ser BREVE (máximo 4 líneas)

Formato de respuesta:
🏆 **[Supermercado]** es tu mejor opción
💰 Total: $X,XXX - Ahorrás $XXX vs [más caro]
📍 A X.X km (Y minutos)
[Opcional: breve comentario sobre alternativa si es relevante]

NO incluyas listas de productos, solo el resumen."""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 512,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5,
                    "top_p": 0.9
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Error generando recomendación: {e}")
            return "Error al generar recomendación"
    
    def reset_conversacion(self):
        """Resetea el historial de conversación"""
        self.conversation_history = []