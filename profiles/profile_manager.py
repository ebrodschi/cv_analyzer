"""
Gestión de perfiles: listado, CRUD en session_state, import/export JSON.
"""

from typing import Dict, List, Optional

import streamlit as st

from profiles.preset_profiles import (
    ALL_PRESETS,
    CATEGORY_LABELS,
    PRESETS_BY_CATEGORY,
    PRESETS_BY_ID,
)
from profiles.profile_model import RecruiterProfile

SESSION_KEY = "custom_profiles"


def _get_custom_profiles() -> Dict[str, RecruiterProfile]:
    """Obtiene perfiles custom del session_state."""
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = {}
    return st.session_state[SESSION_KEY]


def list_all_profiles() -> List[RecruiterProfile]:
    """Retorna todos los perfiles (presets + custom)."""
    return ALL_PRESETS + list(_get_custom_profiles().values())


def list_profiles_grouped() -> Dict[str, List[RecruiterProfile]]:
    """Retorna perfiles agrupados por categoría, incluyendo custom."""
    grouped = {cat: list(profiles) for cat, profiles in PRESETS_BY_CATEGORY.items()}
    custom = _get_custom_profiles()
    if custom:
        grouped["custom"] = list(custom.values())
    return grouped


def get_profile(profile_id: str) -> Optional[RecruiterProfile]:
    """Busca un perfil por ID (primero en custom, luego en presets)."""
    custom = _get_custom_profiles()
    if profile_id in custom:
        return custom[profile_id]
    if profile_id in PRESETS_BY_ID:
        return PRESETS_BY_ID[profile_id]
    return None


def save_custom_profile(profile: RecruiterProfile) -> None:
    """Guarda un perfil custom en session_state."""
    custom = _get_custom_profiles()
    profile.is_preset = False
    custom[profile.id] = profile


def delete_custom_profile(profile_id: str) -> bool:
    """Elimina un perfil custom. Retorna True si se eliminó."""
    custom = _get_custom_profiles()
    if profile_id in custom:
        del custom[profile_id]
        return True
    return False


def import_profile_from_json(json_str: str) -> RecruiterProfile:
    """Importa un perfil desde JSON y lo guarda en session_state.
    Si el id colisiona con un preset, le agrega sufijo '_custom'.
    """
    profile = RecruiterProfile.from_json(json_str)
    profile.is_preset = False

    # Evitar colisión con presets: el custom debe tener su propio id
    if profile.id in PRESETS_BY_ID:
        profile.id = f"{profile.id}_custom"
        profile.name = f"{profile.name} (importado)"

    save_custom_profile(profile)
    return profile


def get_category_labels() -> Dict[str, str]:
    """Retorna labels de categorías incluyendo custom si hay."""
    labels = dict(CATEGORY_LABELS)
    if _get_custom_profiles():
        labels["custom"] = "📁 Mis Perfiles"
    return labels
