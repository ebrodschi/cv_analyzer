@echo off
REM Script de inicio rápido para CV Analyzer (Windows)

echo 🚀 CV Analyzer - Quick Start
echo ==============================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

REM Activar entorno virtual
echo.
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo.
echo 📥 Instalando dependencias...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt

if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas

REM Verificar .env
echo.
if not exist ".env" (
    echo ⚠️  Archivo .env no encontrado
    echo 📝 Copiando .env.example a .env...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANTE: Edita el archivo .env y agrega tu API key
    echo    Abre .env con tu editor de texto favorito
    echo.
    pause
) else (
    echo ✅ Archivo .env encontrado
)

REM Ejecutar Streamlit
echo.
echo 🎉 Todo listo!
echo.
echo ▶️  Iniciando aplicación Streamlit...
echo.
streamlit run app.py
