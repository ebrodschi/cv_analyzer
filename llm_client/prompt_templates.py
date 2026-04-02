"""
Sistema de plantillas de prompts configurables para análisis de CVs.
"""

from typing import Any, Dict, Optional

# Plantillas predefinidas de especialidades (mantenidas para backward compat)
ESPECIALIDAD_TEMPLATES = {
    "electricista": {
        "titulo": "Electricista de Mantenimiento Industrial",
        "experiencia_campo": "experiencia_electricista_confirmada",
        "descripcion_experiencia": "trabajo previo con tareas de mantenimiento eléctrico, electricidad industrial, electrónica industrial",
        "exclusiones": "electricidad de obra de construcción",
        "rango_edad": "25-45",
        "conocimientos_relevantes": "PLC, electricidad industrial, neumática, electrónica",
        "industrias_relevantes": "fábricas industriales y rubros afines alimenticio",
    },
    "electromecanico": {
        "titulo": "Electromecánico de Mantenimiento Industrial",
        "experiencia_campo": "experiencia_electromecanico_confirmada",
        "descripcion_experiencia": "trabajo previo con tareas de mantenimiento electromecánico industrial",
        "exclusiones": "electricidad de obra de construcción",
        "rango_edad": "25-45",
        "conocimientos_relevantes": "PLC, electricidad industrial, neumática, electromecánica",
        "industrias_relevantes": "fábricas industriales y rubros afines alimenticio",
    },
    "mecanico": {
        "titulo": "Mecánico Industrial",
        "experiencia_campo": "experiencia_mecanico_industrial_confirmada",
        "descripcion_experiencia": "trabajo previo con tareas de mantenimiento mecánico, soldador industrial",
        "exclusiones": "mecánico de obra de construcción",
        "rango_edad": "25-45",
        "conocimientos_relevantes": "soldadura de caños pequeñas medidas, soldaduras piping",
        "industrias_relevantes": "fábricas industriales",
    },
    "pañolero": {
        "titulo": "Pañolero Industrial",
        "experiencia_campo": "experiencia_pañol_depositos_confirmada",
        "descripcion_experiencia": "trabajo previo con tareas de pañol industrial, depósitos",
        "exclusiones": "ninguna",
        "rango_edad": "25-50",
        "conocimientos_relevantes": "PLC, electricidad industrial, neumática, electrónica, hidráulica",
        "industrias_relevantes": "fábricas industriales y rubros afines alimenticio",
    },
    "personalizado": {
        "titulo": "",
        "experiencia_campo": "experiencia_confirmada",
        "descripcion_experiencia": "",
        "exclusiones": "",
        "rango_edad": "25-45",
        "conocimientos_relevantes": "",
        "industrias_relevantes": "",
    },
}


# Criterios de score por defecto (mantenido para backward compat)
DEFAULT_SCORE_CRITERIA = """🎯 Criterios para el score (1-10):

Educación relevante (hasta 2 puntos):
• +1 si culminó el secundario
• +1 si el secundario es técnico

Experiencia (hasta 4 puntos):
• +1 si tiene más de 2 años
• +1 si tiene más de 3 años
• +1 si trabajó en fábricas industriales y rubros afines
• +1 si tuvo responsabilidades específicas o lideró tareas

Claridad y presentación del CV (hasta 1 punto):
• 1 punto si está bien organizado, con fechas y descripciones claras

Conocimientos técnicos (hasta 2 puntos):
• Presencia de conocimientos relevantes para la posición

Ubicación geográfica (hasta 1 punto):
• +1 si reside en la zona objetivo o radio cercano

Penalizaciones:
• -2 puntos si el candidato tiene 2 o más oficios NO relacionados a electricidad (ej: plomero, durlero, gasista, etc.)"""


