from scipy.cluster import hierarchy
from scipy import linalg
import numpy as np

from ..schemas.design import Design
from ..schemas.dsm import DesignStructureMatrix

__version__ = "2.0.0"

def get_dsm_analysis(design: Design):
    """
    Get the design structure matrix for a design.

    Args:
        design (`:obj:Design`): the design to analyze.

    Returns:
        `:obj:DesignStructureMatrix`: the design structure matrix.
    """
    dsm = get_dsm(design)
    return DesignStructureMatrix(
        version=__version__,
        matrix=dsm,
        labels=get_dsm_labels(design),
        order=get_dsm_order(dsm)
    )

def get_dsm(design: Design):
    return [ [ a.intersects(b)
            for a in design.get_valid_bricks() ]
            for b in design.get_valid_bricks() ]

def get_dsm_labels(design):
    return [brick.name for brick in design.get_valid_bricks()]

def get_dsm_order(dsm):
    return hierarchy.dendrogram(
            hierarchy.linkage(dsm, method='single', optimal_ordering=True),
            no_plot=True
        )['leaves']

def get_graph_energy(dsm):
    return np.sum(np.abs(linalg.eig(dsm - np.eye(len(dsm)))[0]))

def get_complexity_c1(dsm, alpha=1):
    # ref: kaushik sinha
    return np.sum(np.multiply(alpha, np.ones(len(dsm))))

def get_complexity_c2(dsm, beta=1):
    # ref: kaushik sinha
    return np.sum(np.multiply(beta, dsm - np.eye(len(dsm))))

def get_complexity_c3(dsm, gamma=None):
    # ref: kaushik sinha
    if gamma is None: gamma = 1/len(dsm)
    return gamma*np.sum(linalg.svd(dsm)[1])

def get_complexity(dsm, alpha=1, beta=1, gamma=None):
    # ref: kaushik sinha
    return (
            get_complexity_c1(dsm, alpha)
            + get_complexity_c2(dsm, beta)
            * get_complexity_c3(dsm, gamma)
        )
