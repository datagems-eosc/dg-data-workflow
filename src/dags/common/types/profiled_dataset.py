from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field as PyField


class LDModel(BaseModel):
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True
    }


@dataclass
class FieldSourceExtract(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # optional, but useful for JSON-LD
    }
    column: Optional[str] = None


@dataclass
class FieldSource(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # optional, but useful for JSON-LD
    }
    fileObject: Optional[Dict[str, str]] = None
    extract: Optional[FieldSourceExtract] = None


@dataclass
class Field(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # optional, but useful for JSON-LD
    }
    type: str = PyField(None, alias="@type")
    id: str = PyField(None, alias="id")
    dataType: Optional[str] = None
    source: Optional[FieldSource] = None
    sample: Optional[List[Any]] = None


@dataclass
class RecordSet(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # optional, but useful for JSON-LD
    }
    type: str = PyField(None, alias="@type")
    id: str = PyField(None, alias="id")
    field: Optional[List[Field]] = None


@dataclass
class DistributionItem(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # optional, but useful for JSON-LD
    }
    type: str = PyField(None, alias="@type")
    id: str = PyField(None, alias="id")


@dataclass
class DatasetResponse(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"  # optional, but useful for JSON-LD
    }
    context: Dict[str, Any] = PyField(None, alias="@context")
    type: str = PyField(None, alias="@type")
    id: str = PyField(None, alias="id")
    distribution: Optional[List[DistributionItem]] = None
    recordSet: Optional[List[RecordSet]] = None
