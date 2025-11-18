#!/bin/bash

# Script de inicio rápido para CV Analyzer

echo "🚀 CV Analyzer - Quick Start"
echo "=============================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.9+"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo ""
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo ""
echo "📥 Instalando dependencias..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Verificar .env
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "📝 Copiando .env.example a .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu API key:"
    echo "   nano .env"
    echo "   o"
    echo "   code .env"
    echo ""
    read -p "Presiona Enter cuando hayas configurado tu API key..."
else
    echo "✅ Archivo .env encontrado"
fi

# Verificar API key
if grep -q "sk-your-openai-api-key-here" .env 2>/dev/null; then
    echo ""
    echo "⚠️  ADVERTENCIA: Parece que no has configurado tu API key"
    echo "   Edita .env y reemplaza 'sk-your-openai-api-key-here' con tu key real"
    echo ""
fi

# Ejecutar Streamlit
echo ""
echo "🎉 Todo listo!"
echo ""
echo "▶️  Iniciando aplicación Streamlit..."
echo ""
streamlit run app.py
