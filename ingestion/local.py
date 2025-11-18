"""
Procesamiento de archivos subidos localmente.
"""

import io
from typing import Union


def process_uploaded_file(uploaded_file) -> tuple[str, bytes, str]:
    """
    Procesa un archivo subido desde Streamlit.

    Args:
        uploaded_file: Objeto UploadedFile de Streamlit

    Returns:
        Tupla (nombre_archivo, contenido_bytes, mime_type)
    """
    filename = uploaded_file.name
    content = uploaded_file.read()
    mime_type = uploaded_file.type or _infer_mime_type(filename)

    return filename, content, mime_type


def _infer_mime_type(filename: str) -> str:
    """
    Infiere el tipo MIME desde el nombre del archivo.

    Args:
        filename: Nombre del archivo

    Returns:
        Tipo MIME
    """
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return "application/pdf"
    elif lower_name.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif lower_name.endswith(".doc"):
        return "application/msword"
    elif lower_name.endswith(".txt"):
        return "text/plain"
    else:
        return "application/octet-stream"


def get_file_extension(filename: str) -> str:
    """
    Obtiene la extensión de un archivo.

    Args:
        filename: Nombre del archivo

    Returns:
        Extensión (sin el punto)
    """
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def is_supported_file(filename: str) -> bool:
    """
    Verifica si un archivo es de tipo soportado (PDF o DOCX).

    Args:
        filename: Nombre del archivo

    Returns:
        True si es soportado
    """
    ext = get_file_extension(filename)
    return ext in ["pdf", "docx"]
