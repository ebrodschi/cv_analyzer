"""
Parser de archivos usando Docling con soporte OCR.
Puede detectar imágenes y fotos en los CVs.
"""

import io
import os
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Union

# Note: DOCLING_SKIP_RAPIDOCR is set in app.py before imports


def parse_with_docling(
    file_content: Union[bytes, io.BytesIO], mime_type: str
) -> Dict[str, any]:
    """
    Parsea un archivo usando Docling con capacidades OCR.
    Detecta si el documento tiene foto/imagen.

    Args:
        file_content: Contenido del archivo en bytes o BytesIO
        mime_type: Tipo MIME del archivo (application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, etc.)

    Returns:
        Diccionario con:
        - text: Texto extraído
        - has_photo: Boolean indicando si se detectó una foto
        - images_count: Número de imágenes detectadas
        - metadata: Metadatos adicionales

    Raises:
        ValueError: Si no se puede parsear el archivo
    """
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import DocumentConverter

        print("🔍 [DEBUG OCR] Iniciando parse_with_docling")
        print(f"   - MIME type: {mime_type}")

        # Asegurar que tenemos bytes
        if isinstance(file_content, io.BytesIO):
            pdf_bytes = file_content.getvalue()
        else:
            pdf_bytes = file_content

        print(f"   - Tamaño del archivo: {len(pdf_bytes)} bytes")

        # Determinar extensión según mime type
        if "pdf" in mime_type.lower():
            suffix = ".pdf"
            input_format = InputFormat.PDF
        elif "word" in mime_type.lower() or "docx" in mime_type.lower():
            suffix = ".docx"
            input_format = InputFormat.DOCX
        else:
            raise ValueError(f"Formato no soportado para OCR: {mime_type}")

        print(f"   - Formato detectado: {suffix} ({input_format})")

        # Docling requiere un archivo en disco, así que creamos uno temporal
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = Path(temp_file.name)

        print(f"   - Archivo temporal creado: {temp_path}")

        try:
            # Crear converter con configuración para usar Tesseract OCR
            print("   - Creando DocumentConverter con OCR habilitado...")

            # Intentar configurar OCR options para forzar tesseract en ambientes con permisos restringidos
            try:
                from docling.datamodel.pipeline_options import (
                    OcrOptions,
                    PdfPipelineOptions,
                )

                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = True

                # Forzar uso de tesseract en lugar de auto-detection
                pipeline_options.ocr_options = OcrOptions(
                    kind="tesseract",  # Forzar tesseract explícitamente
                    force_full_page_ocr=False,
                    use_pdf_images=True,
                )

                converter = DocumentConverter(
                    format_options={InputFormat.PDF: pipeline_options}
                )
                print("   ✓ Configurado para usar Tesseract OCR")
            except Exception as config_error:
                # Fallback a configuración por defecto si falla la config explícita
                print(f"   ⚠️ Usando config por defecto: {config_error}")
                converter = DocumentConverter()

            # Convertir documento
            print("   - Convirtiendo documento con Docling...")
            result = converter.convert(temp_path)
            print("   ✅ Conversión exitosa")

            # Extraer texto
            text = result.document.export_to_markdown()
            print(f"   - Texto extraído: {len(text)} caracteres")

            # Detectar imágenes/fotos
            has_photo = False
            images_count = 0
            candidate_photos = []  # Imágenes que parecen fotos de CV

            # Parámetros para detectar fotos de CV
            MIN_WIDTH = 50  # píxeles (reducido para capturar fotos pequeñas)
            MIN_HEIGHT = 50  # píxeles
            MAX_ASPECT_RATIO = (
                2.5  # relación alto/ancho máxima (permite fotos más verticales)
            )
            MIN_ASPECT_RATIO = (
                0.4  # relación alto/ancho mínima (permite fotos más horizontales)
            )

            # Docling detecta imágenes en el documento
            if hasattr(result.document, "pictures") and result.document.pictures:
                print(
                    f"   - Total pictures en documento: {len(result.document.pictures)}"
                )
                for idx, picture in enumerate(result.document.pictures):
                    # Intentar obtener dimensiones del bounding box en prov
                    width = None
                    height = None

                    # Docling guarda las dimensiones en prov[0].bbox
                    if hasattr(picture, "prov") and len(picture.prov) > 0:
                        prov_item = picture.prov[0]
                        if hasattr(prov_item, "bbox"):
                            bbox = prov_item.bbox
                            # BoundingBox tiene atributos l, r, t, b
                            if (
                                hasattr(bbox, "l")
                                and hasattr(bbox, "r")
                                and hasattr(bbox, "t")
                                and hasattr(bbox, "b")
                            ):
                                width = abs(bbox.r - bbox.l)
                                height = abs(bbox.t - bbox.b)

                    print(f"   - Picture {idx}: {width}x{height} px")

                    # Si tenemos dimensiones válidas y mayores a 0, validar si parece foto de CV
                    if width and height:
                        aspect_ratio = height / width

                        # Foto de CV típica: cuadrada o vertical, tamaño mínimo
                        is_cv_photo = (
                            width >= MIN_WIDTH
                            and height >= MIN_HEIGHT
                            and MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO
                        )

                        if is_cv_photo:
                            candidate_photos.append(
                                {
                                    "width": width,
                                    "height": height,
                                    "aspect_ratio": aspect_ratio,
                                    "type": "picture",
                                }
                            )
                            print(
                                f"     ✓ Posible foto de CV (ratio: {aspect_ratio:.2f})"
                            )
                        else:
                            print(
                                f"     ✗ No parece foto CV (ratio: {aspect_ratio:.2f}, muy ancha/alta o pequeña)"
                            )
                    else:
                        # Si no tenemos dimensiones, asumir que es foto potencial
                        print(
                            f"     ⚠️ No se pudieron obtener dimensiones, asumiendo foto de CV"
                        )
                        candidate_photos.append(
                            {
                                "width": 0,
                                "height": 0,
                                "aspect_ratio": 1.0,
                                "type": "picture_no_dims",
                            }
                        )

            # También verificar en las páginas
            if hasattr(result.document, "pages"):
                for page_num, page in enumerate(result.document.pages):
                    if hasattr(page, "images") and page.images:
                        for idx, image in enumerate(page.images):
                            width = getattr(image, "width", 0) or getattr(image, "w", 0)
                            height = getattr(image, "height", 0) or getattr(
                                image, "h", 0
                            )

                            print(
                                f"   - Imagen página {page_num}, img {idx}: {width}x{height} px"
                            )

                            if width > 0 and height > 0:
                                aspect_ratio = height / width

                                is_cv_photo = (
                                    width >= MIN_WIDTH
                                    and height >= MIN_HEIGHT
                                    and MIN_ASPECT_RATIO
                                    <= aspect_ratio
                                    <= MAX_ASPECT_RATIO
                                )

                                if is_cv_photo:
                                    candidate_photos.append(
                                        {
                                            "width": width,
                                            "height": height,
                                            "aspect_ratio": aspect_ratio,
                                            "type": "page_image",
                                            "page": page_num,
                                        }
                                    )
                                    print(
                                        f"     ✓ Posible foto de CV (ratio: {aspect_ratio:.2f})"
                                    )
                                else:
                                    print(
                                        f"     ✗ No parece foto CV (ratio: {aspect_ratio:.2f})"
                                    )
                            else:
                                images_count += 1

            # Determinar si tiene foto basado en imágenes candidatas
            has_photo = len(candidate_photos) > 0
            images_count = len(candidate_photos)

            if has_photo:
                print(
                    f"   📷 Detección de fotos: {has_photo} ({images_count} fotos detectadas)"
                )
                for i, photo in enumerate(candidate_photos):
                    print(
                        f"      Foto {i+1}: {photo['width']}x{photo['height']}px (ratio: {photo['aspect_ratio']:.2f})"
                    )
            else:
                print(f"   📷 Detección de fotos: No se detectaron fotos de CV")

            # Metadatos
            metadata = {
                "pages": (
                    len(result.document.pages)
                    if hasattr(result.document, "pages")
                    else 0
                ),
                "tables_count": (
                    len(result.document.tables)
                    if hasattr(result.document, "tables")
                    else 0
                ),
            }

            print(f"   📊 Metadatos: {metadata}")

            return {
                "text": text,
                "has_photo": has_photo,
                "images_count": images_count,
                "metadata": metadata,
            }

        finally:
            # Limpiar archivo temporal
            try:
                temp_path.unlink()
                print(f"   - Archivo temporal eliminado: {temp_path}")
            except Exception as cleanup_error:
                print(f"   ⚠️ Error limpiando archivo temporal: {cleanup_error}")

    except ImportError as e:
        print(f"❌ [DEBUG OCR] ImportError: {e}")
        raise ImportError(
            "Docling no está instalado. Instálalo con: pip install docling\n"
            f"Error: {str(e)}"
        )
    except Exception as e:
        print(f"❌ [DEBUG OCR] Error: {type(e).__name__}: {e}")
        print("   Traceback completo:")
        traceback.print_exc()
        raise ValueError(f"Error parseando con Docling (OCR): {str(e)}")
