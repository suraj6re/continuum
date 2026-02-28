import numpy as np
from typing import List, Dict, Optional, Tuple
import math
from collections import defaultdict

def detect_schedule_tables(layer1_output: Dict, text_entities: List[Dict]) -> List[Dict]:
    """Detect and parse schedule tables from grid structures
    
    Args:
        layer1_output: Layer 1 output with geometry
        text_entities: List of text entities
    
    Returns:
        List of detected tables with parsed data
    """
    # Extract all lines
    all_lines = _extract_all_lines(layer1_output)
    
    if len(all_lines) < 4:
        return []
    
    # Separate horizontal and vertical lines
    horizontal_lines, vertical_lines = _separate_lines_by_orientation(all_lines)
    
    if len(horizontal_lines) < 2 or len(vertical_lines) < 2:
        return []
    
    # Cluster lines to find grid structures
    h_clusters = _cluster_parallel_lines(horizontal_lines, axis='y')
    v_clusters = _cluster_parallel_lines(vertical_lines, axis='x')
    
    # Find grid intersections
    tables = _detect_grid_tables(h_clusters, v_clusters, text_entities)
    
    return tables

def _extract_all_lines(layer1_output: Dict) -> List[Dict]:
    """Extract all line entities from Layer 1 output
    
    Args:
        layer1_output: Layer 1 output
    
    Returns:
        List of line dicts with start, end, angle, length
    """
    lines = []
    geometry = layer1_output.get('geometry', {})
    
    # Extract LINE entities
    if 'LINE' in geometry:
        for entity in geometry['LINE']:
            coords = entity.get('coordinates', [])
            if len(coords) >= 2:
                start, end = coords[0], coords[1]
                start_x = start.get('x') if isinstance(start, dict) else start.x
                start_y = start.get('y') if isinstance(start, dict) else start.y
                end_x = end.get('x') if isinstance(end, dict) else end.x
                end_y = end.get('y') if isinstance(end, dict) else end.y
                
                dx = end_x - start_x
                dy = end_y - start_y
                angle = math.degrees(math.atan2(dy, dx)) % 180
                length = math.sqrt(dx**2 + dy**2)
                
                lines.append({
                    'start': [start_x, start_y],
                    'end': [end_x, end_y],
                    'angle': angle,
                    'length': length
                })
    
    return lines

def _separate_lines_by_orientation(lines: List[Dict], tolerance: float = 5.0) -> Tuple[List[Dict], List[Dict]]:
    """Separate lines into horizontal and vertical
    
    Args:
        lines: List of line dicts
        tolerance: Angle tolerance in degrees
    
    Returns:
        Tuple of (horizontal_lines, vertical_lines)
    """
    horizontal = []
    vertical = []
    
    for line in lines:
        angle = line['angle']
        
        # Horizontal: angle near 0° or 180°
        if angle < tolerance or angle > (180 - tolerance):
            horizontal.append(line)
        # Vertical: angle near 90°
        elif abs(angle - 90) < tolerance:
            vertical.append(line)
    
    return horizontal, vertical

