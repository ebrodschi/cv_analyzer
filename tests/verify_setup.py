#!/usr/bin/env python3
"""
Script de verificación post-instalación para CV Analyzer.
Verifica que todo esté configurado correctamente.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Verifica versión de Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ requerido")
        print(f"   Tu versión: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Verifica que las dependencias estén instaladas."""
    required = [
        "streamlit",
        "pandas",
        "pydantic",
        "yaml",
        "fitz",  # pymupdf
        "docx",
        "pdfplumber",
        "openpyxl",
    ]

    missing = []
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False

    print("✅ Todas las dependencias instaladas")
    return True


def check_env_file():
    """Verifica que .env exista."""
    if not Path(".env").exists():
        print("⚠️  Archivo .env no encontrado")
        print("   Ejecuta: cp .env.example .env")
        print("   Luego edita .env con tu API key")
        return False

    print("✅ Archivo .env existe")
    return True


def check_api_key():
    """Verifica que API key esté configurada."""
    # Intentar cargar .env
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "sk-your-openai-api-key-here" in content:
                print("⚠️  API key no configurada en .env")
                print("   Edita .env y reemplaza con tu key real")
                return False
            elif "OPENAI_API_KEY=" in content:
                print("✅ API key configurada en .env")
                return True
    except:
        pass

    # Verificar variable de entorno
    if os.getenv("OPENAI_API_KEY"):
        print("✅ API key encontrada en variables de entorno")
        return True

    print("⚠️  API key no encontrada")
    return False


def check_file_structure():
    """Verifica estructura de archivos."""
    required_dirs = ["llm_client", "ingestion", "parsing", "schema", "utils", "tests"]
    required_files = ["app.py", "requirements.txt"]

    all_ok = True

    for dir_name in required_dirs:
        if not Path(dir_name).is_dir():
            print(f"❌ Directorio faltante: {dir_name}/")
            all_ok = False

    for file_name in required_files:
        if not Path(file_name).is_file():
            print(f"❌ Archivo faltante: {file_name}")
            all_ok = False

    if all_ok:
        print("✅ Estructura de archivos correcta")

    return all_ok


def check_imports():
    """Verifica que los módulos locales se importen correctamente."""
    try:
        from llm_client.base import BaseLLMClient
        from parsing.pdf import parse_pdf
        from schema.yaml_loader import get_default_schema

        print("✅ Módulos locales importan correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False


def main():
    """Ejecuta todas las verificaciones."""
    print("🔍 CV Analyzer - Verificación de Instalación\n")
    print("=" * 50)

    checks = [
        ("Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Archivo .env", check_env_file),
        ("API Key", check_api_key),
        ("Estructura", check_file_structure),
        ("Imports", check_imports),
    ]

    results = []

    for name, check_func in checks:
        print(f"\n📋 Verificando {name}...")
        result = check_func()
        results.append(result)

    print("\n" + "=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Resultado: {passed}/{total} verificaciones exitosas\n")

    if passed == total:
        print("✅ ¡Todo configurado correctamente!")
        print("\n🚀 Siguiente paso:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Hay problemas que resolver antes de continuar")
        print("\n📖 Consulta:")
        print("   - README.md para instrucciones detalladas")
        print("   - QUICKSTART.md para inicio rápido")

    print()


if __name__ == "__main__":
    main()
