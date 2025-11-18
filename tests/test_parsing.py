"""
Tests para el módulo de parsing.
"""

import io

import pytest

from parsing.docx import parse_docx
from parsing.pdf import parse_pdf
from utils.text_clean import normalize_text


def test_normalize_text():
    """Test de normalización de texto."""
    raw_text = """


    Header Repetitivo

    Nombre:    Juan   Pérez
    Experiencia:
    • Desarrollador     Python
    • Data Scientist


    Header Repetitivo

    Educación:
    Universidad Nacional - 2020

    Header Repetitivo

    """

    normalized = normalize_text(raw_text)

    # Debe remover espacios múltiples
    assert "    " not in normalized

    # Debe preservar bullets
    assert "•" in normalized

    # No debe tener más de 2 saltos de línea seguidos
    assert "\n\n\n" not in normalized


def test_normalize_empty_text():
    """Test con texto vacío."""
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""


def test_normalize_preserves_structure():
    """Test que preserva estructura importante."""
    text = """
    Experiencia Laboral:
    • Python Developer
    • Data Analyst

    Educación:
    Universidad de Buenos Aires
    """

    normalized = normalize_text(text)

    # Debe preservar bullets
    assert "Python Developer" in normalized
    assert "•" in normalized

    # Debe preservar secciones
    assert "Experiencia" in normalized
    assert "Educación" in normalized


def test_parse_pdf_with_invalid_data():
    """Test de parsing PDF con datos inválidos."""
    invalid_data = b"Not a PDF file"

    with pytest.raises(ValueError):
        parse_pdf(invalid_data)


def test_parse_docx_with_invalid_data():
    """Test de parsing DOCX con datos inválidos."""
    invalid_data = b"Not a DOCX file"

    with pytest.raises(ValueError):
        parse_docx(invalid_data)


# Nota: Los tests reales de PDF y DOCX requieren archivos de ejemplo
# En producción, agregar tests con archivos dummy en tests/samples/


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
