"""
Clase base abstracta para clientes LLM.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .prompt_templates import PromptConfig


class BaseLLMClient(ABC):
    """
    Interfaz abstracta para clientes LLM.

    Permite abstraer la implementación específica del proveedor de LLM.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs,
    ):
        """
        Inicializa el cliente LLM.

        Args:
            model: Nombre del modelo a usar
            temperature: Temperatura para la generación (0-1)
            max_tokens: Máximo de tokens en la respuesta
            **kwargs: Parámetros adicionales específicos del proveedor
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_params = kwargs

    @abstractmethod
    def extract_profile(
        self,
        text: str,
        schema: Dict[str, Any],
        prompt_config: Optional[PromptConfig] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Extrae información estructurada de un CV en texto plano.

        Args:
            text: Texto del CV
            schema: Esquema de datos a extraer (formato personalizado)
            prompt_config: Configuración de prompts (especialidad, localidad, criterios)
            retry_count: Número de intento (para reintentos internos)

        Returns:
            Diccionario con los datos extraídos

        Raises:
            Exception: Si falla la extracción después de todos los reintentos
        """
        pass

    @abstractmethod
    def _build_extraction_prompt(
        self,
        text: str,
        schema: Dict[str, Any],
        prompt_config: Optional[PromptConfig] = None,
    ) -> tuple[str, str]:
        """
        Construye el prompt del sistema y del usuario para extracción.

        Args:
            text: Texto del CV
            schema: Esquema de datos a extraer
            prompt_config: Configuración de prompts (especialidad, localidad, criterios)

        Returns:
            Tupla (system_prompt, user_prompt)
        """
        pass

    def _get_system_prompt(self) -> str:
        """
        Prompt del sistema base para todos los proveedores.

        Returns:
            System prompt
        """
        return """Sos un asistente experto en análisis de CVs (currículums vitae).
Tu tarea es extraer información estructurada de CVs en español o inglés.

IMPORTANTE:
- Debes responder EXCLUSIVAMENTE con JSON válido
- No incluyas explicaciones, comentarios ni texto adicional
- El JSON debe cumplir exactamente con el esquema proporcionado
- Si un campo no puede deducirse con alta confianza, usa null o lista vacía []
- Para campos numéricos, usa números (no strings)
- Para campos categorical, usa exactamente uno de los valores permitidos
- Sé preciso y conservador: mejor null que inventar información"""

    def _format_schema_for_prompt(self, schema: Dict[str, Any]) -> str:
        """
        Formatea el esquema para incluirlo en el prompt.

        Args:
            schema: Esquema en formato personalizado

        Returns:
            Descripción del esquema en texto
        """
        lines = ["Esquema JSON requerido:\n{"]

        for var in schema["variables"]:
            name = var["name"]
            var_type = var["type"]
            required = var.get("required", False)

            # Descripción del campo
            desc_parts = [f'  "{name}": ']

            if var_type == "string":
                desc_parts.append('"string"')
            elif var_type == "integer":
                desc_parts.append("number (entero)")
                if "min" in var or "max" in var:
                    range_info = []
                    if "min" in var:
                        range_info.append(f"min={var['min']}")
                    if "max" in var:
                        range_info.append(f"max={var['max']}")
                    desc_parts.append(f' ({", ".join(range_info)})')
            elif var_type == "categorical":
                allowed = ", ".join(f'"{v}"' for v in var["allowed_values"])
                desc_parts.append(f"uno de: [{allowed}]")
            elif var_type == "list[string]":
                desc_parts.append('["string", ...]')
            elif var_type == "list[object]":
                desc_parts.append("[{...}, ...]")
            else:
                desc_parts.append(f"{var_type}")

            if required:
                desc_parts.append(" [REQUERIDO]")
            else:
                desc_parts.append(" [opcional, puede ser null]")

            lines.append("".join(desc_parts))

        lines.append("}")

        return "\n".join(lines)
