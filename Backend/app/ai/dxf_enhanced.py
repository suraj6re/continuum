import ezdxf
from typing import Dict, List
from app.ai.geometry_model import *
from app.ai.geometry_utils import *
import logging

logger = logging.getLogger(__name__)

def process_dxf_enhanced(file_path: str) -> Dict:
    """Enhanced DXF processing with blocks, splines, and all entity types"""
    
    try:
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()
        
        # Extract units
        units_info = extract_units(doc)
        
        # Extract blocks first
        blocks = extract_blocks(doc)
        
        # Extract all entities
        entities = []
        layers = set()
        
        for entity in modelspace:
            try:
                layers.add(entity.dxf.layer)
                parsed = parse_entity(entity, blocks, units_info)
                if parsed:
                    entities.extend(parsed if isinstance(parsed, list) else [parsed])
            except Exception as e:
                logger.warning(f"Failed to parse entity {entity.dxftype()}: {e}")
        
        # Compute global bounding box
        global_bbox = compute_global_bounding_box(entities)
        
        # Extract text entities
        text_entities = extract_text_entities(entities)
        
        # Organize by type
        organized = organize_entities(entities)
        
        return {
            'geometry': organized,
            'bounding_box': global_bbox,
            'text': text_entities,
            'units': units_info,
            'layers': list(layers),
            'blocks': list(blocks.keys()),
            'pipeline_type': 'vector',
            'entity_count': count_entities(organized)
        }
    
    except Exception as e:
        raise ValueError(f"Failed to parse DXF: {str(e)}")

def extract_units(doc) -> Dict:
    """Extract and normalize units from DXF"""
    try:
        insunits = doc.header.get('$INSUNITS', 0)
        unit_map = {
            0: 'unitless', 1: 'inches', 2: 'feet', 3: 'miles',
            4: 'millimeters', 5: 'centimeters', 6: 'meters', 7: 'kilometers'
        }
        unit_name = unit_map.get(insunits, 'meters')
        
        scale_to_meters = {
            'inches': 0.0254, 'feet': 0.3048, 'millimeters': 0.001,
            'centimeters': 0.01, 'meters': 1.0, 'unitless': 1.0
        }
        
        return {
            'unit': unit_name,
            'scale': scale_to_meters.get(unit_name, 1.0),
            'insunits': insunits
        }
    except:
        return {'unit': 'meters', 'scale': 1.0, 'insunits': 6}

def extract_blocks(doc) -> Dict:
    """Extract block definitions"""
    blocks = {}
    
    for block in doc.blocks:
        if not block.name.startswith('*'):  # Skip anonymous blocks
            block_entities = []
            for entity in block:
                try:
                    parsed = parse_entity(entity, {}, {'unit': 'meters', 'scale': 1.0})
                    if parsed:
                        block_entities.extend(parsed if isinstance(parsed, list) else [parsed])
                except:
                    pass
            
            blocks[block.name] = block_entities
    
    return blocks

