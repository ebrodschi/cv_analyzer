"""
Parser de archivos PDF usando pymupdf con fallback a pdfplumber.
Con soporte opcional para OCR usando docling.
"""

import io
from typing import Any, Dict, Union


def parse_pdf(
    file_content: Union[bytes, io.BytesIO], use_ocr: bool = False
) -> Union[str, Dict[str, Any]]:
    """
    Extrae texto de un archivo PDF.
    Intenta primero con pymupdf (más rápido) y si falla usa pdfplumber.

    Si use_ocr=True, usa docling con OCR para mejor detección de imágenes y texto en imágenes.

    Args:
        file_content: Contenido del archivo PDF en bytes o BytesIO
        use_ocr: Si True, usa docling con OCR para detectar fotos y extraer texto de imágenes

    Returns:
        Si use_ocr=False: Texto extraído del PDF (str)
        Si use_ocr=True: Dict con 'text', 'has_photo', 'images_count', 'metadata'

    Raises:
        ValueError: Si no se puede parsear el PDF con ningún método
    """
    # Si OCR está habilitado, usar docling
    if use_ocr:
        try:
            from parsing.ocr import parse_with_docling

            return parse_with_docling(file_content, "application/pdf")
        except ImportError:
            print("⚠️ Docling no disponible. Cayendo a método tradicional sin OCR.")
            print("   Para usar OCR, instala: pip install docling")
            # Continuar con método tradicional
        except Exception as e:
            print(f"⚠️ Error con OCR, usando método tradicional: {str(e)}")
            # Continuar con método tradicional

    # Método tradicional (sin OCR)
    # Asegurar que tenemos bytes
    if isinstance(file_content, io.BytesIO):
        pdf_bytes = file_content.getvalue()
    else:
        pdf_bytes = file_content

    # Intentar con pymupdf primero (PyMuPDF/fitz)
    try:
        text = _parse_with_pymupdf(pdf_bytes)
        if text.strip():  # Si obtuvimos contenido
            if use_ocr:
                # Retornar en formato dict para consistencia
                return {
                    "text": text,
                    "has_photo": False,  # Método tradicional no detecta fotos
                    "images_count": 0,
                    "metadata": {},
                }
            return text
    except Exception as e:
        print(f"⚠️ pymupdf falló, intentando con pdfplumber: {str(e)}")

    # Fallback a pdfplumber
    try:
        text = _parse_with_pdfplumber(pdf_bytes)
        if text.strip():
            if use_ocr:
                return {
                    "text": text,
                    "has_photo": False,
                    "images_count": 0,
                    "metadata": {},
                }
            return text
        raise ValueError("El PDF no contiene texto extraíble")
    except Exception as e:
        raise ValueError(f"Error parseando PDF con ambos métodos: {str(e)}")


def _parse_with_pymupdf(pdf_bytes: bytes) -> str:
    """
    Parsea PDF usando pymupdf (más rápido, mejor para PDFs con texto).

    Args:
        pdf_bytes: Contenido del PDF en bytes

    Returns:
        Texto extraído
    """
    import fitz  # pymupdf

    text_parts = []

    # Abrir PDF desde bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    try:
        for page_num in range(doc.page_count):
            page = doc[page_num]

            # Extraer texto de la página
            page_text = page.get_text("text")

            if page_text.strip():
                text_parts.append(page_text)

            # También intentar extraer de imágenes si no hay texto
            if not page_text.strip():
                # Intentar extraer texto de áreas de texto (para PDFs complejos)
                blocks = page.get_text("blocks")
                for block in blocks:
                    if len(block) >= 5:  # block[4] contiene el texto
                        text_parts.append(block[4])

        return "\n\n".join(text_parts)

    finally:
        doc.close()


def _parse_with_pdfplumber(pdf_bytes: bytes) -> str:
    """
    Parsea PDF usando pdfplumber (mejor para PDFs con tablas o layouts complejos).

    Args:
        pdf_bytes: Contenido del PDF en bytes

    Returns:
        Texto extraído
    """
    import pdfplumber

    text_parts = []

    # Abrir PDF desde bytes
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            # Extraer texto
            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

            # Intentar extraer tablas si hay
            tables = page.extract_tables()
            for table in tables:
                # Convertir tabla a texto
                table_text = "\n".join(
                    [
                        " | ".join([str(cell) if cell else "" for cell in row])
                        for row in table
                        if row
                    ]
                )
                if table_text.strip():
                    text_parts.append(f"\n[Tabla]\n{table_text}\n")

    return "\n\n".join(text_parts)


def get_pdf_metadata(pdf_bytes: bytes) -> dict:
    """
    Extrae metadatos del PDF (autor, título, páginas, etc).

    Args:
        pdf_bytes: Contenido del PDF en bytes

    Returns:
        Diccionario con metadatos
    """
    try:
        import fitz

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        metadata = {
            "pages": doc.page_count,
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", ""),
        }

        doc.close()
        return metadata

    except Exception:
        return {"pages": 0}
