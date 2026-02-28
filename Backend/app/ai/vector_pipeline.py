import ezdxf
from typing import Dict, List

def run_vector_pipeline(file_path: str, file_type: str) -> Dict:
    """Process vector files (DXF, DWG, vector PDF)"""
    
    if file_type.upper() in ['DXF']:
        return process_dxf(file_path)
    elif file_type.upper() in ['DWG']:
        return process_dwg(file_path)
    else:
        raise ValueError(f"Unsupported vector file type: {file_type}")

def process_dxf(file_path: str) -> Dict:
    """Parse DXF file using ezdxf"""
    
    try:
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()
        
        # Extract entities
        lines = []
        circles = []
        polylines = []
        text_entities = []
        layers = set()
        
        for entity in modelspace:
            layers.add(entity.dxf.layer)
            
            if entity.dxftype() == 'LINE':
                lines.append({
                    'start': [entity.dxf.start.x, entity.dxf.start.y],
                    'end': [entity.dxf.end.x, entity.dxf.end.y],
                    'layer': entity.dxf.layer
                })
            
            elif entity.dxftype() == 'CIRCLE':
                circles.append({
                    'center': [entity.dxf.center.x, entity.dxf.center.y],
                    'radius': entity.dxf.radius,
                    'layer': entity.dxf.layer
                })
            
            elif entity.dxftype() == 'LWPOLYLINE':
                points = [[p[0], p[1]] for p in entity.get_points()]
                polylines.append({
                    'points': points,
                    'closed': entity.closed,
                    'layer': entity.dxf.layer
                })
            
            elif entity.dxftype() == 'TEXT':
                text_entities.append({
                    'text': entity.dxf.text,
                    'position': [entity.dxf.insert.x, entity.dxf.insert.y],
                    'height': entity.dxf.height,
                    'layer': entity.dxf.layer
                })
        
        # Normalize units
        units = doc.units
        normalized_units = normalize_units(units)
        
        return {
            'geometry': {
                'lines': lines,
                'circles': circles,
                'polylines': polylines,
                'layers': list(layers)
            },
            'text': text_entities,
            'units': normalized_units,
            'pipeline_type': 'vector'
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
