from fastapi_utils.api_model import APIModel
from pydantic import Field
from typing import List

class ValueAnalysis(APIModel):
    version: str = Field(
        ...,
        description="Version number."
    )
    passenger: float = Field(
        ...,
        description="Passenger capacity value metric (0-100)."
    )
    cargo: float = Field(
        ...,
        description="Cargo capacity value metric (0-100)."
    )
    handling: float = Field(
        ...,
        description="Handling value metric (0-100)."
    )
    acceleration: float = Field(
        ...,
        description="Acceleration value metric (0-100)."
    )
    safety: float = Field(
        ...,
        description="Safety value metric (0-100)."
    )
    coolness: float = Field(
        ...,
        description="Coolness value metric (0-100)."
    )
    total: float = Field(
        ...,
        description="Total value metric (0-100)."
    )
    price: float = Field(
        ...,
        description="Estimated market price ($)."
    )
