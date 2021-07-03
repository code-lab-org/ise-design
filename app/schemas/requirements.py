from fastapi_utils.api_model import APIModel
from pydantic import Field
from typing import List

class ValidBricksRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if only valid bricks are used."
    )
    invalid_bricks: List[str] = Field(
        ...,
        description="List of invalid brick IDs."
    )

class FullyConnectedRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if only valid bricks are used."
    )
    count: int = Field(
        ...,
        description="Count of connected components."
    )

class SteeringWheelRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if only one steering wheel is used."
    )
    count: int = Field(
        ...,
        description="Count of steering wheels used."
    )

class SeatRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if at least one seat is correctly aligned."
    )
    count: int = Field(
        ...,
        description="Seat count."
    )
    alignment: List[bool] = Field(
        ...,
        description="List of whether seats are correctly aligned."
    )

class WheelRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if at least four wheels are correctly aligned and positioned."
    )
    count: int = Field(
        ...,
        description="Wheel count."
    )
    alignment: List[bool] = Field(
        ...,
        description="List of whether seats are correctly aligned."
    )
    positioning: List[bool] = Field(
        ...,
        description="List of whether seats are correctly positioned."
    )

class HeadlightRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if at least two headlights are correctly aligned and positioned."
    )
    count: int = Field(
        ...,
        description="Headlight count."
    )
    alignment: List[bool] = Field(
        ...,
        description="List of whether headlights are correctly aligned."
    )
    positioning: List[bool] = Field(
        ...,
        description="List of whether headlights are correctly positioned."
    )

class TaillightRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if at least two taillights are correctly aligned and positioned."
    )
    count: int = Field(
        ...,
        description="Taillight count."
    )
    alignment: List[bool] = Field(
        ...,
        description="List of whether taillights are correctly aligned."
    )
    positioning: List[bool] = Field(
        ...,
        description="List of whether taillights are correctly positioned."
    )

class LicensePlateRequirement(APIModel):
    value: bool = Field(
        ...,
        description="True, if at least one license plate is correctly aligned and positioned."
    )
    count: int = Field(
        ...,
        description="License plate count."
    )
    alignment: List[bool] = Field(
        ...,
        description="List of whether license plates are correctly aligned."
    )
    positioning: List[bool] = Field(
        ...,
        description="List of whether license plates are correctly positioned."
    )

class RequirementsAnalysis(APIModel):
    version: str = Field(
        ...,
        description="Version number"
    )
    is_only_valid_bricks: ValidBricksRequirement = Field(
        ...,
        description="Requirement that only valid bricks are used."
    )
    is_fully_connected: FullyConnectedRequirement = Field(
        ...,
        description="Requirement that all bricks are fully connected."
    )
    is_one_steering_wheel: SteeringWheelRequirement = Field(
        ...,
        description="Requirement that only one steering wheel is used."
    )
    is_min_one_seat_aligned: SeatRequirement = Field(
        ...,
        description="Requirement that at least one seat is correctly aligned."
    )
    is_min_four_wheels_aligned_on_bottom: WheelRequirement = Field(
        ...,
        description="Requirement that at least four wheels are correctly aligned and positioned."
    )
    is_min_two_headlights_aligned_on_front: HeadlightRequirement = Field(
        ...,
        description="Requirement that at least two headlights are correctly aligned and positioned."
    )
    is_min_two_taillights_aligned_on_back: TaillightRequirement = Field(
        ...,
        description="Requirement that at least two taillights are correctly aligned and positioned."
    )
    is_one_license_plate_aligned_on_back: LicensePlateRequirement = Field(
        ...,
        description="Requirement that at least one license plates is correctly aligned and positioned."
    )
    is_valid: bool = Field(
        ...,
        description="True, if all requirements are satisifed."
    )
