import numpy as np
import math

from ..schemas.design import Design
from ..schemas.value import ValueAnalysis

__version__ = "2.0.0"

def get_value_analysis(design: Design):
    """
    Get the value analysis for a design.

    Args:
        design (`:obj:Design`): the design to analyze.

    Returns:
        `:obj:ValueAnalysis`: the value analysis.
    """
    return ValueAnalysis(
        version=__version__,
        passenger=get_value_passenger_capacity(design),
        cargo=get_value_cargo_capacity(design),
        handling=get_value_handling(design),
        acceleration=get_value_acceleration(design),
        safety=get_value_safety(design),
        coolness=get_value_coolness(design),
        total=get_value_total(design),
        price=get_value_price(design),
    )

def get_logistic_transform(point, min_value=0, max_value=1, midpoint=0, growth_rate=1):
    return min_value + (max_value-min_value)/(1+math.exp(-growth_rate*(point-midpoint)))

def get_value_passenger_capacity(design: Design):
    volume = design.get_volume()/1000*0.4**3
    num_seats = sum(
        1 for brick in design.get_valid_bricks()
        if brick.bl_id == "4079b"
    )
    return get_logistic_transform(
        num_seats*50 + volume,
        min_value=0,
        max_value=100,
        midpoint=200,
        growth_rate=0.02
    )

def get_value_cargo_capacity(design: Design):
    volume = design.get_volume()/1000*0.4**3
    cargo_volume = sum(
        brick.volume/1000*0.4**3
        for brick in design.get_valid_bricks()
        if brick.bl_id == "4345" or brick.bl_id == "4345b"
    )
    return get_logistic_transform(
        cargo_volume*4 + volume,
        min_value=0,
        max_value=100,
        midpoint=125,
        growth_rate=0.03
    )

def get_value_handling(design: Design):
    mass = design.get_mass()
    wheelbase = design.get_wheelbase()*0.4
    return get_logistic_transform(
        mass + wheelbase,
        min_value=100,
        max_value=0,
        midpoint=75,
        growth_rate=0.075
    )

def get_value_acceleration(design: Design):
    mass = design.get_mass()
    height = design.get_height()*0.4
    return get_logistic_transform(
        mass*5 + height,
        min_value=100,
        max_value=0,
        midpoint=160,
        growth_rate=0.1
    )

def get_value_safety(design: Design):
    mass = design.get_mass()
    safety = sum(
        brick.safety if brick.is_aligned(design) else 0
        for brick in design.get_valid_bricks()
    )
    return get_logistic_transform(
        mass*2 + safety,
        min_value=0,
        max_value=100,
        midpoint=80,
        growth_rate=0.04
    )

def get_value_coolness(design: Design):
    coolness = sum(
        brick.coolness
        for brick in design.get_valid_bricks()
    )
    return get_logistic_transform(
        coolness,
        min_value=0,
        max_value=100,
        midpoint=30,
        growth_rate=0.09
    )

def get_value_total(design: Design):
    return (
            0.2*get_value_passenger_capacity(design)
            + 0.2*get_value_cargo_capacity(design)
            + 0.1*get_value_handling(design)
            + 0.15*get_value_acceleration(design)
            + 0.15*get_value_safety(design)
            + 0.2*get_value_coolness(design)
        )

def get_value_price(design: Design):
    return get_logistic_transform(
            get_value_total(design),
            min_value=2,
            max_value=20,
            midpoint=50,
            growth_rate=0.1
        )
