"""
Verifica la instalación y versión de Docling.
Muestra información útil para debugging.
"""

import sys


def check_docling_installation():
    """Verifica que Docling esté instalado correctamente."""
    print("\n" + "=" * 60)
    print("🔍 Verificación de Instalación de Docling")
    print("=" * 60 + "\n")

    # 1. Verificar importación
    print("1️⃣ Verificando importación de Docling...")
    try:
        import docling

        print("   ✅ Docling instalado")
        print(
            f"   📦 Versión: {docling.__version__ if hasattr(docling, '__version__') else 'Desconocida'}"
        )
        print(f"   📁 Ubicación: {docling.__file__}")
    except ImportError as e:
        print(f"   ❌ Error importando Docling: {e}")
        print("\n   💡 Instala Docling con: pip install docling")
        return False

    # 2. Verificar módulos clave
    print("\n2️⃣ Verificando módulos clave...")
    modules_to_check = [
        "docling.document_converter",
        "docling.datamodel.base_models",
        "docling.datamodel.pipeline_options",
    ]

    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}: {e}")

    # 3. Verificar clases importantes
    print("\n3️⃣ Verificando clases importantes...")
    try:
        from docling.document_converter import DocumentConverter

        print("   ✅ DocumentConverter")

        from docling.datamodel.base_models import InputFormat

        print("   ✅ InputFormat")
        print(f"      - Valores disponibles: {[f.value for f in InputFormat]}")

        from docling.datamodel.pipeline_options import PdfPipelineOptions

        print("   ✅ PdfPipelineOptions")

        # Crear instancia para ver opciones
        options = PdfPipelineOptions()
        print(f"      - do_ocr (default): {options.do_ocr}")
        print(f"      - do_table_structure (default): {options.do_table_structure}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    # 4. Probar creación de DocumentConverter
    print("\n4️⃣ Probando creación de DocumentConverter...")

    # Test 1: Sin opciones
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        print("   ✅ Test 1: DocumentConverter() sin opciones - OK")
    except Exception as e:
        print(f"   ❌ Test 1 falló: {e}")

    # Test 2: Con opciones PDF
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter

        pdf_options = PdfPipelineOptions()
        pdf_options.do_ocr = True

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pdf_options,
            }
        )
        print("   ✅ Test 2: DocumentConverter con OCR habilitado - OK")
    except Exception as e:
        print(f"   ❌ Test 2 falló: {e}")
        import traceback

        traceback.print_exc()

    # 5. Mostrar dependencias
    print("\n5️⃣ Dependencias de Docling...")
    try:
        import pkg_resources

        docling_dist = pkg_resources.get_distribution("docling")

        print(f"   📦 Docling {docling_dist.version}")
        print(f"\n   Dependencias requeridas:")
        for req in docling_dist.requires():
            print(f"      - {req}")
    except Exception as e:
        print(f"   ⚠️ No se pudo obtener info de dependencias: {e}")

    # 6. Verificar backends disponibles
    print("\n6️⃣ Verificando backends disponibles...")
    backends = [
        "docling.backend.pypdfium2_backend",
        "docling.backend.docling_parse_backend",
    ]

    for backend in backends:
        try:
            __import__(backend)
            print(f"   ✅ {backend.split('.')[-1]}")
        except ImportError:
            print(f"   ⚠️ {backend.split('.')[-1]} no disponible")

    print("\n" + "=" * 60)
    print("✅ Verificación completada")
    print("=" * 60 + "\n")

    return True


def show_python_env():
    """Muestra información del entorno Python."""
    print("\n" + "=" * 60)
    print("🐍 Información del Entorno Python")
    print("=" * 60 + "\n")

    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path[0]}")

    # Listar paquetes instalados relevantes
    print("\n📦 Paquetes instalados relevantes:")
    try:
        import pkg_resources

        packages = [
            "docling",
            "pdfplumber",
            "pymupdf",
            "python-docx",
        ]

        for pkg in packages:
            try:
                dist = pkg_resources.get_distribution(pkg)
                print(f"   - {pkg}: {dist.version}")
            except pkg_resources.DistributionNotFound:
                print(f"   - {pkg}: ❌ No instalado")
    except ImportError:
        print("   ⚠️ pkg_resources no disponible")


if __name__ == "__main__":
    show_python_env()

    success = check_docling_installation()

    if success:
        print("\n✅ Todo parece estar bien instalado!")
        print("\n💡 Próximos pasos:")
        print("   1. Prueba con: python debug_ocr.py tu_archivo.pdf")
        print("   2. O procesa CVs en la app con OCR activado")
    else:
        print("\n❌ Hay problemas con la instalación de Docling")
        print("\n💡 Intenta:")
        print("   1. pip uninstall docling -y")
        print("   2. pip install docling")
        print("   3. Ejecuta este script nuevamente: python verify_docling.py")

    print()
