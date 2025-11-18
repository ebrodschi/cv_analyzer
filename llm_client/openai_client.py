"""
Cliente LLM para OpenAI.
"""

import json
import os
from typing import Any, Dict, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .base import BaseLLMClient
from .prompt_templates import PromptConfig, create_default_config


class OpenAIClient(BaseLLMClient):
    """
    Cliente para API de OpenAI.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: Optional[int] = 2000,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Inicializa cliente OpenAI.

        Args:
            model: Modelo de OpenAI (ej: gpt-4, gpt-3.5-turbo)
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens
            api_key: API key (si no se provee, se lee de variable de entorno)
            **kwargs: Parámetros adicionales (ignorados para compatibilidad)
        """
        super().__init__(model, temperature, max_tokens, **kwargs)

        # Obtener API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key no encontrada. "
                "Define OPENAI_API_KEY en variables de entorno."
            )

        # Inicializar cliente
        try:
            from openai import OpenAI

            # Solo pasar api_key, sin kwargs adicionales para evitar conflictos
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Librería 'openai' no instalada. " "Instala con: pip install openai"
            )
        except TypeError as e:
            # Si falla por argumentos inesperados, intentar sin kwargs
            raise ValueError(
                f"Error inicializando OpenAI client: {str(e)}. "
                "Verifica que tengas instalada la versión correcta: pip install openai>=1.0.0"
            )

    @retry(
        stop=stop_after_attempt(1),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
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
        Extrae perfil usando OpenAI API.

        Args:
            text: Texto del CV
            schema: Esquema de extracción
            prompt_config: Configuración de prompts (especialidad, localidad, criterios)
            retry_count: Contador de reintentos de validación

        Returns:
            Diccionario con datos extraídos y validados
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

        # Llamar a OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},  # Forzar JSON
            )

            response_text = response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error llamando a OpenAI API: {str(e)}")

        # Parsear JSON
        data, parse_error = parse_json_safely(response_text)

        if parse_error:
            if retry_count < 1:  # Solo 1 reintento
                # Reintentar con prompt de corrección
                correction_prompt = generate_correction_prompt(
                    response_text, parse_error, schema
                )
                return self._retry_with_correction(
                    correction_prompt, schema, retry_count + 1, text, prompt_config
                )
            else:
                raise ValueError(
                    f"No se pudo parsear JSON después de {retry_count + 1} intentos: {parse_error}"
                )

        # Validar contra esquema
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
                # Reintentar con prompt de corrección
                correction_prompt = generate_correction_prompt(
                    response_text, validation_error, schema
                )
                return self._retry_with_correction(
                    correction_prompt, schema, retry_count + 1, text, prompt_config
                )
            else:
                raise ValueError(
                    f"Validación falló después de {retry_count + 1} intentos: {validation_error}"
                )
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
        """
        Reintenta la extracción con un prompt de corrección.

        Args:
            correction_prompt: Prompt con instrucciones de corrección
            schema: Esquema de extracción
            retry_count: Contador de reintentos
            text: Texto completo del CV (para contexto completo)
            prompt_config: Configuración de prompts

        Returns:
            Datos extraídos y validados
        """
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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_user_prompt},
                ],
                temperature=0.1,  # Más determinístico para correcciones
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            response_text = response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error en reintento {retry_count}: {str(e)}")

        # Parsear y validar
        data, parse_error = parse_json_safely(response_text)
        if parse_error:
            raise ValueError(
                f"Error parseando JSON en reintento {retry_count}: {parse_error}"
            )

        is_valid, validated_data, validation_error = validate_extraction(data, schema)
        if not is_valid:
            raise ValueError(
                f"Validación falló en reintento {retry_count}: {validation_error}"
            )

        return validated_data

    def _build_extraction_prompt(
        self,
        text: str,
        schema: Dict[str, Any],
        prompt_config: Optional[PromptConfig] = None,
    ) -> tuple[str, str]:
        """
        Construye prompts para OpenAI.

        Args:
            text: Texto del CV
            schema: Esquema de extracción
            prompt_config: Configuración de prompts (especialidad, localidad, criterios)

        Returns:
            Tupla (system_prompt, user_prompt)
        """
        # Si no hay configuración, usar la predeterminada
        if prompt_config is None:
            prompt_config = create_default_config()

        # Usar el sistema de templates para construir el prompt completo
        system_prompt, user_prompt = prompt_config.build_full_prompt(text, schema)

        return system_prompt, user_prompt
