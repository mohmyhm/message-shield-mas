from .chain import ChainTopology
from .star import StarTopology
from .mesh import MeshTopology

REGISTRY: dict[str, type] = {
    "chain": ChainTopology,
    "star": StarTopology,
    "mesh": MeshTopology,
}

def get_topology(name: str):
    if name not in REGISTRY:
        raise ValueError(f"Unknown topology '{name}'. Choose from {list(REGISTRY)}")
    return REGISTRY[name]()
