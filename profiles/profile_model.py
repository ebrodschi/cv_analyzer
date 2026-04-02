"""
Modelo de datos para perfiles de reclutamiento.
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PositionConfig:
    """Configuración de la posición a buscar."""

    titulo: str = ""
    experiencia_campo: str = "experiencia_confirmada"
    descripcion_experiencia: str = ""
    exclusiones: str = ""
    rango_edad: str = "25-45"
    conocimientos_relevantes: str = ""
    industrias_relevantes: str = ""


@dataclass
class TechStackConfig:
    """Configuración de stack tecnológico (para perfiles IT)."""

    required: List[str] = field(default_factory=list)
    preferred: List[str] = field(default_factory=list)


@dataclass
class ExtraField:
    """Campo adicional de extracción."""

    name: str
    type: str
    required: bool = False
    description: str = ""
    min: Optional[int] = None
    max: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    properties: Optional[Dict[str, str]] = None

    def to_schema_dict(self) -> Dict[str, Any]:
        """Convierte a formato compatible con YAML schema."""
        d: Dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "required": self.required,
        }
        if self.description:
            d["description"] = self.description
        if self.min is not None:
            d["min"] = self.min
        if self.max is not None:
            d["max"] = self.max
        if self.allowed_values:
            d["allowed_values"] = self.allowed_values
        if self.properties:
            d["properties"] = self.properties
        return d


@dataclass
class RecruiterProfile:
    """Perfil de reclutamiento que agrupa toda la configuración para analizar CVs."""

    id: str
    name: str
    category: str  # "industrial" | "it" | "kiosko" | "general"
    position: PositionConfig = field(default_factory=PositionConfig)
    tech_stack: Optional[TechStackConfig] = None
    extra_fields: List[ExtraField] = field(default_factory=list)
    scoring_criteria: str = ""
    preaprobado_conditions: List[str] = field(default_factory=list)
    is_preset: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el perfil a diccionario."""
        d = asdict(self)
        if self.tech_stack is None:
            d["tech_stack"] = None
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecruiterProfile":
        """Crea un perfil desde un diccionario."""
        position_data = data.get("position", {})
        position = PositionConfig(**position_data) if position_data else PositionConfig()

        tech_stack = None
        if data.get("tech_stack"):
            tech_stack = TechStackConfig(**data["tech_stack"])

        extra_fields = []
        for ef in data.get("extra_fields", []):
            extra_fields.append(ExtraField(**ef))

        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            position=position,
            tech_stack=tech_stack,
            extra_fields=extra_fields,
            scoring_criteria=data.get("scoring_criteria", ""),
            preaprobado_conditions=data.get("preaprobado_conditions", []),
            is_preset=data.get("is_preset", False),
        )

    def to_json(self) -> str:
        """Serializa a JSON para descarga."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "RecruiterProfile":
        """Crea desde JSON subido por el usuario."""
        return cls.from_dict(json.loads(json_str))

    def clone(self, new_id: str, new_name: str) -> "RecruiterProfile":
        """Crea una copia del perfil con nuevo id y nombre."""
        data = self.to_dict()
        data["id"] = new_id
        data["name"] = new_name
        data["is_preset"] = False
        return RecruiterProfile.from_dict(data)
