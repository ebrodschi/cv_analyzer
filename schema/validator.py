"""
Validación de respuestas del LLM usando pydantic y jsonschema.
"""

import json
from typing import Any, Dict, Optional, Type

import jsonschema
from pydantic import BaseModel, Field, ValidationError, create_model


def validate_extraction(
    data: Dict[str, Any], schema: Dict[str, Any], use_pydantic: bool = True
) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Valida datos extraídos contra un esquema.

    Args:
        data: Datos extraídos por el LLM
        schema: Esquema en formato personalizado (de yaml_loader)
        use_pydantic: Si usar pydantic (True) o jsonschema (False)

    Returns:
        Tupla (es_válido, datos_validados, mensaje_error)
    """
    if use_pydantic:
        return _validate_with_pydantic(data, schema)
    else:
        return _validate_with_jsonschema(data, schema)


def _preprocess_data(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pre-procesa los datos para convertir tipos cuando sea necesario.
    Esto ayuda a manejar casos donde el LLM devuelve strings en lugar de enteros/booleanos.

    Args:
        data: Datos a pre-procesar
        schema: Esquema con las definiciones de tipos

    Returns:
        Datos pre-procesados con tipos convertidos
    """
    processed_data = data.copy()

    # Crear un mapa de nombre -> tipo esperado
    type_map = {var["name"]: var["type"] for var in schema.get("variables", [])}

    for key, value in processed_data.items():
        if key not in type_map or value is None:
            continue

        expected_type = type_map[key]

        # Convertir strings a integers
        if expected_type == "integer" and isinstance(value, str):
            try:
                # Intentar extraer el número de strings como "8/10" o "8 puntos"
                import re

                match = re.search(r"\d+", value)
                if match:
                    processed_data[key] = int(match.group())
                else:
                    processed_data[key] = None
            except (ValueError, AttributeError):
                processed_data[key] = None

        # Convertir strings a floats
        elif expected_type == "float" and isinstance(value, str):
            try:
                processed_data[key] = float(value)
            except ValueError:
                processed_data[key] = None

        # Convertir strings a booleans
        elif expected_type == "boolean" and isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ["true", "yes", "sí", "si", "1", "verdadero"]:
                processed_data[key] = True
            elif value_lower in ["false", "no", "0", "falso"]:
                processed_data[key] = False
            else:
                processed_data[key] = None

    return processed_data


def _validate_with_pydantic(
    data: Dict[str, Any], schema: Dict[str, Any]
) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Valida usando pydantic.

    Args:
        data: Datos a validar
        schema: Esquema personalizado

    Returns:
        Tupla (es_válido, datos_validados, mensaje_error)
    """
    try:
        # DEBUG: Ver datos ANTES de pre-procesamiento
        if "score_general" in data:
            print(
                f"🔍 DEBUG Pre-validación - score_general RAW: {repr(data['score_general'])} (tipo: {type(data['score_general']).__name__})"
            )

        # Pre-procesar datos para convertir tipos cuando sea necesario
        data = _preprocess_data(data, schema)

        # DEBUG: Ver datos después de pre-procesamiento
        if "score_general" in data:
            print(
                f"🔧 DEBUG Post-preprocesamiento - score_general: {data['score_general']} (tipo: {type(data['score_general']).__name__})"
            )

        # Crear modelo pydantic dinámico
        model = create_pydantic_model(schema)

        # Validar datos
        validated = model(**data)

        # Convertir a dict
        validated_dict = validated.model_dump()

        return True, validated_dict, None

    except ValidationError as e:
        error_msg = _format_pydantic_errors(e)
        return False, None, error_msg

    except Exception as e:
        return False, None, f"Error inesperado en validación: {str(e)}"


def _validate_with_jsonschema(
    data: Dict[str, Any], schema: Dict[str, Any]
) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Valida usando jsonschema.

    Args:
        data: Datos a validar
        schema: Esquema personalizado

    Returns:
        Tupla (es_válido, datos_validados, mensaje_error)
    """
    try:
        from schema.yaml_loader import schema_to_json_schema

        # Convertir a JSON Schema
        json_schema = schema_to_json_schema(schema)

        # Validar
        jsonschema.validate(instance=data, schema=json_schema)

        return True, data, None

    except jsonschema.exceptions.ValidationError as e:
        error_msg = f"Error de validación en '{e.json_path}': {e.message}"
        return False, None, error_msg

    except Exception as e:
        return False, None, f"Error inesperado en validación: {str(e)}"


