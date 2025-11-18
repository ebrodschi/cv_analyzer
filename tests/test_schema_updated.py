#!/usr/bin/env python3
"""
Script de prueba para validar el schema actualizado con los nuevos campos.
"""

import sys

from schema.yaml_loader import get_default_schema, get_variable_names, load_yaml_schema


def test_default_schema():
    """Prueba el schema por defecto."""
    print("=" * 70)
    print("TEST: Schema por defecto")
    print("=" * 70)

    # Obtener schema YAML
    yaml_content = get_default_schema()
    print("\nContenido YAML:")
    print(yaml_content)

    # Cargar y validar
    try:
        schema = load_yaml_schema(yaml_content)
        print("\n✅ Schema válido!")

        # Obtener variables
        variables = get_variable_names(schema)
        print(f"\n📋 Variables definidas ({len(variables)}):")
        for i, var_name in enumerate(variables, 1):
            print(f"  {i:2d}. {var_name}")

        # Verificar campos nuevos
        required_fields = [
            "nombre",
            "mail",
            "telefono",
            "hay_foto_en_cv",
            "primaria_completa",
            "secundaria_completa",
            "terciario_completo",
            "experiencia_electricista_confirmada",
            "años_experiencia",
            "edad",  # NUEVO
            "localidad_residencia",  # NUEVO
            "lugar_residencia_proximo",
            "edad_en_rango",
            "score_general",
            "observaciones",
            "stack_tecnologico",
            "idiomas",
        ]

        print("\n🔍 Verificación de campos requeridos:")
        missing = []
        for field in required_fields:
            if field in variables:
                print(f"  ✅ {field}")
            else:
                print(f"  ❌ {field} - FALTANTE")
                missing.append(field)

        if missing:
            print(f"\n❌ Faltan {len(missing)} campos: {', '.join(missing)}")
            return False
        else:
            print("\n✅ Todos los campos requeridos están presentes!")
            return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_schema_details():
    """Prueba detalles específicos del schema."""
    print("\n" + "=" * 70)
    print("TEST: Detalles del schema")
    print("=" * 70)

    yaml_content = get_default_schema()
    schema = load_yaml_schema(yaml_content)

    # Verificar campo edad
    print("\n🔍 Campo 'edad':")
    edad_var = next((v for v in schema["variables"] if v["name"] == "edad"), None)
    if edad_var:
        print(f"  - Tipo: {edad_var['type']}")
        print(f"  - Min: {edad_var.get('min', 'N/A')}")
        print(f"  - Max: {edad_var.get('max', 'N/A')}")
        print(f"  - Required: {edad_var.get('required', False)}")
        print(f"  - Descripción: {edad_var.get('description', 'N/A')}")
    else:
        print("  ❌ Campo no encontrado")
        return False

    # Verificar campo localidad_residencia
    print("\n🔍 Campo 'localidad_residencia':")
    loc_var = next(
        (v for v in schema["variables"] if v["name"] == "localidad_residencia"), None
    )
    if loc_var:
        print(f"  - Tipo: {loc_var['type']}")
        print(f"  - Required: {loc_var.get('required', False)}")
        print(f"  - Descripción: {loc_var.get('description', 'N/A')}")
    else:
        print("  ❌ Campo no encontrado")
        return False

    # Verificar campo observaciones
    print("\n🔍 Campo 'observaciones':")
    obs_var = next(
        (v for v in schema["variables"] if v["name"] == "observaciones"), None
    )
    if obs_var:
        print(f"  - Tipo: {obs_var['type']}")
        print(f"  - Required: {obs_var.get('required', False)}")
        print(f"  - Descripción: {obs_var.get('description', 'N/A')}")

        # Verificar que la descripción menciona el resumen
        if "resumen" in obs_var.get("description", "").lower():
            print("  ✅ Descripción incluye instrucción de resumen")
        else:
            print("  ⚠️  Descripción no menciona 'resumen'")
    else:
        print("  ❌ Campo no encontrado")
        return False

    return True


def main():
    """Función principal."""
    print("\n" + "🧪" * 35)
    print("PRUEBAS DEL SCHEMA ACTUALIZADO")
    print("🧪" * 35 + "\n")

    # Ejecutar tests
    test1 = test_default_schema()
    test2 = test_schema_details()

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"Test Schema por defecto: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Test Detalles del schema: {'✅ PASS' if test2 else '❌ FAIL'}")

    if test1 and test2:
        print("\n🎉 Todos los tests pasaron exitosamente!")
        return 0
    else:
        print("\n❌ Algunos tests fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())
