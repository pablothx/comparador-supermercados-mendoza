#!/bin/bash

# Script de instalación rápida para el Comparador de Supermercados

echo "🛒 Instalando Comparador de Supermercados..."
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instalá Python 3.9 o superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Editá el archivo .env con tus credenciales de AWS"
    echo ""
fi

echo ""
echo "✅ Instalación completada!"
echo ""
echo "Para ejecutar la aplicación:"
echo "  1. Activá el entorno virtual: source venv/bin/activate"
echo "  2. Editá .env con tus credenciales de AWS"
echo "  3. Ejecutá: streamlit run src/app.py"
echo ""
echo "Para tests: python tests/test_basic.py"
echo ""
