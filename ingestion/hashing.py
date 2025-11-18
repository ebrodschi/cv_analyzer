"""
Cálculo de hash SHA1 para archivos.
"""

import hashlib
import io
from typing import Union


def compute_hash(content: Union[bytes, io.BytesIO], algorithm: str = "sha1") -> str:
    """
    Calcula hash de un archivo.

    Args:
        content: Contenido del archivo (bytes o BytesIO)
        algorithm: Algoritmo de hash ('sha1', 'md5', 'sha256')

    Returns:
        Hash hexadecimal del archivo
    """
    # Convertir a bytes si es necesario
    if isinstance(content, io.BytesIO):
        data = content.getvalue()
    else:
        data = content

    # Calcular hash
    if algorithm == "sha1":
        return hashlib.sha1(data).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    else:
        raise ValueError(f"Algoritmo no soportado: {algorithm}")


def compute_hash_from_file(file_path: str, algorithm: str = "sha1") -> str:
    """
    Calcula hash de un archivo desde su ruta.

    Args:
        file_path: Ruta al archivo
        algorithm: Algoritmo de hash

    Returns:
        Hash hexadecimal
    """
    with open(file_path, "rb") as f:
        return compute_hash(f.read(), algorithm)
