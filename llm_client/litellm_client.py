"""
Cliente LLM genérico usando LiteLLM.
Soporta múltiples proveedores (Anthropic, Azure, etc).
"""

import os
from typing import Any, Dict, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMClient
from .prompt_templates import PromptConfig, create_default_config


class LiteLLMClient(BaseLLMClient):
    """
    Cliente genérico usando LiteLLM.
    Soporta Anthropic, Azure OpenAI, Cohere, etc.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.1,
        max_tokens: Optional[int] = 2000,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs,
    ):
        """
        Inicializa cliente LiteLLM.

        Args:
            model: Modelo (ej: claude-3-sonnet-20240229, azure/gpt-4)
            temperature: Temperatura
            max_tokens: Máximo de tokens
            api_key: API key (se infiere del proveedor si no se provee)
            api_base: URL base de la API (para proveedores custom)
            **kwargs: Parámetros adicionales
        """
        super().__init__(model, temperature, max_tokens, **kwargs)

        self.api_key = api_key
        self.api_base = api_base

        # Intentar importar litellm
        try:
            import litellm

            self.litellm = litellm

            # Configurar API key si se provee
            if self.api_key:
                # LiteLLM usa variables de entorno, las seteamos temporalmente
                self._setup_api_keys()

        except ImportError:
            raise ImportError(
                "Librería 'litellm' no instalada. " "Instala con: pip install litellm"
            )

    def _setup_api_keys(self):
        """
        Configura API keys según el proveedor detectado en el modelo.
        """
        model_lower = self.model.lower()

        if "claude" in model_lower or "anthropic" in model_lower:
            if not os.getenv("ANTHROPIC_API_KEY") and self.api_key:
                os.environ["ANTHROPIC_API_KEY"] = self.api_key

        elif "azure" in model_lower:
            if not os.getenv("AZURE_API_KEY") and self.api_key:
                os.environ["AZURE_API_KEY"] = self.api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def extract_profile(
        self,
        text: str,
        schema: Dict[str, Any],
        prompt_config: Optional[PromptConfig] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Extrae perfil usando LiteLLM.

        Args:
            text: Texto del CV
            schema: Esquema de extracción
            prompt_config: Configuración de prompts (especialidad, localidad, criterios)
            retry_count: Contador de reintentos

        Returns:
            Diccionario con datos extraídos
        """
        from schema.validator import (
            generate_correction_prompt,
            parse_json_safely,
            validate_extraction,
        )

        # Si no hay configuración, usar la predeterminada
        if prompt_config is None:
            prompt_config = create_default_config()

        # Construir prompts
        system_prompt, user_prompt = self._build_extraction_prompt(
            text, schema, prompt_config
        )

        # Preparar mensajes
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Llamar a LiteLLM
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
            }

            if self.max_tokens:
                kwargs["max_tokens"] = self.max_tokens

            if self.api_base:
                kwargs["api_base"] = self.api_base

            response = self.litellm.completion(**kwargs)
            response_text = response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error llamando a LiteLLM: {str(e)}")

        # Parsear JSON
        data, parse_error = parse_json_safely(response_text)

        if parse_error:
            if retry_count < 1:  # Solo 1 reintento
                correction_prompt = generate_correction_prompt(
                    response_text, parse_error, schema
                )
                return self._retry_with_correction(
                    correction_prompt, schema, retry_count + 1, text, prompt_config
                )
            else:
                raise ValueError(f"No se pudo parsear JSON: {parse_error}")

        # Validar
        is_valid, validated_data, validation_error = validate_extraction(data, schema)

        if not is_valid:
            print(f"❌ DEBUG Validación falló en intento {retry_count}:")
            print(f"   Error: {validation_error}")
            print(f"   Datos recibidos keys: {list(data.keys())}")

            # Mostrar el contenido del campo problemático si está en el error
            if "idiomas" in validation_error and "idiomas" in data:
                import json

                print(
                    f"   Valor de 'idiomas' recibido: {json.dumps(data['idiomas'], indent=2, ensure_ascii=False)}"
                )

            if retry_count < 1:  # Solo 1 reintento
                print(f"   🔄 Disparando retry con corrección...")
                correction_prompt = generate_correction_prompt(
                    response_text, validation_error, schema
                )
                return self._retry_with_correction(
                    correction_prompt, schema, retry_count + 1, text, prompt_config
                )
            else:
                raise ValueError(f"Validación falló: {validation_error}")
        else:
            print(f"✅ DEBUG Validación exitosa en intento {retry_count}")

        return validated_data

    def _retry_with_correction(
        self,
        correction_prompt: str,
        schema: Dict[str, Any],
        retry_count: int,
        text: str,
        prompt_config: Optional[PromptConfig] = None,
    ) -> Dict[str, Any]:
        """Reintenta con corrección."""
        from schema.validator import parse_json_safely, validate_extraction

        # Construir prompts con el CV completo
        system_prompt, user_prompt = self._build_extraction_prompt(
            text, schema, prompt_config
        )

        # Agregar el mensaje de corrección al user prompt
        full_user_prompt = f"""{user_prompt}

---
IMPORTANTE: Tu respuesta anterior tuvo el siguiente error:
{correction_prompt}

Por favor, genera una respuesta completa y correcta que incluya TODOS los campos del schema."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_prompt},
        ]

        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
            }

            if self.max_tokens:
                kwargs["max_tokens"] = self.max_tokens

            response = self.litellm.completion(**kwargs)
            response_text = response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error en reintento: {str(e)}")

        data, parse_error = parse_json_safely(response_text)
        if parse_error:
            raise ValueError(f"Error parseando JSON en reintento: {parse_error}")

        is_valid, validated_data, validation_error = validate_extraction(data, schema)
        if not is_valid:
            raise ValueError(f"Validación falló en reintento: {validation_error}")

        return validated_data

    def _build_extraction_prompt(
        self,
        text: str,
        schema: Dict[str, Any],
        prompt_config: Optional[PromptConfig] = None,
    ) -> tuple[str, str]:
        """Construye prompts."""
        # Si no hay configuración, usar la predeterminada
        if prompt_config is None:
            prompt_config = create_default_config()

        # Usar el sistema de templates para construir el prompt completo
        system_prompt, user_prompt = prompt_config.build_full_prompt(text, schema)

        return system_prompt, user_prompt