class PromptConfig:
    """Configuración de prompts para análisis de CVs."""

    def __init__(
        self,
        especialidad: str = "personalizado",
        localidad: str = "",
        radio_km: int = 10,
        criterios_score: Optional[str] = None,
        campos_adicionales: Optional[Dict[str, Any]] = None,
        profile=None,
    ):
        """
        Inicializa configuración de prompts.

        Args:
            especialidad: Tipo de especialidad (legacy, ignorado si se pasa profile)
            localidad: Localidad de la posición a cubrir
            radio_km: Radio en kilómetros desde la localidad
            criterios_score: Criterios personalizados para el score (ignorado si se pasa profile)
            campos_adicionales: Campos adicionales personalizados (legacy)
            profile: RecruiterProfile que reemplaza especialidad + criterios
        """
        self.localidad = localidad
        self.radio_km = radio_km
        self.profile = profile

        if profile is not None:
            # Usar el perfil como fuente de verdad
            self.especialidad = profile.id
            self.criterios_score = profile.scoring_criteria or DEFAULT_SCORE_CRITERIA
            self.template = {
                "titulo": profile.position.titulo,
                "experiencia_campo": profile.position.experiencia_campo,
                "descripcion_experiencia": profile.position.descripcion_experiencia,
                "exclusiones": profile.position.exclusiones,
                "rango_edad": profile.position.rango_edad,
                "conocimientos_relevantes": profile.position.conocimientos_relevantes,
                "industrias_relevantes": profile.position.industrias_relevantes,
            }
            self.campos_adicionales = {}
        else:
            # Legacy: usar especialidad string
            self.especialidad = especialidad
            self.criterios_score = criterios_score or DEFAULT_SCORE_CRITERIA
            self.campos_adicionales = campos_adicionales or {}
            self.template = ESPECIALIDAD_TEMPLATES.get(
                especialidad, ESPECIALIDAD_TEMPLATES["personalizado"]
            ).copy()
            if especialidad == "personalizado" and campos_adicionales:
                self.template.update(campos_adicionales)

    def get_system_prompt(self) -> str:
        """Genera el system prompt configurado."""
        base = """Sos un analista de recursos humanos especializado en perfiles técnicos.
Tu tarea es analizar el contenido de UN SOLO CV y devolver un JSON con información estructurada del candidato.

IMPORTANTE:
- Debes responder EXCLUSIVAMENTE con JSON válido
- No incluyas explicaciones, comentarios ni texto adicional
- El JSON debe cumplir exactamente con el esquema proporcionado
- Si un campo no puede deducirse con alta confianza, usa null, false o lista vacía []
- Para campos numéricos, usa números (no strings)
- Para campos booleanos, usa true o false (no strings)
- Para campos categorical, usa exactamente uno de los valores permitidos
- Sé preciso y conservador: mejor null/false que inventar información
- Si un campo no se menciona explícitamente, asumí que es falso o null"""

        # Para perfiles IT con tech stack, agregar instrucción específica
        if self.profile and self.profile.tech_stack:
            required = ", ".join(self.profile.tech_stack.required)
            preferred = ", ".join(self.profile.tech_stack.preferred)
            base += f"""

EVALUACIÓN DE STACK TECNOLÓGICO:
Tecnologías requeridas para esta posición: {required}
Tecnologías deseables: {preferred}
- Para 'stack_tecnologico': listá TODAS las tecnologías, lenguajes y frameworks mencionados en el CV
- Para 'match_tech_stack': calculá el porcentaje de tecnologías REQUERIDAS ({required}) que el candidato domina (0-100)"""

        return base

    def get_user_prompt_header(self, schema: Dict[str, Any]) -> str:
        """Genera el encabezado del user prompt con el contexto de la posición."""
        titulo = self.template.get("titulo", "Perfil Técnico")

        header = f"""Vas a analizar un CV para una posición de: {titulo}"""

        if self.localidad:
            header += f"\nUbicación de la posición: {self.localidad}, Argentina"
            header += f"\nRadio aceptable: {self.radio_km} km"

        return header

    def get_field_definitions(self) -> str:
        """Genera las definiciones de campos específicos de la especialidad/perfil."""
        experiencia_campo = self.template.get(
            "experiencia_campo", "experiencia_confirmada"
        )
        descripcion_exp = self.template.get("descripcion_experiencia", "")
        exclusiones = self.template.get("exclusiones", "")
        rango_edad = self.template.get("rango_edad", "25-45")

        definitions = f"""
Definiciones para campos específicos:

• primaria_completa: true si se menciona finalización de estudios primarios
• secundaria_completa: true si terminó la secundaria (aclarar si es escuela técnica)
• terciario_completo: true si cursó y finalizó una tecnicatura relacionada
• {experiencia_campo}: true si se menciona {descripcion_exp} y se puede corroborar con fechas o descripciones"""

        if exclusiones:
            definitions += f"\n  False si menciona {exclusiones}"

        edad_parts = rango_edad.split("-")
        if len(edad_parts) == 2:
            definitions += f"\n• edad_en_rango: true si edad está entre {edad_parts[0]} y {edad_parts[1]} años, false en otro caso"

        definitions += f"\n• lugar_residencia_proximo: true si reside en un radio menor o igual a {self.radio_km}km de {self.localidad}"

        return definitions

    def get_score_instructions(self) -> str:
        """Genera las instrucciones para calcular el score."""
        return f"""
score_general: Número del 1 al 10 según los siguientes criterios:

{self.criterios_score}

IMPORTANTE: Evalúa cuidadosamente cada criterio y asigna puntos justificados."""

    def format_schema_for_prompt(self, schema: Dict[str, Any]) -> str:
        """Formatea el esquema para incluirlo en el prompt."""
        lines = ["Esquema JSON requerido:\n{"]

        for var in schema["variables"]:
            name = var["name"]
            var_type = var["type"]
            required = var.get("required", False)

            desc_parts = [f'  "{name}": ']

            if var_type == "string":
                desc_parts.append('"string"')
            elif var_type == "boolean":
                desc_parts.append("true o false")
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

    def build_full_prompt(
        self, cv_text: str, schema: Dict[str, Any]
    ) -> tuple[str, str]:
        """Construye el prompt completo para análisis de CV."""
        system_prompt = self.get_system_prompt()

        # Construir user prompt
        user_prompt_parts = [
            self.get_user_prompt_header(schema),
            "",
            self.format_schema_for_prompt(schema),
            "",
            self.get_field_definitions(),
            "",
            self.get_score_instructions(),
            "",
            "Instrucciones adicionales:",
            "• Para 'edad': extrae la edad en años si se menciona explícitamente",
            "• Para 'localidad_residencia': extrae la localidad/ciudad donde reside (ej: 'Lanús, Buenos Aires')",
            "• Para 'años_experiencia': suma todos los años de experiencia laboral relevante",
            "• Para 'nivel_educativo_alcanzado': elige el nivel MÁS ALTO alcanzado",
            "• Para 'stack_tecnológico': lista todas las tecnologías, lenguajes y frameworks mencionados",
            "• Para 'idiomas': extrae idioma y nivel (si se menciona)",
            "• Para 'emails' y 'teléfonos': extrae exactamente como aparecen",
            "• Para 'observaciones': escribe un resumen del perfil en MÁXIMO 3 oraciones destacando:",
            "  - Aspectos relevantes NO capturados en otros campos",
            "  - Soft skills o habilidades interpersonales mencionadas",
            "  - Proyectos especiales, logros o certificaciones adicionales",
            "  - Cualquier información diferenciadora del candidato",
            "• Si no encuentras información para un campo, usa null, false o [] (no inventes)",
            "",
            "Texto del CV a analizar:",
            "---",
            cv_text[:10000],
            "---",
            "",
            "Responde SOLO con el JSON, sin explicaciones adicionales.",
        ]

        user_prompt = "\n".join(user_prompt_parts)

        return system_prompt, user_prompt


def create_default_config() -> PromptConfig:
    """Crea una configuración por defecto."""
    return PromptConfig(
        especialidad="personalizado",
        localidad="Buenos Aires",
        radio_km=10,
        criterios_score=DEFAULT_SCORE_CRITERIA,
    )


def get_especialidades_disponibles() -> list[str]:
    """Retorna lista de especialidades predefinidas disponibles (legacy)."""
    return [k for k in ESPECIALIDAD_TEMPLATES.keys() if k != "personalizado"]
