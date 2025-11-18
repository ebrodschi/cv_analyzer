"""
Utilidades para normalización y limpieza de texto de CVs.
"""

import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Normaliza el texto extraído de un CV:
    - Remueve headers/footers repetitivos
    - Une líneas cortadas
    - Normaliza espacios en blanco
    - Conserva bullet points y estructura de listas

    Args:
        text: Texto crudo extraído del CV

    Returns:
        Texto normalizado
    """
    if not text:
        return ""

    # Separar en líneas
    lines = text.split("\n")

    # Remover líneas muy cortas que probablemente sean ruido (headers/footers)
    # pero conservar bullets y números
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Conservar líneas con contenido significativo o bullets
        if stripped and (
            len(stripped) > 2
            or stripped.startswith(("•", "-", "*", "·", "○"))
            or re.match(r"^\d+[\.)]\s*$", stripped)  # números de lista
        ):
            cleaned_lines.append(line)

    # Unir el texto
    text = "\n".join(cleaned_lines)

    # Detectar y remover headers/footers repetitivos
    text = _remove_repeated_patterns(text)

    # Normalizar espacios múltiples pero conservar saltos de línea significativos
    text = re.sub(r" +", " ", text)  # espacios múltiples -> uno
    text = re.sub(r"\n{3,}", "\n\n", text)  # más de 2 saltos -> 2

    # Unir líneas cortadas (heurística: si una línea termina sin puntuación y la siguiente no es bullet)
    lines = text.split("\n")
    merged_lines = []
    i = 0
    while i < len(lines):
        current = lines[i].strip()

        # Si hay línea siguiente y esta no termina en puntuación fuerte
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # No unir si la siguiente línea empieza con bullet o mayúscula después de punto
            if (
                current
                and not current[-1] in ".!?:;"
                and not next_line.startswith(("•", "-", "*", "·", "○", "▪"))
                and not re.match(r"^\d+[\.)]\s", next_line)
                and not (
                    len(next_line) > 0
                    and next_line[0].isupper()
                    and current.endswith(".")
                )
            ):
                merged_lines.append(current + " " + next_line)
                i += 2
                continue

        merged_lines.append(current)
        i += 1

    text = "\n".join(merged_lines)

    # Limpieza final
    text = text.strip()

    return text


def _remove_repeated_patterns(text: str, min_repetitions: int = 3) -> str:
    """
    Detecta y remueve patrones repetitivos (headers/footers).

    Args:
        text: Texto a limpiar
        min_repetitions: Número mínimo de repeticiones para considerar un patrón

    Returns:
        Texto sin patrones repetitivos
    """
    lines = text.split("\n")

    # Contar ocurrencias de cada línea
    line_counts = {}
    for line in lines:
        stripped = line.strip()
        if stripped:
            line_counts[stripped] = line_counts.get(stripped, 0) + 1

    # Identificar líneas repetitivas
    repeated_lines = {
        line
        for line, count in line_counts.items()
        if count >= min_repetitions and len(line) < 100  # Solo líneas cortas
    }

    # Remover líneas repetitivas
    cleaned_lines = [
        line
        for line in lines
        if line.strip() not in repeated_lines or line.strip() == ""
    ]

    return "\n".join(cleaned_lines)


def extract_sections(text: str) -> dict:
    """
    Intenta extraer secciones comunes de un CV (experiencia, educación, etc).

    Args:
        text: Texto del CV normalizado

    Returns:
        Diccionario con secciones identificadas
    """
    sections = {
        "experiencia": [],
        "educacion": [],
        "habilidades": [],
        "idiomas": [],
        "otros": [],
    }

    # Patrones de secciones comunes (español e inglés)
    patterns = {
        "experiencia": r"(?:experiencia|experience|trabajo|employment|professional)",
        "educacion": r"(?:educaci[oó]n|education|formaci[oó]n|estudios|academic)",
        "habilidades": r"(?:habilidades|skills|competencias|tecnolog[ií]as|stack)",
        "idiomas": r"(?:idiomas|languages|lenguas)",
    }

    lines = text.split("\n")
    current_section = "otros"

    for line in lines:
        line_lower = line.lower().strip()

        # Detectar inicio de sección
        section_found = False
        for section_name, pattern in patterns.items():
            if re.search(pattern, line_lower) and len(line_lower) < 50:
                current_section = section_name
                section_found = True
                break

        # Agregar línea a la sección actual (si no es el título de sección)
        if not section_found and line.strip():
            sections[current_section].append(line.strip())

    # Convertir listas a texto
    return {k: "\n".join(v) for k, v in sections.items() if v}