def create_pydantic_model(schema: Dict[str, Any]) -> Type[BaseModel]:
    """
    Crea un modelo Pydantic dinámico a partir del esquema.

    Args:
        schema: Esquema personalizado

    Returns:
        Clase BaseModel de pydantic
    """
    from pydantic import ConfigDict

    fields = {}

    for var in schema["variables"]:
        name = var["name"]
        var_type = var["type"]
        required = var.get("required", False)

        # Determinar tipo Python y configuración de Field
        python_type, field_config = _get_pydantic_field(var)

        # Configurar como opcional si no es required
        if not required:
            python_type = Optional[python_type]
            if field_config is None:
                field_config = Field(default=None)
            else:
                field_config.default = None

        # Agregar campo
        if field_config:
            fields[name] = (python_type, field_config)
        else:
            fields[name] = (python_type, ...)

    # Crear modelo con configuración que permite coerción de tipos
    model = create_model(
        "CVExtractionModel",
        __config__=ConfigDict(
            str_strip_whitespace=True,  # Eliminar espacios en strings
            validate_default=True,  # Validar valores por defecto
            arbitrary_types_allowed=True,  # Permitir tipos arbitrarios
        ),
        **fields,
    )

    return model


def _get_pydantic_field(var: Dict[str, Any]) -> tuple[Type, Optional[Any]]:
    """
    Determina el tipo Python y configuración de Field para una variable.

    Args:
        var: Definición de variable

    Returns:
        Tupla (tipo_python, field_config)
    """
    from typing import List

    var_type = var["type"]
    field_config = None

    if var_type == "string":
        python_type = str
        if "format" in var:
            # Pydantic soporta validación de email directamente
            if var["format"] == "email":
                from pydantic import EmailStr

                python_type = EmailStr

    elif var_type == "integer":
        python_type = int
        kwargs = {}
        if "min" in var:
            kwargs["ge"] = var["min"]
        if "max" in var:
            kwargs["le"] = var["max"]
        if kwargs:
            field_config = Field(**kwargs)

    elif var_type == "float":
        python_type = float

    elif var_type == "boolean":
        python_type = bool

    elif var_type == "categorical":
        from typing import Literal

        # Crear Literal con los valores permitidos
        allowed = tuple(var["allowed_values"])
        python_type = Literal[allowed]

    elif var_type == "list[string]":
        python_type = List[str]

    elif var_type == "list[integer]":
        python_type = List[int]

    elif var_type == "list[object]":
        # Crear modelo anidado para objetos en la lista
        if "properties" in var:
            nested_fields = {}
            for prop_name, prop_type in var["properties"].items():
                if isinstance(prop_type, str):
                    nested_fields[prop_name] = (_type_string_to_python(prop_type), ...)
                elif isinstance(prop_type, list):
                    # Es un enum
                    from typing import Literal

                    enum_type = Literal[tuple(prop_type)]
                    nested_fields[prop_name] = (enum_type, ...)

            nested_model = create_model(f'{var["name"].title()}Item', **nested_fields)
            python_type = List[nested_model]
        else:
            python_type = List[dict]

    elif var_type == "object":
        python_type = dict

    else:
        python_type = Any

    return python_type, field_config


def _type_string_to_python(type_str: str) -> Type:
    """
    Convierte string de tipo a tipo Python.

    Args:
        type_str: Nombre del tipo como string

    Returns:
        Tipo Python correspondiente
    """
    type_map = {
        "string": str,
        "integer": int,
        "float": float,
        "boolean": bool,
    }
    return type_map.get(type_str, str)


def _format_pydantic_errors(error: ValidationError) -> str:
    """
    Formatea errores de pydantic de manera legible.

    Args:
        error: ValidationError de pydantic

    Returns:
        Mensaje de error formateado
    """
    errors = []
    for err in error.errors():
        loc = " -> ".join(str(l) for l in err["loc"])
        msg = err["msg"]
        errors.append(f"  • {loc}: {msg}")

    return "Errores de validación:\n" + "\n".join(errors)


def parse_json_safely(text: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Intenta parsear JSON de manera segura, con limpieza de texto común.

    Args:
        text: Texto que debería contener JSON

    Returns:
        Tupla (datos_parseados, error)
    """
    # Limpiar texto común
    text = text.strip()

    # Remover markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        # Remover primera y última línea si son ```
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    # Intentar parsear
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            return None, "El JSON parseado no es un objeto"
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Error parseando JSON: {str(e)}"


def generate_correction_prompt(
    original_response: str, validation_error: str, schema: Dict[str, Any]
) -> str:
    """
    Genera un prompt de corrección cuando la validación falla.

    Args:
        original_response: Respuesta original del LLM
        validation_error: Mensaje de error de validación
        schema: Esquema esperado

    Returns:
        Prompt de corrección
    """
    return f"""Tu respuesta anterior no pudo validarse correctamente.

Error encontrado:
{validation_error}

Tu respuesta original fue:
{original_response[:500]}...

Por favor, corrige el JSON para que cumpla exactamente con el esquema requerido.
Asegúrate de:
1. Que el JSON sea válido (sin comas extra, comillas correctas)
2. Que todos los campos required estén presentes
3. Que los tipos de datos sean correctos (integer como número, no string)
4. Que los valores categorical sean exactamente uno de los permitidos
5. Que las listas tengan el formato correcto

Responde ÚNICAMENTE con el JSON corregido, sin explicaciones ni markdown."""
