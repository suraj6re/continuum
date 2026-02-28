import re
import math
from lxml import etree
from typing import List, Dict, Tuple
from app.ai.geometry_model import *
from app.ai.geometry_utils import *
import numpy as np

def parse_svg_enhanced(svg_data: str, page_height: float = 1000) -> Dict:
    """Enhanced SVG parsing with full path support and transforms"""
    
    svg_root = etree.fromstring(svg_data.encode('utf-8'))
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    entities = []
    
    # Parse all elements recursively
    entities.extend(parse_svg_element(svg_root, ns, np.eye(4), page_height))
    
    # Compute global bounding box
    global_bbox = compute_global_bounding_box(entities)
    
    # Extract text entities
    text_entities = extract_text_entities(entities)
    
    # Organize entities
    organized = organize_entities(entities)
    
    return {
        'geometry': organized,
        'bounding_box': global_bbox,
        'text': text_entities,
        'units': {'unit': 'points', 'scale': 0.0254/72},
        'pipeline_type': 'vector',
        'source': 'svg_enhanced',
        'entity_count': count_entities(organized)
    }

def parse_svg_element(element, ns: Dict, parent_transform: np.ndarray, page_height: float) -> List[GeometryEntity]:
    """Recursively parse SVG element and children"""
    
    entities = []
    
    # Get element transform
    transform_str = element.get('transform', '')
    element_transform = parse_svg_transform(transform_str)
    combined_transform = parent_transform @ element_transform
    
    # Get stroke attributes
    stroke_attrs = extract_stroke_attributes(element)
    
    tag = element.tag.replace('{http://www.w3.org/2000/svg}', '')
    
    # LINE
    if tag == 'line':
        start = Point(float(element.get('x1', 0)), float(element.get('y1', 0)))
        end = Point(float(element.get('x2', 0)), float(element.get('y2', 0)))
        
        start = apply_transform_matrix(flip_y_coordinate(start, page_height), combined_transform)
        end = apply_transform_matrix(flip_y_coordinate(end, page_height), combined_transform)
        
        entities.append(Line(start=start, end=end, **stroke_attrs))
    
    # POLYLINE
    elif tag == 'polyline':
        points = parse_points_attribute(element.get('points', ''))
        points = [apply_transform_matrix(flip_y_coordinate(p, page_height), combined_transform) for p in points]
        entities.append(Polyline(points=points, closed=False, **stroke_attrs))
    
    # POLYGON
    elif tag == 'polygon':
        points = parse_points_attribute(element.get('points', ''))
        points = [apply_transform_matrix(flip_y_coordinate(p, page_height), combined_transform) for p in points]
        entities.append(Polyline(points=points, closed=True, **stroke_attrs))
    
    # CIRCLE
    elif tag == 'circle':
        cx = float(element.get('cx', 0))
        cy = float(element.get('cy', 0))
        r = float(element.get('r', 0))
        
        center = apply_transform_matrix(flip_y_coordinate(Point(cx, cy), page_height), combined_transform)
        entities.append(Circle(center=center, radius=r, **stroke_attrs))
    
    # ELLIPSE
    elif tag == 'ellipse':
        cx = float(element.get('cx', 0))
        cy = float(element.get('cy', 0))
        rx = float(element.get('rx', 0))
        ry = float(element.get('ry', 0))
        
        # Approximate as polyline
        points = approximate_ellipse_svg(cx, cy, rx, ry, page_height, combined_transform)
        entities.append(Polyline(points=points, closed=True, **stroke_attrs, metadata={'entity_type': 'ELLIPSE'}))
    
    # PATH (Full support)
    elif tag == 'path':
        d = element.get('d', '')
        if d:
            path_entities = parse_svg_path(d, page_height, combined_transform, stroke_attrs)
            entities.extend(path_entities)
    
    # TEXT
    elif tag == 'text':
        x = float(element.get('x', 0))
        y = float(element.get('y', 0))
        text_content = ''.join(element.itertext())
        font_size = parse_font_size(element.get('font-size', '12'))
        
        position = apply_transform_matrix(flip_y_coordinate(Point(x, y), page_height), combined_transform)
        entities.append(Text(position=position, text=text_content, height=font_size, **stroke_attrs))
    
    # GROUP - recurse
    elif tag == 'g':
        for child in element:
            entities.extend(parse_svg_element(child, ns, combined_transform, page_height))
    
    # CLIPPATH - extract geometry
    elif tag == 'clipPath':
        for child in element:
            entities.extend(parse_svg_element(child, ns, combined_transform, page_height))
    
    # Recurse for other elements
    else:
        for child in element:
            entities.extend(parse_svg_element(child, ns, combined_transform, page_height))
    
    return entities

