import ezdxf
from typing import Dict, List
import math

def run_vector_pipeline(file_path: str, file_type: str) -> Dict:
    """Process vector files (DXF, DWG, vector PDF)"""
    
    if file_type.upper() in ['DXF']:
        return process_dxf(file_path)
    elif file_type.upper() in ['DWG']:
        return process_dwg(file_path)
    else:
        raise ValueError(f"Unsupported vector file type: {file_type}")

def process_dxf(file_path: str) -> Dict:
    """Parse DXF file using ezdxf - Extract all entity types"""
    
    try:
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()
        
        # Extract entities
        lines = []
        circles = []
        arcs = []
        polylines = []
        lwpolylines = []
        hatches = []
        text_entities = []
        mtext_entities = []
        layers = set()
        
        for entity in modelspace:
            layer_name = entity.dxf.layer
            layers.add(layer_name)
            
            # LINE
            if entity.dxftype() == 'LINE':
                lines.append({
                    'start': [entity.dxf.start.x, entity.dxf.start.y],
                    'end': [entity.dxf.end.x, entity.dxf.end.y],
                    'layer': layer_name,
                    'color': entity.dxf.color if hasattr(entity.dxf, 'color') else None,
                    'lineweight': entity.dxf.lineweight if hasattr(entity.dxf, 'lineweight') else None
                })
            
            # CIRCLE
            elif entity.dxftype() == 'CIRCLE':
                circles.append({
                    'center': [entity.dxf.center.x, entity.dxf.center.y],
                    'radius': entity.dxf.radius,
                    'layer': layer_name,
                    'color': entity.dxf.color if hasattr(entity.dxf, 'color') else None
                })
            
            # ARC
            elif entity.dxftype() == 'ARC':
                arcs.append({
                    'center': [entity.dxf.center.x, entity.dxf.center.y],
                    'radius': entity.dxf.radius,
                    'start_angle': entity.dxf.start_angle,
                    'end_angle': entity.dxf.end_angle,
                    'layer': layer_name,
                    'color': entity.dxf.color if hasattr(entity.dxf, 'color') else None
                })
            
            # LWPOLYLINE
            elif entity.dxftype() == 'LWPOLYLINE':
                points = [[p[0], p[1]] for p in entity.get_points()]
                lwpolylines.append({
                    'points': points,
                    'closed': entity.closed,
                    'layer': layer_name,
                    'color': entity.dxf.color if hasattr(entity.dxf, 'color') else None
                })
            
            # POLYLINE
            elif entity.dxftype() == 'POLYLINE':
                points = [[v.dxf.location.x, v.dxf.location.y] for v in entity.vertices]
                polylines.append({
                    'points': points,
                    'closed': entity.is_closed,
                    'layer': layer_name
                })
            
            # HATCH
            elif entity.dxftype() == 'HATCH':
                hatches.append({
                    'pattern': entity.dxf.pattern_name,
                    'layer': layer_name,
                    'paths': len(entity.paths)
                })
            
            # TEXT
            elif entity.dxftype() == 'TEXT':
                text_entities.append({
                    'text': entity.dxf.text,
                    'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                    'height': entity.dxf.height,
                    'layer': layer_name,
                    'rotation': entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0
                })
            
            # MTEXT
            elif entity.dxftype() == 'MTEXT':
                mtext_entities.append({
                    'text': entity.text,
                    'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                    'height': entity.dxf.char_height,
                    'layer': layer_name
                })
        
        # Normalize units
        units = doc.units
        normalized_units = normalize_units(units)
        
        return {
            'geometry': {
                'lines': lines,
                'circles': circles,
                'arcs': arcs,
                'lwpolylines': lwpolylines,
                'polylines': polylines,
                'hatches': hatches,
                'layers': list(layers)
            },
            'text': text_entities + mtext_entities,
            'units': normalized_units,
            'pipeline_type': 'vector',
            'entity_count': {
                'lines': len(lines),
                'circles': len(circles),
                'arcs': len(arcs),
                'polylines': len(lwpolylines) + len(polylines),
                'hatches': len(hatches),
                'text': len(text_entities) + len(mtext_entities)
            }
        }
    
    except Exception as e:
        raise ValueError(f"Failed to parse DXF: {str(e)}")

def process_dwg(file_path: str) -> Dict:
    """Process DWG file (requires conversion to DXF first)"""
    # DWG requires external converter or library
    # Placeholder implementation
    return {
        'geometry': {'lines': [], 'circles': [], 'polylines': []},
        'text': [],
        'units': {'unit': 'meters', 'scale': 1.0},
        'pipeline_type': 'vector',
        'note': 'DWG processing requires conversion to DXF'
    }

def normalize_units(units: int) -> Dict:
    """Normalize DXF units to standard format"""
    unit_map = {
        0: 'unitless',
        1: 'inches',
        2: 'feet',
        4: 'millimeters',
        5: 'centimeters',
        6: 'meters',
    }
    
    scale_to_meters = {
        'inches': 0.0254,
        'feet': 0.3048,
        'millimeters': 0.001,
        'centimeters': 0.01,
        'meters': 1.0,
        'unitless': 1.0
    }
    
    unit_name = unit_map.get(units, 'meters')
    
    return {
        'unit': unit_name,
        'scale': scale_to_meters.get(unit_name, 1.0)
    }
