"""
Carga y validación de esquemas YAML para definir variables de extracción.
"""

from typing import Any, Dict, List

import yaml


def get_default_schema(especialidad: str = "electricista") -> str:
    """
    Retorna el esquema YAML por defecto, adaptado a la especialidad.

    Args:
        especialidad: Especialidad seleccionada (electricista, electromecanico, mecanico, pañolero, personalizado)

    Returns:
        String con el esquema YAML por defecto
    """
    # Mapeo de especialidad a nombre de campo de experiencia
    experiencia_field_map = {
        "electricista": "experiencia_electricista_confirmada",
        "electromecanico": "experiencia_electromecanico_confirmada",
        "mecanico": "experiencia_mecanico_industrial_confirmada",
        "pañolero": "experiencia_pañol_depositos_confirmada",
        "personalizado": "experiencia_confirmada",
    }

    experiencia_field = experiencia_field_map.get(
        especialidad, "experiencia_confirmada"
    )

    return f"""version: 1
variables:
  # Información de contacto
  - name: nombre
    type: string
    required: false
  - name: mail
    type: string
    format: email
    required: false
  - name: telefono
    type: string
    required: false

  # Información del CV
  - name: hay_foto_en_cv
    type: boolean
    required: false

  # Educación
  - name: primaria_completa
    type: boolean
    required: true
  - name: secundaria_completa
    type: boolean
    required: true
  - name: secundaria_tecnica
    type: boolean
    required: false
    description: Indica si el secundario cursado fue una escuela técnica
  - name: titulo_secundario
    type: string
    required: false
    description: Título obtenido en el secundario (ej. "Técnico Electromecánico", "Bachiller", "Técnico Electricista", etc.)
  - name: terciario_completo
    type: boolean
    required: false

  # Experiencia laboral
  - name: {experiencia_field}
    type: boolean
    required: true
  - name: años_experiencia
    type: integer
    min: 0
    max: 50
    required: false

  # Ubicación y edad
  - name: edad
    type: integer
    min: 18
    max: 80
    required: false
    description: Edad del candidato en años
  - name: localidad_residencia
    type: string
    required: false
    description: Localidad o ciudad donde reside el candidato
  - name: lugar_residencia_proximo
    type: boolean
    required: false
    description: Indica si reside cerca de la ubicación objetivo
  - name: edad_en_rango
    type: boolean
    required: false
    description: Indica si la edad está en el rango deseado

  # Evaluación y comentarios
  - name: score_general
    type: integer
    min: 1
    max: 10
    required: true
    description: Puntaje general del candidato evaluado del 1 al 10 basado en experiencia, educación y adecuación al perfil
  - name: observaciones
    type: string
    required: false
    description: Resumen del perfil en máximo 3 oraciones destacando aspectos no capturados en otros campos

  # Campos adicionales opcionales
  - name: idiomas
    type: list[object]
    properties:
      idioma: string
      nivel: string
    required: false
  - name: otros_oficios_tecnicos
    type: list[string]
    required: false
    description: Listado de otros conocimientos técnicos o oficios que posee el candidato
"""


def load_yaml_schema(yaml_content: str) -> Dict[str, Any]:
    """
    Carga y valida un esquema YAML.

    Args:
        yaml_content: Contenido del YAML como string

    Returns:
        Diccionario con el esquema parseado y validado

    Raises:
        ValueError: Si el YAML es inválido o no cumple con el formato esperado
    """
    try:
        schema = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(f"Error parseando YAML: {str(e)}")

    # Validar estructura básica
    if not isinstance(schema, dict):
        raise ValueError("El esquema debe ser un diccionario")

    if "version" not in schema:
        raise ValueError("El esquema debe incluir un campo 'version'")

    if "variables" not in schema:
        raise ValueError("El esquema debe incluir un campo 'variables'")

    if not isinstance(schema["variables"], list):
        raise ValueError("El campo 'variables' debe ser una lista")

    # Validar cada variable
    seen_names = set()
    for i, var in enumerate(schema["variables"]):
        _validate_variable(var, i, seen_names)

    return schema


