import numpy as np

from ..schemas.design import Design
from ..schemas.requirements import (
    RequirementsAnalysis,
    ValidBricksRequirement,
    FullyConnectedRequirement,
    SteeringWheelRequirement,
    SeatRequirement,
    WheelRequirement,
    HeadlightRequirement,
    TaillightRequirement,
    LicensePlateRequirement
)

__version__ = "2.0.0"

def get_requirements_analysis(design: Design):
    """
    Get the requirements analysis for a design.

    Args:
        design (`:obj:Design`): the design to analyze.

    Returns:
        `:obj:RequirementsAnalysis`: the requirements analysis.
    """
    return RequirementsAnalysis(
        version=__version__,
        is_only_valid_bricks=ValidBricksRequirement(
            value=is_only_valid_bricks(design),
            invalid_bricks=get_invalid_bricks(design)
        ),
        is_fully_connected=FullyConnectedRequirement(
            value=is_fully_connected(design),
            count=count_components(design)
        ),
        is_one_steering_wheel=SteeringWheelRequirement(
            value=is_one_steering_wheel(design),
            count=count_steering_wheels(design)
        ),
        is_min_one_seat_aligned=SeatRequirement(
            value=is_min_one_seat_aligned(design),
            count=count_seats(design),
            alignment=is_seat_aligned(design)
        ),
        is_min_four_wheels_aligned_on_bottom=WheelRequirement(
            value=is_min_four_wheels_aligned_on_bottom(design),
            count=count_wheels(design),
            alignment=is_wheel_aligned(design),
            positioning=is_wheel_on_bottom(design)
        ),
        is_min_two_headlights_aligned_on_front=HeadlightRequirement(
            value=is_min_two_headlights_aligned_on_front(design),
            count=count_headlights(design),
            alignment=is_headlight_aligned(design),
            positioning=is_headlight_on_front(design)
        ),
        is_min_two_taillights_aligned_on_back=TaillightRequirement(
            value=is_min_two_taillights_aligned_on_back(design),
            count=count_taillights(design),
            alignment=is_taillight_aligned(design),
            positioning=is_taillight_on_back(design)
        ),
        is_one_license_plate_aligned_on_back=LicensePlateRequirement(
            value=is_one_license_plate_aligned_on_back(design),
            count=count_license_plates(design),
            alignment=is_license_plate_aligned(design),
            positioning=is_license_plate_on_back(design)
        ),
        is_valid=is_valid(design)
    )

def is_only_valid_bricks(design: Design):
    return len(get_invalid_bricks(design)) == 0

def get_invalid_bricks(design: Design):
    return [brick.bl_id for brick in design.get_invalid_bricks()]

def is_fully_connected(design: Design):
    return count_components(design) == 1

def count_components(design: Design):
    return design.get_num_components()

def count_seats(design: Design):
    return sum(
            1 for brick in design.bricks
            if brick.bl_id == "4079b"
        )

def is_seat_aligned(design: Design):
    return [
            brick.is_aligned(design)
            for brick in design.bricks
            if brick.bl_id == "4079b"
        ]

def is_min_one_seat_aligned(design: Design):
    return bool(
            sum(
                is_seat_aligned(design)
            ) >= 1
        )

def count_cargo_holds(design: Design):
    return sum(
            brick.bl_id == "4345"
            for brick in design.bricks
        )

def count_steering_wheels(design: Design):
    return sum(
            brick.bl_id == "3829c01"
            for brick in design.bricks
        )

def is_one_steering_wheel(design: Design):
    return count_steering_wheels(design) == 1

def count_wheels(design: Design):
    return sum(
            brick.bl_id == "30027bc01"
            for brick in design.bricks
        )

def is_wheel_aligned(design: Design):
    return [
            brick.is_aligned(design)
            for brick in design.bricks
            if brick.bl_id == "30027bc01"
        ]

def is_wheel_on_bottom(design: Design):
    return [
            bool(design.is_close_to_axis(
                brick,
                np.negative(design.get_top_axis())
            ))
            for brick in design.bricks
            if brick.bl_id == "30027bc01"
        ]

def is_min_four_wheels_aligned_on_bottom(design: Design):
    return bool(
            sum(
                np.logical_and(
                    is_wheel_aligned(design),
                    is_wheel_on_bottom(design)
                )
            ) >= 4
        )

def count_headlights(design: Design):
    return sum(
            (brick.bl_id == "54200" or brick.bl_id == "98138") and brick.bl_color == 12
            for brick in design.bricks
        )

def is_headlight_aligned(design: Design):
    return [
            brick.is_aligned(design)
            for brick in design.bricks
            if (brick.bl_id == "54200" or brick.bl_id == "98138") and brick.bl_color == 12
        ]

def is_headlight_on_front(design: Design):
    return [
            bool(design.is_close_to_axis(
                brick,
                design.get_forward_axis()
            ))
            for brick in design.bricks
            if (brick.bl_id == "54200" or brick.bl_id == "98138") and brick.bl_color == 12
        ]

def is_min_two_headlights_aligned_on_front(design: Design):
    return bool(
            sum(
                np.logical_and(
                    is_headlight_aligned(design),
                    is_headlight_on_front(design)
                )
            ) >= 2
        )

def count_taillights(design: Design):
    return sum(
            (brick.bl_id == "54200" or brick.bl_id == "98138") and brick.bl_color == 17
            for brick in design.bricks
        )

def is_taillight_aligned(design: Design):
    return [
            brick.is_aligned(design)
            for brick in design.bricks
            if (brick.bl_id == "54200" or brick.bl_id == "98138") and brick.bl_color == 17
        ]

def is_taillight_on_back(design: Design):
    return [
            bool(design.is_close_to_axis(
                brick,
                np.negative(design.get_forward_axis())
            ))
            for brick in design.bricks
            if (brick.bl_id == "54200" or brick.bl_id == "98138") and brick.bl_color == 17
        ]

def is_min_two_taillights_aligned_on_back(design: Design):
    return bool(
            sum(
                np.logical_and(
                    is_taillight_aligned(design),
                    is_taillight_on_back(design)
                )
            ) >= 2
        )

def count_license_plates(design: Design):
    return sum(
            (brick.bl_id == "3069b") and brick.bl_color == 3
            for brick in design.bricks
        )

def is_license_plate_aligned(design: Design):
    return [
            brick.is_aligned(design)
            for brick in design.bricks
            if (brick.bl_id == "3069b") and brick.bl_color == 3
        ]

def is_license_plate_on_back(design: Design):
    return [
            bool(design.is_close_to_axis(
                brick,
                np.negative(design.get_forward_axis())
            ))
            for brick in design.bricks
            if (brick.bl_id == "3069b") and brick.bl_color == 3
        ]

def is_one_license_plate_aligned_on_back(design: Design):
    return bool(
            sum(
                np.logical_and(
                    is_license_plate_aligned(design),
                    is_license_plate_on_back(design)
                )
            ) == 1
        )

def is_valid(design: Design):
    return all([
            is_only_valid_bricks(design),
            is_fully_connected(design),
            is_one_steering_wheel(design),
            is_min_one_seat_aligned(design),
            is_min_four_wheels_aligned_on_bottom(design),
            is_min_two_headlights_aligned_on_front(design),
            is_min_two_taillights_aligned_on_back(design),
            is_one_license_plate_aligned_on_back(design)
        ])
