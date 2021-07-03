from fastapi_utils.api_model import APIModel
from pydantic import Field
from typing import List, Dict

class BillOfMaterialsLine(APIModel):
    name: str = Field(
        ...,
        description="Material name."
    )
    cost: float = Field(
        ...,
        description="Unit cost ($)."
    )
    quantity: int = Field(
        ...,
        description="Quantity used."
    )

class AssemblyCostAnalysis(APIModel):
    components: float = Field(
        ...,
        description="Cost of assembling individual components ($)."
    )
    integration: float = Field(
        ...,
        description="Cost of integrating components ($)."
    )
    total: float = Field(
        ...,
        description="Total assembly cost ($)."
    )

class OverheadCostAnalysis(APIModel):
    engineering: float = Field(
        ...,
        description="Cost of engineering staff ($)."
    )
    marketing: float = Field(
        ...,
        description="Cost of marketing staff ($)."
    )
    administration: float = Field(
        ...,
        description="Cost of administration staff ($)."
    )
    facilities: float = Field(
        ...,
        description="Cost of facilities ($)."
    )
    total: float = Field(
        ...,
        description="Total overhead cost ($)."
    )

class CostAnalysis(APIModel):
    version: str = Field(
        ...,
        description="Version number."
    )
    materials: float = Field(
        ...,
        description="Cost of the materials ($)."
    )
    bom: Dict[str, BillOfMaterialsLine] = Field(
        ...,
        description="Bill of materials."
    )
    assembly: AssemblyCostAnalysis = Field(
        ...,
        description="Assembly cost analysis."
    )
    overhead: OverheadCostAnalysis = Field(
        ...,
        description="Overhead cost analysis."
    )
    total: float = Field(
        ...,
        description="Total cost ($)."
    )
