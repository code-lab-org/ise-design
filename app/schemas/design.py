from datetime import datetime
from fastapi_utils.api_model import APIModel
import numpy as np
from pydantic import Field
from scipy.spatial import ConvexHull
from typing import List, Optional

from .brick import Brick
from .dsm import DesignStructureMatrix
from .requirements import RequirementsAnalysis
from .cost import CostAnalysis
from .value import ValueAnalysis

class Design(APIModel):
    design_id: str = Field(
        ...,
        description="Unique identifier for this design."
    )
    name: str = Field(
        ...,
        description="Name of this design."
    )
    designer: str = Field(
        ...,
        description="Name of the designer."
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of design submission."
    )
    bricks: List[Brick] = Field(
        [],
        description="Constituent bricks in this design."
    )

    def get_convex_hull(self):
        """
        Get the convex hull about this design.

        Returns:
            `:obj:ConvexHull`: the convex hull.
        """
        if len(self.get_valid_bricks()) > 0:
            return ConvexHull(np.concatenate(tuple(
                    brick.vertices
                    for brick in self.get_valid_bricks()
                )))
        else:
            return None

    def get_forward_axis(self):
        """
        Get a unit vector pointing in the "forward" direction.

        Returns:
            `:obj:array`: a unit vector pointing in the forward direction.
        """
        # look for the first steering wheel brick (bl_id 3829c01)
        for brick in self.bricks:
            if brick.bl_id == "3829c01":
                # transform valid axis by its rotation matrix
                return np.matmul(
                        brick.rotation,
                        [0, 0, -1]
                    )
        return np.array([1,0,0])

    def get_top_axis(self):
        """
        Get a unit vector pointing in the "top" direction.

        Returns:
            `:obj:array`: a unit vector pointing in the top direction.
        """
        return np.array([0, -1, 0])

    def get_driver_side_axis(self):
        """
        Get a unit vector pointing in the "driver side" direction.

        Returns:
            `:obj:array`: a unit vector pointing in the driver side direction.
        """
        # look for the first steering wheel brick (bl_id 3829c01)
        for brick in self.bricks:
            if brick.bl_id == "3829c01":
                return np.matmul(
                        brick.rotation,
                        [1, 0, 0]
                    )
        return np.array([0,0,1])

    def get_mass(self):
        """
        Get the total mass as the sum of all valid bricks.

        Returns:
            float: the total mass (grams).
        """
        return sum(brick.mass for brick in self.get_valid_bricks())

    def get_cost(self):
        """
        Get the total cost as the sum of all valid bricks.

        Returns:
            float: the total cost ($).
        """
        return sum(brick.cost for brick in self.get_valid_bricks())

    def get_volume(self):
        """
        Get the total volume of the convex hull.

        Returns:
            float: the total volume (LDU^3, 1 LDU = 0.4 mm).
        """
        hull = self.get_convex_hull()
        return hull.volume if hull is not None else 0

    def get_size(self):
        """
        Get the total size of the convex hull.

        Returns:
            `:obj:array`: the length of the three dimensions (LDU, 1 LDU = 0.4 mm).
        """
        hull = self.get_convex_hull()
        return np.ptp(np.array([
                hull.points[v,:]
                for v in hull.vertices
            ]), axis=0) if hull is not None else np.zeros(3)

    def get_width(self):
        """
        Get the width of the design along the driver's side axis.

        Returns:
            float: the vehicle width (LDU, 1 LDU = 0.4 mm).
        """
        return abs(np.dot(self.get_driver_side_axis(), self.get_size()))

    def get_length(self):
        """
        Get the length of the design along the forward axis.

        Returns:
            float: the vehicle length (LDU, 1 LDU = 0.4 mm).
        """
        return abs(np.dot(self.get_forward_axis(), self.get_size()))

    def get_height(self):
        """
        Get the height of the design along the top axis.

        Returns:
            float: the vehicle height (LDU, 1 LDU = 0.4 mm).
        """
        return abs(np.dot(self.get_top_axis(), self.get_size()))

    def is_close_to_axis(self, brick, axis, tolerance=12):
        """
        Determines whether a brick is positioned on the face defined by an axis.

        Args:
            brick (`:obj:Brick`): the brick for which to check alignment.
            axis (`:obj:array`): unit vector pointing to the alignment face.
            tolerance (int): numerical tolerance.

        Returns:
            bool: True, if the brick is positioned close to the designated axis.
        """
        # check if the dot product of each vertex with the axis is close to
        # the maximum value of the dot product of the convex hull with the axis
        # i.e., check whether the vertex shares any points in common with the
        # convex hull in the direction pointed to by the axis
        return np.any(
                np.isclose(
                    np.dot(brick.vertices, axis),
                    np.max(np.dot(self.get_convex_hull().points, axis), axis=0),
                    atol=tolerance
                )
            )

    def get_wheelbase(self):
        """
        Get the wheelbase (length between axels) of the design.

        Returns:
            float: the wheelbase (LDU, 1 LDU = 0.4 mm).
        """
        if sum(1 for i in self.bricks if i.bl_id == '30027bc01') < 4:
            return 0
        # find wheelbase by taking difference between maximum and minimum
        # wheel position in the direction of the forward axis
        return np.around(
                np.max([
                    np.dot(self.get_forward_axis(), wheel.position)
                    for wheel in self.bricks if wheel.bl_id == '30027bc01'
                ]) - np.min([
                    np.dot(self.get_forward_axis(), wheel.position)
                    for wheel in self.bricks if wheel.bl_id == '30027bc01'
                ])
            )

    def get_track(self):
        """
        Get the track (width between wheels) of the design.

        Returns:
            float: the track (LDU, 1 LDU = 0.4 mm).
        """
        if sum(1 for i in self.bricks if i.bl_id == '30027bc01') < 4:
            return 0
        # find track by taking difference between maximum and minimum
        # wheel position in the direction of the driver side axis
        return np.around(
                np.max([
                    np.dot(self.get_driver_side_axis(), wheel.position)
                    for wheel in self.bricks if wheel.bl_id == '30027bc01'
                ]) - np.min([
                    np.dot(self.get_driver_side_axis(), wheel.position)
                    for wheel in self.bricks if wheel.bl_id == '30027bc01'
                ])
            )

    def get_num_components(self):
        """
        Get the number of connected components in the design.

        Returns:
            int: the number of connected components
        """
        components = []
        for brick in self.get_valid_bricks():
            intersections = []
            # loop over existing components
            for component in components:
                # loop over each brick in the component
                for other_brick in component:
                    # if intersects with brick, intersects with this component
                    if brick.intersects(other_brick):
                        intersections.append(component)
                        break
            # compile all the intersecting components
            new_component = [brick]
            # loop through each interaction
            for component in intersections:
                # loop through each brick of the component
                for other_brick in component:
                    # append the brick to the new component
                    new_component.append(other_brick)
                # remove the original component
                components.remove(component)
            # append a new component that composes all overlapping bricks
            components.append(new_component)
        return len(components)

    def get_valid_bricks(self):
        """
        Get the list of valid bricks.

        Returns:
            List[`:obj:Brick`]: the list of valid bricks
        """
        return [brick for brick in self.bricks if brick.is_valid]

    def get_invalid_bricks(self):
        """
        Get the list of invalid bricks.

        Returns:
            List[`:obj:Brick`]: the list of invalid bricks
        """
        return [
                brick for brick in self.bricks
                if brick is None or not brick.is_valid
            ]

    def get_num_seats(self):
        """
        Get the number of seats.

        Returns:
            int: the number of seats
        """
        return sum(
                1 for brick in self.get_valid_bricks()
                if brick.bl_id == "4079b"
            )

    def get_cargo_volume(self):
        """
        Get the total cargo volume.

        Returns:
            float: the cargo volume (LDU^3, 1 LDU = 0.4 mm).
        """
        return sum(
                brick.volume
                for brick in self.get_valid_bricks()
                if brick.bl_id == "4345" or brick.bl_id == "4345b"
            )

