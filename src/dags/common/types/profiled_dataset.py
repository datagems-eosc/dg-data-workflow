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
class DistributionItem(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }
    type: str = PyField(None, alias="@type")
    id: str = PyField(None, alias="@id")


@dataclass
class DatasetResponse(LDModel):
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }
    context: Dict[str, Any] = PyField(None, alias="@context")
    type: str = PyField(None, alias="@type")
    id: str = PyField(None, alias="@id")
    distribution: Optional[List[DistributionItem]] = None
    recordSet: Optional[List[Any]] = None
