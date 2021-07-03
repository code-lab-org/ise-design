from fastapi_utils.api_model import APIModel
from pydantic import conlist, Field
from typing import List, Optional
import numpy as np

class Brick(APIModel):
    bl_id: Optional[str] = Field(
        None,
        description="BrickLink brick identifier."
    )
    ld_color: Optional[str] = Field(
        None,
        description="LDraw color identifier."
    )
    position: conlist(float, min_items=3, max_items=3) = Field(
        [0,0,0],
        description="Brick position vector. See LDraw specification."
    )
    rotation: conlist(conlist(float, min_items=3, max_items=3), min_items=3, max_items=3) = Field(
        [[1,0,0],[0,1,0],[0,0,1]],
        description="Brick rotation matrix. See LDraw specification."
    )
    id: Optional[str] = Field(
        None,
        description="Brick identifier."
    )
    name: Optional[str] = Field(
        None,
        description="Brick name."
    )
    cost: Optional[float] = Field(
        None,
        description="Brick cost (U.S. dollars)."
    )
    mass: Optional[float] = Field(
        None,
        description="Brick mass (grams)."
    )
    is_valid: bool = Field(
        False,
        description="True, if this brick is defined in the palette."
    )
    vertices: Optional[conlist(conlist(float, min_items=3, max_items=3), min_items=8, max_items=8)] = Field(
        None,
        description="Brick bounding box vertices (1 LDU = 0.4 mm)."
    )
    valid_forward_axes: Optional[List[conlist(float, min_items=3, max_items=3)]] = Field(
        None,
        description="Unit vectors that are acceptable forward axes."
    )
    safety: Optional[float] = Field(
        None,
        description="Safety metric contribution."
    )
    coolness: Optional[float] = Field(
        None,
        description="Coolness metric contribution."
    )
    volume: Optional[float] = Field(
        None,
        description="Volume of bounding box (LDU^3, 1 LDU = 0.4 mm)."
    )
    bl_color: Optional[int] = Field(
        None,
        description="BrickLink color identifier."
    )

    def intersects(self, brick, inclusive=False):
        """
        Determines whether this brick intersects another brick.

        Args:
            brick (`:obj:Brick`): the other brick.
            inclusive (bool): True, if position checks are inclusive (<=, >=).

        Returns:
            bool: True, if this brick intersects the provided brick.
        """
        return all(
            min(v[i] for v in self.vertices) <= max(v[i] for v in brick.vertices)
            and max(v[i] for v in self.vertices) >= min(v[i] for v in brick.vertices)
            for i in range(3)
        ) if inclusive else all(
            min(v[i] for v in self.vertices) < max(v[i] for v in brick.vertices)
            and max(v[i] for v in self.vertices) > min(v[i] for v in brick.vertices)
            for i in range(3)
        )

    def is_aligned(self, design):
        """
        Determines whether this brick is aligned with a design.

        Args:
            design (`:obj:Design`): the design.

        Returns:
            bool: True, if this brick is properly aligned with the design.
        """
        # check if the brick's "valid forward axis" (rotated based on brick
        # orientation) is orthogonal to the vehicle "forward axis" (i.e.,
        # vector dot product is 0) for any of the brick's "valid forward axes"
        return (self.valid_forward_axes is None) or any(
            np.around(
                np.dot(
                    design.get_forward_axis(),
                    np.matmul(self.rotation, forward_axis)
                )
            ) > 0
            for forward_axis in self.valid_forward_axes
        )
