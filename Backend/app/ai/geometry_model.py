from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class Point:
    x: float
    y: float
    z: float = 0.0

@dataclass
class BoundingBox:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

@dataclass
class GeometryEntity:
    """Unified geometry model for all entity types"""
    entity_type: str
    coordinates: List[Point]
    layer: str = "0"
    color: Tuple[int, int, int] = (255, 255, 255)
    lineweight: float = 0.0
    linetype: str = "CONTINUOUS"
    rotation: float = 0.0
    transform_matrix: Optional[np.ndarray] = None
    bounding_box: Optional[BoundingBox] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.bounding_box is None:
            self.bounding_box = self.calculate_bounding_box()

    def calculate_bounding_box(self) -> BoundingBox:
        """Calculate bounding box from coordinates"""
        if not self.coordinates:
            return BoundingBox(0, 0, 0, 0)
        
        xs = [p.x for p in self.coordinates]
        ys = [p.y for p in self.coordinates]
        
        return BoundingBox(
            min_x=min(xs),
            min_y=min(ys),
            max_x=max(xs),
            max_y=max(ys)
        )

# Alias for STEP 8 requirement
DrawingEntity = GeometryEntity

class Line(GeometryEntity):
    def __init__(self, start: Point, end: Point, **kwargs):
        super().__init__(
            entity_type="LINE",
            coordinates=[start, end],
            **kwargs
        )

class Polyline(GeometryEntity):
    def __init__(self, points: List[Point], closed: bool = False, **kwargs):
        super().__init__(
            entity_type="POLYLINE",
            coordinates=points,
            **kwargs
        )
        self.metadata['closed'] = closed

class Arc(GeometryEntity):
    def __init__(self, center: Point, radius: float, start_angle: float, end_angle: float, **kwargs):
        super().__init__(
            entity_type="ARC",
            coordinates=[center],
            **kwargs
        )
        self.metadata.update({
            'radius': radius,
            'start_angle': start_angle,
            'end_angle': end_angle
        })

class Circle(GeometryEntity):
    def __init__(self, center: Point, radius: float, **kwargs):
        super().__init__(
            entity_type="CIRCLE",
            coordinates=[center],
            **kwargs
        )
        self.metadata['radius'] = radius

class Spline(GeometryEntity):
    def __init__(self, control_points: List[Point], degree: int = 3, **kwargs):
        super().__init__(
            entity_type="SPLINE",
            coordinates=control_points,
            **kwargs
        )
        self.metadata['degree'] = degree

class Text(GeometryEntity):
    def __init__(self, position: Point, text: str, height: float, **kwargs):
        super().__init__(
            entity_type="TEXT",
            coordinates=[position],
            **kwargs
        )
        self.metadata.update({
            'text': text,
            'height': height
        })

class BlockReference(GeometryEntity):
    def __init__(self, position: Point, block_name: str, scale_x: float = 1.0, 
                 scale_y: float = 1.0, scale_z: float = 1.0, **kwargs):
        super().__init__(
            entity_type="INSERT",
            coordinates=[position],
            **kwargs
        )
        self.metadata.update({
            'block_name': block_name,
            'scale_x': scale_x,
            'scale_y': scale_y,
            'scale_z': scale_z
        })

class Hatch(GeometryEntity):
    def __init__(self, boundary_points: List[Point], pattern: str, **kwargs):
        super().__init__(
            entity_type="HATCH",
            coordinates=boundary_points,
            **kwargs
        )
        self.metadata['pattern'] = pattern
