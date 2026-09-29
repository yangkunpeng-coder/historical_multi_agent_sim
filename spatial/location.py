from enum import StrEnum

from pydantic import BaseModel, Field


class LocationKind(StrEnum):
    HOME = "home"
    FIELD = "field"
    MARKET = "market"
    COUNTY_OFFICE = "county_office"
    COURT = "court"
    EXAM_HALL = "exam_hall"
    VILLAGE = "village"


class Location(BaseModel):
    location_id: str
    name: str
    kind: LocationKind
    capacity: int = Field(default=100, ge=1)