def parse_entity(entity, blocks: Dict, units: Dict) -> List[GeometryEntity]:
    """Parse any DXF entity to unified geometry model"""
    
    etype = entity.dxftype()
    layer = entity.dxf.layer
    color = get_color(entity)
    lineweight = getattr(entity.dxf, 'lineweight', 0)
    
    # LINE
    if etype == 'LINE':
        return [Line(
            start=Point(entity.dxf.start.x, entity.dxf.start.y, entity.dxf.start.z),
            end=Point(entity.dxf.end.x, entity.dxf.end.y, entity.dxf.end.z),
            layer=layer, color=color, lineweight=lineweight
        )]
    
    # CIRCLE
    elif etype == 'CIRCLE':
        return [Circle(
            center=Point(entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
            radius=entity.dxf.radius,
            layer=layer, color=color, lineweight=lineweight
        )]
    
    # ARC
    elif etype == 'ARC':
        return [Arc(
            center=Point(entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
            radius=entity.dxf.radius,
            start_angle=entity.dxf.start_angle,
            end_angle=entity.dxf.end_angle,
            layer=layer, color=color, lineweight=lineweight
        )]
    
    # LWPOLYLINE
    elif etype == 'LWPOLYLINE':
        points = [Point(p[0], p[1], 0) for p in entity.get_points()]
        return [Polyline(
            points=points,
            closed=entity.closed,
            layer=layer, color=color, lineweight=lineweight
        )]
    
    # POLYLINE
    elif etype == 'POLYLINE':
        points = [Point(v.dxf.location.x, v.dxf.location.y, v.dxf.location.z) 
                  for v in entity.vertices]
        return [Polyline(
            points=points,
            closed=entity.is_closed,
            layer=layer, color=color, lineweight=lineweight
        )]
    
    # SPLINE
    elif etype == 'SPLINE':
        control_points = [Point(p[0], p[1], p[2] if len(p) > 2 else 0) 
                          for p in entity.control_points]
        return [Spline(
            control_points=control_points,
            degree=entity.dxf.degree,
            layer=layer, color=color, lineweight=lineweight
        )]
    
    # ELLIPSE
    elif etype == 'ELLIPSE':
        # Approximate ellipse as polyline
        points = approximate_ellipse(entity)
        return [Polyline(
            points=points,
            closed=True,
            layer=layer, color=color, lineweight=lineweight,
            metadata={'entity_type': 'ELLIPSE'}
        )]
    
    # TEXT
    elif etype == 'TEXT':
        return [Text(
            position=Point(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
            text=entity.dxf.text,
            height=entity.dxf.height,
            layer=layer, color=color,
            rotation=getattr(entity.dxf, 'rotation', 0)
        )]
    
    # MTEXT
    elif etype == 'MTEXT':
        return [Text(
            position=Point(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
            text=entity.text,
            height=entity.dxf.char_height,
            layer=layer, color=color
        )]
    
    # INSERT (Block Reference)
    elif etype == 'INSERT':
        block_ref = BlockReference(
            position=Point(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
            block_name=entity.dxf.name,
            scale_x=entity.dxf.xscale,
            scale_y=entity.dxf.yscale,
            scale_z=entity.dxf.zscale,
            layer=layer, color=color,
            rotation=entity.dxf.rotation
        )
        
        # Explode block if definition exists
        if entity.dxf.name in blocks:
            return explode_block(block_ref, blocks[entity.dxf.name])
        
        return [block_ref]
    
    # HATCH
    elif etype == 'HATCH':
        boundary_points = extract_hatch_boundary(entity)
        return [Hatch(
            boundary_points=boundary_points,
            pattern=entity.dxf.pattern_name,
            layer=layer, color=color,
            metadata={
                'pattern_angle': getattr(entity.dxf, 'pattern_angle', 0),
                'pattern_scale': getattr(entity.dxf, 'pattern_scale', 1.0),
                'solid': entity.dxf.solid_fill
            }
        )]
    
    return []

def get_color(entity) -> Tuple[int, int, int]:
    """Extract RGB color from entity"""
    try:
        if hasattr(entity, 'rgb'):
            return entity.rgb
        elif hasattr(entity.dxf, 'true_color'):
            tc = entity.dxf.true_color
            return ((tc >> 16) & 0xFF, (tc >> 8) & 0xFF, tc & 0xFF)
        else:
            # ACI color to RGB (simplified)
            aci = getattr(entity.dxf, 'color', 7)
            return aci_to_rgb(aci)
    except:
        return (255, 255, 255)

def aci_to_rgb(aci: int) -> Tuple[int, int, int]:
    """Convert AutoCAD Color Index to RGB"""
    aci_colors = {
        1: (255, 0, 0), 2: (255, 255, 0), 3: (0, 255, 0),
        4: (0, 255, 255), 5: (0, 0, 255), 6: (255, 0, 255),
        7: (255, 255, 255), 8: (128, 128, 128)
    }
    return aci_colors.get(aci, (255, 255, 255))

def approximate_ellipse(entity, num_points: int = 32) -> List[Point]:
    """Approximate ellipse as polyline"""
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Simplified ellipse approximation
        x = entity.dxf.center.x + entity.dxf.major_axis.x * math.cos(angle)
        y = entity.dxf.center.y + entity.dxf.major_axis.y * math.sin(angle)
        points.append(Point(x, y, entity.dxf.center.z))
    return points

def extract_hatch_boundary(entity) -> List[Point]:
    """Extract boundary points from hatch"""
    points = []
    for path in entity.paths:
        for edge in path.edges:
            if hasattr(edge, 'start'):
                points.append(Point(edge.start[0], edge.start[1], 0))
    return points

def explode_block(block_ref: BlockReference, block_entities: List[GeometryEntity]) -> List[GeometryEntity]:
    """Transform block entities to world coordinates"""
    exploded = []
    
    # Create transformation matrix
    matrix = create_transform_matrix(
        tx=block_ref.coordinates[0].x,
        ty=block_ref.coordinates[0].y,
        tz=block_ref.coordinates[0].z,
        sx=block_ref.metadata['scale_x'],
        sy=block_ref.metadata['scale_y'],
        sz=block_ref.metadata['scale_z'],
        rotation=block_ref.rotation
    )
    
    for entity in block_entities:
        transformed_coords = [apply_transform_matrix(p, matrix) for p in entity.coordinates]
        entity.coordinates = transformed_coords
        exploded.append(entity)
    
    return exploded

def organize_entities(entities: List[GeometryEntity]) -> Dict:
    """Organize entities by type"""
    organized = {}
    for entity in entities:
        etype = entity.entity_type
        if etype not in organized:
            organized[etype] = []
        organized[etype].append(entity.__dict__)
    return organized

def count_entities(organized: Dict) -> Dict:
    """Count entities by type"""
    return {k: len(v) for k, v in organized.items()}

def extract_text_entities(entities: List[GeometryEntity]) -> List[Dict]:
    """Extract text entities in required format"""
    text_list = []
    for entity in entities:
        if entity.entity_type == 'TEXT':
            text_list.append({
                'text': entity.metadata.get('text', ''),
                'position': [entity.coordinates[0].x, entity.coordinates[0].y],
                'layer': entity.layer
            })
    return text_list
