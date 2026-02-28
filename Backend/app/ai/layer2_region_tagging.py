from typing import List, Dict, Optional

def tag_regions(text_entities: List[Dict], title_block: Optional[Dict], 
                legend_info: Optional[Dict], schedule_tables: List[Dict],
                sheet_border: Optional[Dict]) -> Dict:
    """Tag text entities by their region (title block, legend, schedule, drawing)
    
    Args:
        text_entities: List of text dicts with 'text' and 'position'
        title_block: Title block info with bounding_box
        legend_info: Legend info with bounding_box
        schedule_tables: List of schedule tables with bbox
        sheet_border: Sheet border bbox
    
    Returns:
        Dict with tagged texts and region statistics
    """
    tagged_texts = []
    region_counts = {
        'title_block': 0,
        'legend': 0,
        'schedule': 0,
        'drawing': 0
    }
    
    # Define region bboxes with small margin (0.5% expansion)
    title_block_bbox = _expand_bbox(title_block.get('bounding_box')) if title_block else None
    legend_bbox = _expand_bbox(legend_info.get('bounding_box')) if legend_info and legend_info.get('status') == 'found' else None
    schedule_bboxes = [_expand_bbox(table['bbox']) for table in schedule_tables]
    
    # Tag each text entity
    for text in text_entities:
        position = text['position']
        role = _assign_role(position, title_block_bbox, legend_bbox, schedule_bboxes)
        
        tagged_texts.append({
            'text': text['text'],
            'position': position,
            'role': role,
            'layer': text.get('layer', '0')
        })
        
        region_counts[role] += 1
    
    return {
        'tagged_texts': tagged_texts,
        'region_counts': region_counts,
        'total_texts': len(text_entities)
    }

def _assign_role(position: List[float], title_block_bbox: Optional[Dict],
                 legend_bbox: Optional[Dict], schedule_bboxes: List[Dict]) -> str:
    """Assign role to text based on spatial containment
    
    Args:
        position: [x, y] coordinates
        title_block_bbox: Title block bounding box
        legend_bbox: Legend bounding box
        schedule_bboxes: List of schedule bounding boxes
    
    Returns:
        Role string: 'title_block', 'legend', 'schedule', or 'drawing'
    """
    # Priority order: title_block > legend > schedule > drawing
    
    # Check title block (highest priority)
    if title_block_bbox and _is_point_in_bbox(position, title_block_bbox):
        return 'title_block'
    
    # Check legend
    if legend_bbox and _is_point_in_bbox(position, legend_bbox):
        return 'legend'
    
    # Check schedule tables
    for idx, schedule_bbox in enumerate(schedule_bboxes):
        if _is_point_in_bbox(position, schedule_bbox):
            return 'schedule'
    
    # Default: drawing region
    return 'drawing'

def _is_point_in_bbox(point: List[float], bbox: Dict) -> bool:
    """Check if point is inside bounding box
    
    Args:
        point: [x, y] coordinates
        bbox: Bounding box with min_x, min_y, max_x, max_y
    
    Returns:
        True if point is inside bbox
    """
    return (bbox['min_x'] <= point[0] <= bbox['max_x'] and 
            bbox['min_y'] <= point[1] <= bbox['max_y'])

def _expand_bbox(bbox: Optional[Dict], margin_ratio: float = 0.005) -> Optional[Dict]:
    """Expand bounding box by small margin to avoid borderline misses
    
    Args:
        bbox: Original bounding box
        margin_ratio: Ratio to expand (default 0.5%)
    
    Returns:
        Expanded bounding box or None
    """
    if not bbox:
        return None
    
    width = bbox['max_x'] - bbox['min_x']
    height = bbox['max_y'] - bbox['min_y']
    
    margin_x = width * margin_ratio
    margin_y = height * margin_ratio
    
    return {
        'min_x': bbox['min_x'] - margin_x,
        'min_y': bbox['min_y'] - margin_y,
        'max_x': bbox['max_x'] + margin_x,
        'max_y': bbox['max_y'] + margin_y
    }