def parse_svg_path(d: str, page_height: float, transform: np.ndarray, stroke_attrs: Dict) -> List[GeometryEntity]:
    """Parse SVG path with full command support"""
    
    entities = []
    commands = tokenize_path(d)
    
    current_point = Point(0, 0)
    path_start = Point(0, 0)
    current_path = []
    
    i = 0
    while i < len(commands):
        cmd = commands[i]
        
        # Move (M/m)
        if cmd in ['M', 'm']:
            i += 1
            x, y = float(commands[i]), float(commands[i+1])
            if cmd == 'm':  # relative
                current_point = Point(current_point.x + x, current_point.y + y)
            else:  # absolute
                current_point = Point(x, y)
            path_start = current_point
            current_path = [current_point]
            i += 2
        
        # Line (L/l)
        elif cmd in ['L', 'l']:
            i += 1
            x, y = float(commands[i]), float(commands[i+1])
            if cmd == 'l':
                current_point = Point(current_point.x + x, current_point.y + y)
            else:
                current_point = Point(x, y)
            current_path.append(current_point)
            i += 2
        
        # Horizontal (H/h)
        elif cmd in ['H', 'h']:
            i += 1
            x = float(commands[i])
            if cmd == 'h':
                current_point = Point(current_point.x + x, current_point.y)
            else:
                current_point = Point(x, current_point.y)
            current_path.append(current_point)
            i += 1
        
        # Vertical (V/v)
        elif cmd in ['V', 'v']:
            i += 1
            y = float(commands[i])
            if cmd == 'v':
                current_point = Point(current_point.x, current_point.y + y)
            else:
                current_point = Point(current_point.x, y)
            current_path.append(current_point)
            i += 1
        
        # Cubic Bezier (C/c)
        elif cmd in ['C', 'c']:
            i += 1
            x1, y1 = float(commands[i]), float(commands[i+1])
            x2, y2 = float(commands[i+2]), float(commands[i+3])
            x, y = float(commands[i+4]), float(commands[i+5])
            
            if cmd == 'c':
                x1 += current_point.x; y1 += current_point.y
                x2 += current_point.x; y2 += current_point.y
                x += current_point.x; y += current_point.y
            
            # Approximate curve
            curve_points = approximate_cubic_bezier(
                current_point, Point(x1, y1), Point(x2, y2), Point(x, y)
            )
            current_path.extend(curve_points)
            current_point = Point(x, y)
            i += 6
        
        # Quadratic Bezier (Q/q)
        elif cmd in ['Q', 'q']:
            i += 1
            x1, y1 = float(commands[i]), float(commands[i+1])
            x, y = float(commands[i+2]), float(commands[i+3])
            
            if cmd == 'q':
                x1 += current_point.x; y1 += current_point.y
                x += current_point.x; y += current_point.y
            
            curve_points = approximate_quadratic_bezier(
                current_point, Point(x1, y1), Point(x, y)
            )
            current_path.extend(curve_points)
            current_point = Point(x, y)
            i += 4
        
        # Close path (Z/z)
        elif cmd in ['Z', 'z']:
            if current_path:
                current_path.append(path_start)
                # Transform and flip
                transformed = [apply_transform_matrix(flip_y_coordinate(p, page_height), transform) 
                              for p in current_path]
                entities.append(Polyline(points=transformed, closed=True, **stroke_attrs))
                current_path = []
            i += 1
        
        else:
            i += 1
    
    # Add remaining path
    if len(current_path) > 1:
        transformed = [apply_transform_matrix(flip_y_coordinate(p, page_height), transform) 
                      for p in current_path]
        entities.append(Polyline(points=transformed, closed=False, **stroke_attrs))
    
    return entities

