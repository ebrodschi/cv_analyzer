"""Módulo de parsing de archivos PDF y DOCX."""

from .docx import parse_docx
from .pdf import parse_pdf

__all__ = ["parse_pdf", "parse_docx"]
