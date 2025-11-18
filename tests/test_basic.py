"""
Script de ejemplo para testear la funcionalidad básica sin UI.
Útil para debugging y pruebas rápidas.
"""

import os

from llm_client.openai_client import OpenAIClient
from schema.yaml_loader import get_default_schema, load_yaml_schema
from utils.text_clean import normalize_text


def test_basic_flow():
    """Test básico del flujo completo."""

    print("🧪 Testing CV Analyzer - Flujo Básico\n")

    # 1. Cargar schema
    print("1️⃣ Cargando schema...")
    schema_yaml = get_default_schema()
    schema = load_yaml_schema(schema_yaml)
    print(f"   ✅ Schema cargado con {len(schema['variables'])} variables\n")

    # 2. Inicializar cliente LLM
    print("2️⃣ Inicializando cliente LLM...")

    if not os.getenv("OPENAI_API_KEY"):
        print("   ❌ OPENAI_API_KEY no encontrada")
        print("   💡 Define la variable de entorno para continuar")
        return

    try:
        client = OpenAIClient(model="gpt-4o-mini", temperature=0.1)
        print("   ✅ Cliente OpenAI inicializado\n")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return

    # 3. Texto de ejemplo (CV simple)
    print("3️⃣ Preparando texto de ejemplo...")
    sample_cv = """
    Juan Pérez
    Email: juan.perez@example.com
    Teléfono: +54 11 1234-5678

    EXPERIENCIA LABORAL

    Desarrollador Python Senior - Empresa ABC (2020-2023)
    - Desarrollo de APIs con FastAPI
    - Implementación de pipelines de datos
    - 3 años de experiencia

    Data Analyst - Empresa XYZ (2018-2020)
    - Análisis de datos con Python y SQL
    - 2 años de experiencia

    EDUCACIÓN

    Licenciatura en Ciencias de la Computación
    Universidad Nacional de Buenos Aires (2014-2018)

    HABILIDADES

    Lenguajes: Python, JavaScript, SQL
    Frameworks: Django, FastAPI, React
    Data Science: Pandas, Scikit-learn, TensorFlow

    IDIOMAS

    Español: Nativo
    Inglés: Avanzado
    """

    normalized_text = normalize_text(sample_cv)
    print(f"   ✅ Texto normalizado ({len(normalized_text)} caracteres)\n")

    # 4. Extraer información
    print("4️⃣ Extrayendo información con LLM...")
    print("   ⏳ Esto puede tomar 10-30 segundos...\n")

    try:
        extracted_data = client.extract_profile(normalized_text, schema)

        print("   ✅ Extracción exitosa!\n")
        print("📊 DATOS EXTRAÍDOS:")
        print("=" * 50)

        for key, value in extracted_data.items():
            print(f"\n{key}:")
            print(f"  {value}")

        print("\n" + "=" * 50)
        print("\n✅ Test completado exitosamente!")

    except Exception as e:
        print(f"   ❌ Error en extracción: {e}")
        return


if __name__ == "__main__":
    test_basic_flow()
