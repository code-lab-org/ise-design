from fastapi_utils.api_model import APIModel
from pydantic import Field
from typing import List

class DesignStructureMatrix(APIModel):
    version: str = Field(
        ...,
        description="Version number."
    )
    matrix: List[List[bool]] = Field(
        ...,
        description="Binary connectivity matrix."
    )
    labels: List[str] = Field(
        ...,
        description="List of column/row labels."
    )
    order: List[int] = Field(
        ...,
        description="List of column/row order indices."
    )