def _cluster_parallel_lines(lines: List[Dict], axis: str = 'y') -> List[List[Dict]]:
    """Cluster parallel lines by their position on perpendicular axis
    
    Args:
        lines: List of line dicts
        axis: 'x' for vertical lines, 'y' for horizontal lines
    
    Returns:
        List of line clusters
    """
    if not lines:
        return []
    
    # Get positions on the perpendicular axis
    positions = []
    for line in lines:
        if axis == 'y':
            # For horizontal lines, use Y coordinate
            pos = (line['start'][1] + line['end'][1]) / 2
        else:
            # For vertical lines, use X coordinate
            pos = (line['start'][0] + line['end'][0]) / 2
        positions.append(pos)
    
    # Sort lines by position
    sorted_indices = np.argsort(positions)
    sorted_lines = [lines[i] for i in sorted_indices]
    sorted_positions = [positions[i] for i in sorted_indices]
    
    # Cluster by proximity
    clusters = []
    current_cluster = [sorted_lines[0]]
    
    # Compute adaptive threshold (5% of range)
    pos_range = max(sorted_positions) - min(sorted_positions)
    threshold = max(pos_range * 0.05, 1.0)
    
    for i in range(1, len(sorted_lines)):
        if sorted_positions[i] - sorted_positions[i-1] < threshold:
            current_cluster.append(sorted_lines[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [sorted_lines[i]]
    
    clusters.append(current_cluster)
    
    return clusters

def _detect_grid_tables(h_clusters: List[List[Dict]], v_clusters: List[List[Dict]], 
                        text_entities: List[Dict]) -> List[Dict]:
    """Detect grid tables from line clusters
    
    Args:
        h_clusters: Horizontal line clusters
        v_clusters: Vertical line clusters
        text_entities: Text entities
    
    Returns:
        List of detected tables
    """
    tables = []
    
    # Need at least 2 horizontal and 2 vertical clusters for a table
    if len(h_clusters) < 2 or len(v_clusters) < 2:
        return tables
    
    # Get representative positions for each cluster
    h_positions = [_get_cluster_position(cluster, axis='y') for cluster in h_clusters]
    v_positions = [_get_cluster_position(cluster, axis='x') for cluster in v_clusters]
    
    # Sort positions
    h_positions.sort()
    v_positions.sort()
    
    # Compute grid score
    grid_score = len(h_positions) * len(v_positions)
    
    if grid_score < 4:  # At least 2x2 grid
        return tables
    
    # Extract cells
    cells = []
    for i in range(len(v_positions) - 1):
        for j in range(len(h_positions) - 1):
            cell = {
                'bbox': {
                    'min_x': v_positions[i],
                    'min_y': h_positions[j],
                    'max_x': v_positions[i + 1],
                    'max_y': h_positions[j + 1]
                },
                'row': j,
                'col': i,
                'texts': []
            }
            cells.append(cell)
    
    # Map text to cells
    for text in text_entities:
        text_pos = text['position']
        for cell in cells:
            if _is_point_in_bbox(text_pos, cell['bbox']):
                cell['texts'].append(text['text'])
    
    # Parse table structure
    table_data = _parse_table_structure(cells, len(h_positions) - 1, len(v_positions) - 1)
    
    if table_data:
        tables.append({
            'grid_score': grid_score,
            'rows': len(h_positions) - 1,
            'cols': len(v_positions) - 1,
            'bbox': {
                'min_x': v_positions[0],
                'min_y': h_positions[0],
                'max_x': v_positions[-1],
                'max_y': h_positions[-1]
            },
            'cells': cells,
            'parsed_data': table_data
        })
    
    return tables

def _get_cluster_position(cluster: List[Dict], axis: str) -> float:
    """Get representative position of a line cluster
    
    Args:
        cluster: List of lines
        axis: 'x' or 'y'
    
    Returns:
        Average position
    """
    positions = []
    for line in cluster:
        if axis == 'y':
            pos = (line['start'][1] + line['end'][1]) / 2
        else:
            pos = (line['start'][0] + line['end'][0]) / 2
        positions.append(pos)
    
    return sum(positions) / len(positions)

def _is_point_in_bbox(point: List[float], bbox: Dict) -> bool:
    """Check if point is inside bounding box
    
    Args:
        point: [x, y] coordinates
        bbox: Bounding box dict
    
    Returns:
        True if point is inside bbox
    """
    return (bbox['min_x'] <= point[0] <= bbox['max_x'] and 
            bbox['min_y'] <= point[1] <= bbox['max_y'])

def _parse_table_structure(cells: List[Dict], num_rows: int, num_cols: int) -> Optional[Dict]:
    """Parse table structure into header and data rows
    
    Args:
        cells: List of cell dicts
        num_rows: Number of rows
        num_cols: Number of columns
    
    Returns:
        Parsed table data or None
    """
    if num_rows < 2:  # Need at least header + 1 data row
        return None
    
    # Organize cells into grid
    grid = [[None for _ in range(num_cols)] for _ in range(num_rows)]
    
    for cell in cells:
        row, col = cell['row'], cell['col']
        if row < num_rows and col < num_cols:
            grid[row][col] = cell
    
    # Extract header (first row)
    headers = []
    for col in range(num_cols):
        if grid[0][col] and grid[0][col]['texts']:
            headers.append(' '.join(grid[0][col]['texts']))
        else:
            headers.append(f'Column_{col}')
    
    # Extract data rows
    data_rows = []
    for row in range(1, num_rows):
        row_data = {}
        for col in range(num_cols):
            if grid[row][col] and grid[row][col]['texts']:
                row_data[headers[col]] = ' '.join(grid[row][col]['texts'])
            else:
                row_data[headers[col]] = ''
        
        # Only add non-empty rows
        if any(row_data.values()):
            data_rows.append(row_data)
    
    return {
        'headers': headers,
        'data': data_rows,
        'row_count': len(data_rows),
        'col_count': num_cols
    }
