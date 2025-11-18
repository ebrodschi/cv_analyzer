"""
Tests para el módulo de schema.
"""

import pytest

from schema.validator import parse_json_safely, validate_extraction
from schema.yaml_loader import (
    get_default_schema,
    load_yaml_schema,
    schema_to_json_schema,
)


def test_default_schema_is_valid():
    """Test que el schema por defecto es válido."""
    schema_yaml = get_default_schema()
    schema = load_yaml_schema(schema_yaml)

    assert "version" in schema
    assert "variables" in schema
    assert len(schema["variables"]) > 0


def test_schema_validation():
    """Test de validación de schema."""
    valid_yaml = """
version: 1
variables:
  - name: test_field
    type: string
    required: true
  - name: test_number
    type: integer
    min: 0
    max: 100
    required: false
"""

    schema = load_yaml_schema(valid_yaml)
    assert len(schema["variables"]) == 2


def test_invalid_schema():
    """Test que schema inválido lanza error."""
    invalid_yaml = """
version: 1
variables:
  - name: test_field
    # missing type
    required: true
"""

    with pytest.raises(ValueError):
        load_yaml_schema(invalid_yaml)


def test_duplicate_variable_names():
    """Test que nombres duplicados lanzan error."""
    duplicate_yaml = """
version: 1
variables:
  - name: test_field
    type: string
    required: true
  - name: test_field
    type: integer
    required: false
"""

    with pytest.raises(ValueError, match="duplicado"):
        load_yaml_schema(duplicate_yaml)


def test_schema_to_json_schema():
    """Test de conversión a JSON Schema."""
    yaml_str = """
version: 1
variables:
  - name: name
    type: string
    required: true
  - name: age
    type: integer
    min: 0
    max: 120
    required: false
"""

    schema = load_yaml_schema(yaml_str)
    json_schema = schema_to_json_schema(schema)

    assert "properties" in json_schema
    assert "name" in json_schema["properties"]
    assert "age" in json_schema["properties"]
    assert "name" in json_schema["required"]


def test_validate_extraction_success():
    """Test de validación exitosa."""
    schema_yaml = """
version: 1
variables:
  - name: nombre
    type: string
    required: true
  - name: edad
    type: integer
    min: 0
    required: false
"""

    schema = load_yaml_schema(schema_yaml)

    data = {"nombre": "Juan Pérez", "edad": 30}

    is_valid, validated, error = validate_extraction(data, schema)

    assert is_valid
    assert validated["nombre"] == "Juan Pérez"
    assert validated["edad"] == 30
    assert error is None


def test_validate_extraction_failure():
    """Test de validación fallida."""
    schema_yaml = """
version: 1
variables:
  - name: nombre
    type: string
    required: true
"""

    schema = load_yaml_schema(schema_yaml)

    # Falta campo required
    data = {"edad": 30}

    is_valid, validated, error = validate_extraction(data, schema)

    assert not is_valid
    assert validated is None
    assert error is not None


def test_parse_json_safely():
    """Test de parseo seguro de JSON."""
    # JSON válido
    valid_json = '{"name": "John", "age": 30}'
    data, error = parse_json_safely(valid_json)
    assert error is None
    assert data["name"] == "John"

    # JSON en markdown
    markdown_json = '```json\n{"name": "John"}\n```'
    data, error = parse_json_safely(markdown_json)
    assert error is None
    assert data["name"] == "John"

    # JSON inválido
    invalid_json = "{name: John}"
    data, error = parse_json_safely(invalid_json)
    assert data is None
    assert error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
