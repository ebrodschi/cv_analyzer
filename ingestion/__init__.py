"""Módulo de ingesta de archivos desde diferentes fuentes."""

from .drive import download_file, list_files_by_folder
from .hashing import compute_hash
from .local import process_uploaded_file

__all__ = [
    "list_files_by_folder",
    "download_file",
    "process_uploaded_file",
    "compute_hash",
]
