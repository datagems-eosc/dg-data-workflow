from dataclasses import dataclass, fields
from typing import Dict, Any, List, Optional

from common.extensions.utils import normalize_keys


@dataclass
class FieldSourceExtract:
    column: str


@dataclass
class FieldSource:
    fileObject: Dict[str, str]
    extract: FieldSourceExtract


@dataclass
class Field:
    type: str
    id: str
    name: str
    description: str
    dataType: str
    source: FieldSource
    sample: List[Any]


@dataclass
class RecordSet:
    type: str
    id: str
    name: str
    description: str
    field: List[Field]


@dataclass
class DistributionItem:
    type: str
    id: str
    name: str
    description: str
    contentSize: str
    contentUrl: str
    encodingFormat: str
    includes: Optional[str] = None
    sha256: Optional[str] = None


@dataclass
class DatasetResponse:
    context: Dict[str, Any]
    type: str
    id: str
    name: str
    description: str
    conformsTo: str
    citeAs: str
    license: str
    url: str
    doi: str
    version: str
    headline: str
    keywords: List[str]
    fieldOfScience: List[str]
    inLanguage: List[str]
    country: str
    datePublished: str
    access: str
    uploadedBy: str
    distribution: List[DistributionItem]
    recordSet: List[RecordSet]

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        d = normalize_keys(data)
        allowed = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in allowed}
        return cls(**filtered)
