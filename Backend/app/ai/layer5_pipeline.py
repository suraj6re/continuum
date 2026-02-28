"""Layer 5 Pipeline: Structured Element Graph Builder
Converts fragmented data into canonical building model (Internal Truth)
"""
from typing import Dict, List
import uuid
from app.ai.layer5_duplicate_merger import merge_duplicate_nodes
from app.ai.layer5_relationship_builder import build_relationships
from app.ai.layer5_level_assignment import assign_levels
from app.ai.layer5_confidence_integration import integrate_confidence

def build_canonical_nodes(layer3_output: Dict, layer4_output: Dict, layer1_output: Dict) -> List[Dict]:
    """Build canonical nodes with complete schema from Layer 3 elements
    
    Args:
        layer3_output: Layer 3 element detection output
        layer4_output: Layer 4 QTO measurements
        layer1_output: Layer 1 geometry (for geometry data)
    
    Returns:
        List of canonical nodes with complete schema
    """
    nodes = []
    
    # Get measurements from Layer 4
    measurements = {m.get('element_id'): m for m in layer4_output.get('measurements', [])}
    
    # Get geometry from Layer 1
    geometry_map = {}
    for geom_type, entities in layer1_output.get('geometry', {}).items():
        for entity in entities:
            entity_id = entity.get('id')
            if entity_id:
                geometry_map[entity_id] = entity
    
    # Process each element from Layer 3
    for element in layer3_output.get('elements', []):
        elem_id = element.get('id')
        elem_type = element.get('type')
        
        # Get measurement and geometry data
        measurement = measurements.get(elem_id, {})
        geometry_data = geometry_map.get(elem_id, {})
        
        # Build canonical node with complete schema
        node = {
            'id': elem_id,
            'type': elem_type,
            'geometry': {},
            'dimensions': {},
            'material': {},
            'level': 'Ground Floor',
            'source_drawing': layer1_output.get('source', 'unknown'),
            'confidence': element.get('confidence', 0.5)
        }
        
        # Extract geometry (centerline/polygon)
        if geometry_data:
            coords = geometry_data.get('coordinates', [])
            if coords:
                node['geometry']['centerline'] = [[c.get('x', 0), c.get('y', 0)] for c in coords]
                node['geometry']['polygon'] = [[c.get('x', 0), c.get('y', 0)] for c in coords]
        
        # Parse material into category and grade
        material_str = element.get('material', 'Unknown')
        node['material'] = {
            'category': material_str,
            'grade': extract_material_grade(material_str)
        }
        
        # Add type-specific dimensions
        if elem_type == 'Wall':
            node['dimensions'] = {
                'length': element.get('length', 0),
                'thickness': element.get('thickness', 0),
                'height': element.get('height', 3.0)
            }
        
        elif elem_type == 'Slab':
            node['dimensions'] = {
                'area': element.get('area', 0),
                'thickness': element.get('thickness', 0.15),
                'length': 0,
                'width': 0
            }
        
        elif elem_type == 'Column':
            node['dimensions'] = {
                'width': element.get('width', 0.3),
                'depth': element.get('depth', 0.3),
                'height': element.get('height', 3.0)
            }
        
        elif elem_type in ['Door', 'Window']:
            node['dimensions'] = {
                'width': element.get('width', 0),
                'height': element.get('height', 0)
            }
            node['code'] = element.get('code', '')
        
        nodes.append(node)
    
    return nodes

def extract_material_grade(material_str: str) -> str:
    """Extract material grade from material string
    
    Args:
        material_str: Material string (e.g., 'Concrete M25', 'Brick')
    
    Returns:
        Material grade or 'Standard'
    """
    # Check for concrete grades
    if 'M' in material_str.upper():
        parts = material_str.upper().split('M')
        if len(parts) > 1:
            grade = parts[1].strip().split()[0]
            return f'M{grade}'
    
    # Check for steel grades
    if 'FE' in material_str.upper():
        return 'FE500'
    
    return 'Standard'

def build_canonical_edges(layer3_output: Dict) -> List[Dict]:
    """Build canonical edges with proper relationship schema
    
    Args:
        layer3_output: Layer 3 element detection output
    
    Returns:
        List of canonical edges with relationship types
    """
    edges = []
    
    for rel in layer3_output.get('relationships', []):
        # Map relationship types to canonical names
        rel_type = rel.get('type', 'connected')
        canonical_relation = map_relationship_type(rel_type, 
                                                   rel.get('source_type'),
                                                   rel.get('target_type'))
        
        edge = {
            'from': rel.get('source'),
            'to': rel.get('target'),
            'relation': canonical_relation
        }
        edges.append(edge)
    
    return edges

def map_relationship_type(rel_type: str, source_type: str, target_type: str) -> str:
    """Map relationship type to canonical relationship name
    
    Args:
        rel_type: Original relationship type
        source_type: Source element type
        target_type: Target element type
    
    Returns:
        Canonical relationship name
    """
    # Door/Window to Wall
    if source_type in ['Door', 'Window'] and target_type == 'Wall':
        return 'attached_to'
    
    # Column to Slab
    if source_type == 'Column' and target_type == 'Slab':
        return 'inside'
    
    # Wall to Wall
    if source_type == 'Wall' and target_type == 'Wall':
        return 'intersects'
    
    # Slab to Wall
    if source_type == 'Slab' and target_type == 'Wall':
        return 'supported_by'
    
    # Default
    return 'connected'

