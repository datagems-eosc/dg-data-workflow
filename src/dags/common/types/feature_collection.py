from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


class LDModel(BaseModel):
    model_config = {"populate_by_name": True, "validate_assignment": True, "arbitrary_types_allowed": True}


@dataclass
class Geometry(LDModel):
    model_config = {"populate_by_name": True, "extra": "allow"}
    type: str
    coordinates: list[float | int]


@dataclass
class Properties(LDModel):
    model_config = {"populate_by_name": True, "extra": "allow"}
    fid: int
    station_file: str
    station_name_gr: str
    station_name_en: str
    ts: int
    date: datetime
    temp_out: float | None
    hi_temp: float | None
    low_temp: float | None
    out_hum: float | None
    bar: float | None
    rain: float | None
    wind_speed: float | None
    wind_dir: float | None
    wind_dir_str: str | None
    hi_speed: float | None
    hi_dir: float | int | None
    hi_dir_str: str | None


@dataclass
class Feature(LDModel):
    model_config = {"populate_by_name": True, "extra": "allow"}
    type: str
    geometry: Geometry
    properties: Properties


@dataclass
class FeatureCollection(LDModel):
    model_config = {"populate_by_name": True, "extra": "allow"}
    type: str
    features: list[Feature]