class DesignAnalysis(APIModel):
    design_id: str = Field(
        ...,
        description="Unique identifier for this design."
    )
    name: str = Field(
        ...,
        description="Name of this design."
    )
    designer: str = Field(
        ...,
        description="Name of the designer."
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of design submission."
    )
    thumbnail: Optional[str] = Field(
        None,
        description="Thumbnail image in base64 encoding."
    )
    mass: float = Field(
        ...,
        description="Vehicle mass (grams).",
    )
    width: float = Field(
        ...,
        description="Vehicle width (LDU, 1 LDU = 0.4 mm).",
    )
    length: float = Field(
        ...,
        description="Vehicle length (LDU, 1 LDU = 0.4 mm).",
    )
    height: float = Field(
        ...,
        description="Vehicle height (LDU, 1 LDU = 0.4 mm).",
    )
    wheelbase: float = Field(
        ...,
        description="Vehicle wheelbase (LDU, 1 LDU = 0.4 mm), i.e., length between wheels.",
    )
    track: float = Field(
        ...,
        description="Vehicle track (LDU, 1 LDU = 0.4 mm), i.e., width between wheels.",
    )
    volume: float = Field(
        ...,
        description="Vehicle volume (LDU^3, 1 LDU = 0.4 mm).",
    )
    number_seats: int = Field(
        ...,
        description="Number of valid seats",
    )
    cargo_volume: float = Field(
        ...,
        description="Cargo volume (LDU^3, 1 LDU = 0.4 mm)",
    )
    dsm: DesignStructureMatrix = Field(
        ...,
        description="Design structure matrix."
    )
    requirements: RequirementsAnalysis = Field(
        ...,
        description="Requirements analysis."
    )
    cost: CostAnalysis = Field(
        ...,
        description="Cost analysis."
    )
    value: ValueAnalysis = Field(
        ...,
        description="Design structure matrix."
    )
    is_valid: bool = Field(
        ...,
        description="True, if this is a valid design."
    )
    total_cost: float = Field(
        ...,
        description="Estimated total cost."
    )
    total_revenue: float = Field(
        ...,
        description="Estimated total revenue."
    )
    total_profit: float = Field(
        ...,
        description="Estimated net unit profit."
    )
    total_roi: float = Field(
        ...,
        description="Estimated return on investment."
    )

class DesignsResponse(APIModel):
    draw: int = Field(
        ...,
        description="Draw count."
    )
    records_total: int = Field(
        ...,
        description="Total number of records."
    )
    records_filtered: int = Field(
        ...,
        description="Filtered number of records."
    )
    designs: List[DesignAnalysis] = Field(
        ...,
        description="List of designs."
    )