def tokenize_path(d: str) -> List[str]:
    """Tokenize SVG path data"""
    # Split by commands and numbers
    tokens = re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', d)
    return tokens

def approximate_cubic_bezier(p0: Point, p1: Point, p2: Point, p3: Point, segments: int = 10) -> List[Point]:
    """Approximate cubic Bezier curve"""
    points = []
    for i in range(1, segments + 1):
        t = i / segments
        x = (1-t)**3 * p0.x + 3*(1-t)**2*t * p1.x + 3*(1-t)*t**2 * p2.x + t**3 * p3.x
        y = (1-t)**3 * p0.y + 3*(1-t)**2*t * p1.y + 3*(1-t)*t**2 * p2.y + t**3 * p3.y
        points.append(Point(x, y))
    return points

def approximate_quadratic_bezier(p0: Point, p1: Point, p2: Point, segments: int = 10) -> List[Point]:
    """Approximate quadratic Bezier curve"""
    points = []
    for i in range(1, segments + 1):
        t = i / segments
        x = (1-t)**2 * p0.x + 2*(1-t)*t * p1.x + t**2 * p2.x
        y = (1-t)**2 * p0.y + 2*(1-t)*t * p1.y + t**2 * p2.y
        points.append(Point(x, y))
    return points

def approximate_ellipse_svg(cx: float, cy: float, rx: float, ry: float, 
                            page_height: float, transform: np.ndarray, segments: int = 32) -> List[Point]:
    """Approximate ellipse as polyline"""
    points = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        point = apply_transform_matrix(flip_y_coordinate(Point(x, y), page_height), transform)
        points.append(point)
    return points

def parse_points_attribute(points_str: str) -> List[Point]:
    """Parse SVG points attribute"""
    coords = re.findall(r'[-+]?[0-9]*\.?[0-9]+', points_str)
    points = []
    for i in range(0, len(coords), 2):
        if i + 1 < len(coords):
            points.append(Point(float(coords[i]), float(coords[i+1])))
    return points

def extract_stroke_attributes(element) -> Dict:
    """Extract stroke and fill attributes"""
    return {
        'lineweight': parse_stroke_width(element.get('stroke-width', '1')),
        'color': parse_color(element.get('stroke', 'black')),
        'metadata': {
            'stroke_dasharray': element.get('stroke-dasharray', 'none'),
            'stroke_linecap': element.get('stroke-linecap', 'butt'),
            'fill': element.get('fill', 'none')
        }
    }

def parse_stroke_width(width_str: str) -> float:
    """Parse stroke width"""
    try:
        return float(re.findall(r'[-+]?[0-9]*\.?[0-9]+', width_str)[0])
    except:
        return 1.0

def parse_color(color_str: str) -> Tuple[int, int, int]:
    """Parse color string to RGB"""
    if color_str.startswith('#'):
        hex_color = color_str.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    elif color_str.startswith('rgb'):
        nums = re.findall(r'\d+', color_str)
        return tuple(int(n) for n in nums[:3])
    else:
        # Named colors
        colors = {'black': (0,0,0), 'white': (255,255,255), 'red': (255,0,0)}
        return colors.get(color_str, (0,0,0))

def parse_font_size(size_str: str) -> float:
    """Parse font size"""
    try:
        return float(re.findall(r'[-+]?[0-9]*\.?[0-9]+', size_str)[0])
    except:
        return 12.0

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
