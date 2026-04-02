"""
Genera esquemas YAML de extracción a partir de un RecruiterProfile.
"""

from profiles.profile_model import RecruiterProfile


def build_schema_from_profile(profile: RecruiterProfile) -> str:
    """
    Genera un esquema YAML compatible con load_yaml_schema() a partir de un perfil.

    Args:
        profile: Perfil de reclutamiento

    Returns:
        String YAML con el esquema de extracción
    """
    lines = ["version: 1", "variables:"]

    # --- Contacto (siempre) ---
    lines += [
        "  # Información de contacto",
        "  - name: nombre",
        "    type: string",
        "    required: false",
        "  - name: mail",
        "    type: string",
        "    format: email",
        "    required: false",
        "  - name: telefono",
        "    type: string",
        "    required: false",
    ]

    # --- Foto en CV (siempre) ---
    lines += [
        "",
        "  # Información del CV",
        "  - name: hay_foto_en_cv",
        "    type: boolean",
        "    required: false",
    ]

    # --- Educación según categoría ---
    lines.append("")
    lines.append("  # Educación")

    if profile.category in ("industrial", "kiosko"):
        lines += [
            "  - name: primaria_completa",
            "    type: boolean",
            "    required: true",
            "  - name: secundaria_completa",
            "    type: boolean",
            "    required: true",
            "  - name: secundaria_tecnica",
            "    type: boolean",
            "    required: false",
            "    description: Indica si el secundario cursado fue una escuela técnica",
            "  - name: titulo_secundario",
            "    type: string",
            "    required: false",
            '    description: Título obtenido en el secundario (ej. "Técnico Electromecánico", "Bachiller")',
            "  - name: terciario_completo",
            "    type: boolean",
            "    required: false",
        ]
    else:
        # IT y general: campo categorical de nivel educativo
        lines += [
            "  - name: nivel_educativo_alcanzado",
            "    type: categorical",
            "    allowed_values: [primaria, secundaria, terciario, universitario, posgrado]",
            "    required: false",
            "    description: Nivel educativo más alto alcanzado por el candidato",
        ]

    # --- Experiencia ---
    exp_campo = profile.position.experiencia_campo
    lines += [
        "",
        "  # Experiencia laboral",
        f"  - name: {exp_campo}",
        "    type: boolean",
        "    required: true",
        "  - name: años_experiencia",
        "    type: integer",
        "    min: 0",
        "    max: 50",
        "    required: false",
    ]

    # --- Tech stack (solo si el perfil lo tiene) ---
    if profile.tech_stack:
        lines += [
            "",
            "  # Stack tecnológico",
            "  - name: stack_tecnologico",
            "    type: list[string]",
            "    required: false",
            "    description: Todas las tecnologías, lenguajes y frameworks mencionados en el CV",
            "  - name: match_tech_stack",
            "    type: integer",
            "    min: 0",
            "    max: 100",
            "    required: false",
            "    description: Porcentaje de tecnologías requeridas que el candidato domina",
        ]

    # --- Ubicación y edad (siempre) ---
    lines += [
        "",
        "  # Ubicación y edad",
        "  - name: edad",
        "    type: integer",
        "    min: 18",
        "    max: 80",
        "    required: false",
        "    description: Edad del candidato en años",
        "  - name: localidad_residencia",
        "    type: string",
        "    required: false",
        "    description: Localidad o ciudad donde reside el candidato",
        "  - name: lugar_residencia_proximo",
        "    type: boolean",
        "    required: false",
        "    description: Indica si reside cerca de la ubicación objetivo",
        "  - name: edad_en_rango",
        "    type: boolean",
        "    required: false",
        "    description: Indica si la edad está en el rango deseado",
    ]

    # --- Score y observaciones (siempre) ---
    lines += [
        "",
        "  # Evaluación y comentarios",
        "  - name: score_general",
        "    type: integer",
        "    min: 1",
        "    max: 10",
        "    required: true",
        "    description: Puntaje general del candidato evaluado del 1 al 10",
        "  - name: observaciones",
        "    type: string",
        "    required: false",
        "    description: Resumen del perfil en máximo 3 oraciones",
    ]

    # --- Campos adicionales opcionales (siempre) ---
    lines += [
        "",
        "  # Campos adicionales",
        "  - name: idiomas",
        "    type: list[object]",
        "    properties:",
        "      idioma: string",
        "      nivel: string",
        "    required: false",
    ]

    # otros_oficios_tecnicos solo para industrial y general
    if profile.category in ("industrial", "general"):
        lines += [
            "  - name: otros_oficios_tecnicos",
            "    type: list[string]",
            "    required: false",
            "    description: Listado de otros conocimientos técnicos o oficios que posee el candidato",
        ]

    # --- Extra fields del perfil ---
    if profile.extra_fields:
        lines += ["", "  # Campos personalizados"]
        for ef in profile.extra_fields:
            lines.append(f"  - name: {ef.name}")
            lines.append(f"    type: {ef.type}")
            lines.append(f"    required: {'true' if ef.required else 'false'}")
            if ef.description:
                lines.append(f"    description: {ef.description}")
            if ef.min is not None:
                lines.append(f"    min: {ef.min}")
            if ef.max is not None:
                lines.append(f"    max: {ef.max}")
            if ef.allowed_values:
                vals = ", ".join(ef.allowed_values)
                lines.append(f"    allowed_values: [{vals}]")
            if ef.properties:
                lines.append("    properties:")
                for prop_name, prop_type in ef.properties.items():
                    lines.append(f"      {prop_name}: {prop_type}")

    return "\n".join(lines) + "\n"