def merge_duplicate_nodes(nodes: List[Dict]) -> List[Dict]:
    """Merge duplicate nodes based on spatial proximity and type
    
    Args:
        nodes: List of canonical nodes
    
    Returns:
        Deduplicated nodes
    """
    # Simple deduplication by ID (Layer 3 should handle spatial merging)
    seen_ids = set()
    unique_nodes = []
    
    for node in nodes:
        if node['id'] not in seen_ids:
            seen_ids.add(node['id'])
            unique_nodes.append(node)
    
    return unique_nodes

def attach_metadata(nodes: List[Dict], layer2_output: Dict) -> List[Dict]:
    """Attach metadata from Layer 2 (scale, legend, schedules)
    
    Args:
        nodes: List of canonical nodes
        layer2_output: Layer 2 semantic understanding output
    
    Returns:
        Nodes with attached metadata
    """
    scale_info = layer2_output.get('scale_info', {})
    legend_dict = layer2_output.get('legend_dictionary', {})
    schedules = layer2_output.get('schedules', {})
    
    for node in nodes:
        # Attach scale info to source_drawing
        if scale_info:
            node['scale_ratio'] = scale_info.get('ratio', 1.0)
        
        # Enhance material with legend info
        material_cat = node.get('material', {}).get('category', '')
        if material_cat in legend_dict:
            node['material']['legend_label'] = legend_dict[material_cat]
        
        # Attach schedule info for doors/windows
        if node['type'] in ['Door', 'Window']:
            code = node.get('code', '')
            for schedule_name, schedule_data in schedules.items():
                for row in schedule_data.get('data', []):
                    if code in str(row):
                        node['schedule_data'] = row
                        break
    
    return nodes

def compute_graph_statistics(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """Compute statistics for the canonical graph
    
    Args:
        nodes: List of canonical nodes
        edges: List of canonical edges
    
    Returns:
        Graph statistics
    """
    stats = {
        'total_elements': len(nodes),
        'total_relationships': len(edges),
        'elements_by_type': {},
        'elements_by_level': {},
        'avg_confidence': 0,
        'total_volume': 0,
        'total_area': 0
    }
    
    # Count by type and level
    for node in nodes:
        node_type = node['type']
        node_level = node.get('level', 'Unknown')
        
        stats['elements_by_type'][node_type] = stats['elements_by_type'].get(node_type, 0) + 1
        stats['elements_by_level'][node_level] = stats['elements_by_level'].get(node_level, 0) + 1
        
        # Sum confidence
        stats['avg_confidence'] += node.get('confidence', 0)
    
    # Average confidence
    if nodes:
        stats['avg_confidence'] /= len(nodes)
    
    return stats

def validate_canonical_graph(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """Validate the canonical graph for completeness
    
    Args:
        nodes: List of canonical nodes
        edges: List of canonical edges
    
    Returns:
        Validation report
    """
    issues = []
    warnings = []
    
    # Check for nodes without dimensions
    for node in nodes:
        if not node.get('dimensions'):
            issues.append(f"Node {node['id']} missing dimensions")
        
        # Check for low confidence
        if node.get('confidence', 0) < 0.5:
            warnings.append(f"Node {node['id']} has low confidence: {node['confidence']}")
        
        # Check for missing material
        if node.get('material') == 'Unknown':
            warnings.append(f"Node {node['id']} has unknown material")
    
    # Check for orphaned edges
    node_ids = {n['id'] for n in nodes}
    for edge in edges:
        if edge['from'] not in node_ids:
            issues.append(f"Edge references missing source: {edge['from']}")
        if edge['to'] not in node_ids:
            issues.append(f"Edge references missing target: {edge['to']}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'total_issues': len(issues),
        'total_warnings': len(warnings)
    }

def run_layer5_pipeline(layer1_output: Dict, layer2_output: Dict, layer3_output: Dict, layer4_output: Dict) -> Dict:
    """Run complete Layer 5 pipeline - Build Canonical Element Graph
    
    Args:
        layer1_output: Layer 1 geometry extraction
        layer2_output: Layer 2 semantic understanding
        layer3_output: Layer 3 element detection
        layer4_output: Layer 4 QTO measurements
    
    Returns:
        Canonical building model (structured element graph)
    """
    
    # Step 1: Build canonical nodes with complete schema
    nodes = build_canonical_nodes(layer3_output, layer4_output, layer1_output)
    
    # Step 2: Attach metadata from Layer 2
    nodes = attach_metadata(nodes, layer2_output)
    
    # Step 3: Merge duplicates and overlaps (NEW)
    nodes = merge_duplicate_nodes(nodes, tolerance=0.1)
    
    # Step 4: Build relationships (NEW)
    edges = build_relationships(nodes, tolerance=0.3)
    
    # Step 5: Assign levels (NEW)
    nodes = assign_levels(nodes, layer2_output)
    
    # Step 6: Integrate confidence (NEW)
    nodes = integrate_confidence(nodes)
    
    # Step 7: Compute statistics
    statistics = compute_graph_statistics(nodes, edges)
    
    # Step 8: Validate graph
    validation = validate_canonical_graph(nodes, edges)
    
    # Build final canonical model
    canonical_model = {
        'elements': nodes,
        'relationships': edges,
        'statistics': statistics,
        'validation': validation,
        'metadata': {
            'source_layers': ['layer1', 'layer2', 'layer3', 'layer4'],
            'is_canonical': True,
            'version': '1.0'
        }
    }
    
    return {
        'success': True,
        'canonical_model': canonical_model,
        'summary': {
            'total_elements': len(nodes),
            'total_relationships': len(edges),
            'valid': validation['valid'],
            'avg_confidence': round(statistics['avg_confidence'], 2)
        }
    }
