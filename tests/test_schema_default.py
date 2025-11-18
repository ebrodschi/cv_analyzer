"""
Script de prueba para validar el schema por defecto.
"""

from schema.yaml_loader import get_default_schema, get_variable_names, load_yaml_schema


def test_default_schema():
    """Prueba el schema por defecto."""
    print("=" * 60)
    print("VALIDACIÓN DEL SCHEMA POR DEFECTO")
    print("=" * 60)

    # Obtener schema YAML
    yaml_content = get_default_schema()

    print("\n📄 Schema YAML:")
    print("-" * 60)
    print(yaml_content)

    # Cargar y validar
    try:
        schema = load_yaml_schema(yaml_content)
        print("\n✅ Schema validado correctamente!")

        # Mostrar variables
        variables = get_variable_names(schema)
        print(f"\n📋 Variables definidas ({len(variables)}):")
        print("-" * 60)
        for i, var_name in enumerate(variables, 1):
            # Obtener detalles de la variable
            var_info = next(v for v in schema["variables"] if v["name"] == var_name)
            var_type = var_info["type"]
            required = "✓" if var_info.get("required", False) else "○"
            print(f"{i:2}. [{required}] {var_name:40} ({var_type})")

        # Ejemplo de JSON esperado
        print("\n📊 Ejemplo de JSON de salida:")
        print("-" * 60)
        ejemplo = {
            "nombre": "Juan Pérez",
            "mail": "juan.perez@email.com",
            "telefono": "+54 11 1234-5678",
            "hay_foto_en_cv": True,
            "primaria_completa": True,
            "secundaria_completa": True,
            "terciario_completo": False,
            "experiencia_electricista_confirmada": True,
            "años_experiencia": 5,
            "lugar_residencia_proximo": True,
            "edad_en_rango": True,
            "score_general": 8,
            "observaciones": "Buen candidato con experiencia relevante",
            "stack_tecnologico": ["PLC", "Electricidad Industrial", "Neumática"],
            "idiomas": [{"idioma": "Español", "nivel": "nativo"}],
        }

        import json

        print(json.dumps(ejemplo, indent=2, ensure_ascii=False))

        print("\n" + "=" * 60)
        print("✅ VALIDACIÓN EXITOSA")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    test_default_schema()
