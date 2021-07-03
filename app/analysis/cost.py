from .dsm import (
    get_dsm,
    get_complexity_c1,
    get_complexity_c2,
    get_complexity_c3,
    get_complexity
)
from ..schemas.design import Design
from ..schemas.cost import (
    CostAnalysis,
    BillOfMaterialsLine,
    AssemblyCostAnalysis,
    OverheadCostAnalysis
)

__version__ = "2.0.1"

def get_cost_analysis(design: Design):
    """
    Get the cost analysis for a design.

    Args:
        design (`:obj:Design`): the design to analyze.

    Returns:
        `:obj:CostAnalysis`: the cost analysis.
    """
    return CostAnalysis(
        version=__version__,
        materials=get_cost_materials(design),
        bom=get_bom(design),
        assembly=AssemblyCostAnalysis(
            components=get_cost_assembly_components(design),
            integration=get_cost_assembly_integration(design),
            total=get_cost_assembly_total(design)
        ),
        overhead=OverheadCostAnalysis(
            engineering=get_cost_overhead_engineering(design),
            marketing=get_cost_overhead_marketing(design),
            facilities=get_cost_overhead_facilities(design),
            administration=get_cost_overhead_administration(design),
            total=get_cost_overhead_total(design),
        ),
        total=get_cost_total(design)
    )

def get_cost_materials(design: Design):
    return design.get_cost()

def get_bom(design: Design):
    bom = {}
    for brick in design.get_valid_bricks():
        if brick.id in bom:
            bom[brick.id].quantity += 1
        else:
            bom[brick.id] = BillOfMaterialsLine(
                name=brick.name,
                cost=brick.cost,
                quantity=1
            )
    return bom

def get_cost_assembly_components(design: Design):
    return get_complexity_c1(get_dsm(design))/100

def get_cost_assembly_integration(design: Design):
    dsm = get_dsm(design)
    return get_complexity_c2(dsm)*get_complexity_c3(dsm)/100

def get_cost_assembly_total(design: Design):
    return get_complexity(get_dsm(design))/100

def get_cost_overhead_engineering(design: Design):
    return (get_cost_materials(design) + get_cost_assembly_total(design)) * 0.35

def get_cost_overhead_marketing(design: Design):
    return (get_cost_materials(design) + get_cost_assembly_total(design)) * 0.20

def get_cost_overhead_facilities(design: Design):
    return (get_cost_materials(design) + get_cost_assembly_total(design)) * 0.30

def get_cost_overhead_administration(design: Design):
    return (get_cost_materials(design) + get_cost_assembly_total(design)) * 0.25

def get_cost_overhead_total(design: Design):
    return (get_cost_materials(design) + get_cost_assembly_total(design)) * 1.10

def get_cost_total(design: Design):
    return get_cost_materials(design) + get_cost_assembly_total(design) + get_cost_overhead_total(design)