def _validate_variable(var: Dict[str, Any], index: int, seen_names: set) -> None:
    """
    Valida una definición de variable individual.

    Args:
        var: Diccionario con la definición de la variable
        index: Índice de la variable en la lista
        seen_names: Set de nombres ya vistos (para detectar duplicados)

    Raises:
        ValueError: Si la variable no es válida
    """
    if not isinstance(var, dict):
        raise ValueError(f"Variable {index} debe ser un diccionario")

    # Campos requeridos
    if "name" not in var:
        raise ValueError(f"Variable {index} debe tener un campo 'name'")

    if "type" not in var:
        raise ValueError(
            f"Variable {index} ({var.get('name', '?')}) debe tener un campo 'type'"
        )

    # Validar nombre único
    name = var["name"]
    if name in seen_names:
        raise ValueError(f"Nombre de variable duplicado: {name}")
    seen_names.add(name)

    # Validar tipo
    valid_types = [
        "string",
        "integer",
        "float",
        "boolean",
        "categorical",
        "list[string]",
        "list[integer]",
        "list[object]",
        "object",
    ]

    var_type = var["type"]
    if var_type not in valid_types:
        raise ValueError(
            f"Tipo inválido para variable '{name}': {var_type}. "
            f"Tipos válidos: {', '.join(valid_types)}"
        )

    # Validaciones específicas por tipo
    if var_type == "categorical":
        if "allowed_values" not in var:
            raise ValueError(
                f"Variable categorical '{name}' debe tener 'allowed_values'"
            )
        if not isinstance(var["allowed_values"], list):
            raise ValueError(f"'allowed_values' de '{name}' debe ser una lista")

    if var_type == "integer":
        if "min" in var and not isinstance(var["min"], (int, float)):
            raise ValueError(f"'min' de '{name}' debe ser un número")
        if "max" in var and not isinstance(var["max"], (int, float)):
            raise ValueError(f"'max' de '{name}' debe ser un número")

    if var_type == "list[object]":
        if "properties" not in var:
            raise ValueError(f"Variable list[object] '{name}' debe tener 'properties'")
        if not isinstance(var["properties"], dict):
            raise ValueError(f"'properties' de '{name}' debe ser un diccionario")

    # Campo 'required' es opcional pero debe ser booleano si existe
    if "required" in var and not isinstance(var["required"], bool):
        raise ValueError(f"'required' de '{name}' debe ser booleano")


def schema_to_json_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte el esquema YAML personalizado a JSON Schema estándar.

    Args:
        schema: Esquema en formato personalizado

    Returns:
        JSON Schema compatible
    """
    properties = {}
    required = []

    for var in schema["variables"]:
        name = var["name"]
        var_type = var["type"]

        # Construir propiedad JSON Schema
        prop = _variable_to_json_schema_property(var)
        properties[name] = prop

        # Agregar a required si es necesario
        if var.get("required", False):
            required.append(name)

    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }

    if required:
        json_schema["required"] = required

    return json_schema


def _variable_to_json_schema_property(var: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte una variable individual a una propiedad JSON Schema.

    Args:
        var: Definición de variable

    Returns:
        Propiedad JSON Schema
    """
    var_type = var["type"]
    prop = {}

    # Mapeo de tipos
    if var_type == "string":
        prop["type"] = "string"
        if "format" in var:
            prop["format"] = var["format"]

    elif var_type == "integer":
        prop["type"] = "integer"
        if "min" in var:
            prop["minimum"] = var["min"]
        if "max" in var:
            prop["maximum"] = var["max"]

    elif var_type == "float":
        prop["type"] = "number"

    elif var_type == "boolean":
        prop["type"] = "boolean"

    elif var_type == "categorical":
        prop["type"] = "string"
        prop["enum"] = var["allowed_values"]

    elif var_type == "list[string]":
        prop["type"] = "array"
        prop["items"] = {"type": "string"}

    elif var_type == "list[integer]":
        prop["type"] = "array"
        prop["items"] = {"type": "integer"}

    elif var_type == "list[object]":
        prop["type"] = "array"
        if "properties" in var:
            items_props = {}
            for prop_name, prop_type in var["properties"].items():
                if isinstance(prop_type, str):
                    items_props[prop_name] = {"type": prop_type}
                elif isinstance(prop_type, list):
                    # Es un enum
                    items_props[prop_name] = {"type": "string", "enum": prop_type}
            prop["items"] = {"type": "object", "properties": items_props}

    elif var_type == "object":
        prop["type"] = "object"
        if "properties" in var:
            prop["properties"] = var["properties"]

    # Agregar descripción si existe
    if "description" in var:
        prop["description"] = var["description"]

    # Permitir null si no es required
    if not var.get("required", False):
        prop = {"anyOf": [prop, {"type": "null"}]}

    return prop


def get_variable_names(schema: Dict[str, Any]) -> List[str]:
    """
    Extrae los nombres de todas las variables del esquema.

    Args:
        schema: Esquema parseado

    Returns:
        Lista de nombres de variables
    """
    return [var["name"] for var in schema.get("variables", [])]
