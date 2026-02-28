from typing import Dict, List, Optional

def build_layer2_output(sheet_border: Optional[Dict], title_block: Optional[Dict],
                        legend_info: Optional[Dict], schedule_tables: List[Dict],
                        region_tags: Dict, layer1_output: Dict) -> Dict:
    """Build structured Layer 2 output for Layer 3
    
    Args:
        sheet_border: Sheet border bbox
        title_block: Title block info
        legend_info: Legend region info
        schedule_tables: List of schedule tables
        region_tags: Region tagging results
        layer1_output: Original Layer 1 output
    
    Returns:
        Structured Layer 2 output
    """
    # Extract scale info
    scale_info = None
    if title_block and 'scale_info' in title_block:
        scale_data = title_block['scale_info']
        if scale_data.get('status') == 'found':
            scale_info = {
                'numerator': scale_data['numerator'],
                'denominator': scale_data['denominator'],
                'ratio': scale_data['ratio'],
                'raw_text': scale_data['raw_text']
            }
    
    # Build drawing region (everything not in other regions)
    drawing_region = {
        'bbox': sheet_border if sheet_border else layer1_output.get('bounding_box'),
        'text_count': region_tags['region_counts'].get('drawing', 0),
        'texts': [t for t in region_tags['tagged_texts'] if t['role'] == 'drawing']
    }
    
    # Build title block region
    title_block_region = None
    if title_block:
        title_block_region = {
            'bbox': title_block.get('bounding_box'),
            'metadata': title_block.get('metadata', {}),
            'text_count': region_tags['region_counts'].get('title_block', 0),
            'texts': [t for t in region_tags['tagged_texts'] if t['role'] == 'title_block']
        }
    
    # Build legend region
    legend_region = None
    legend_dictionary = {}
    if legend_info and legend_info.get('status') == 'found':
        legend_region = {
            'bbox': legend_info.get('bounding_box'),
            'expanded_bbox': legend_info.get('expanded_bbox'),
            'shape_count': legend_info.get('shape_count', 0),
            'text_count': region_tags['region_counts'].get('legend', 0),
            'texts': [t for t in region_tags['tagged_texts'] if t['role'] == 'legend']
        }
        legend_dictionary = legend_info.get('legend_dictionary', {})
    
    # Build schedule regions
    schedule_regions = []
    schedules = {}
    for idx, table in enumerate(schedule_tables):
        schedule_key = f'schedule_{idx}'
        schedule_regions.append({
            'bbox': table['bbox'],
            'grid': f"{table['rows']}x{table['cols']}",
            'grid_score': table['grid_score']
        })
        
        if table.get('parsed_data'):
            schedules[schedule_key] = {
                'headers': table['parsed_data']['headers'],
                'data': table['parsed_data']['data'],
                'row_count': table['parsed_data']['row_count'],
                'col_count': table['parsed_data']['col_count']
            }
    
    # Build final output
    layer2_output = {
        'drawing_region': drawing_region,
        'title_block_region': title_block_region,
        'scale_info': scale_info,
        'legend_region': legend_region,
        'legend_dictionary': legend_dictionary,
        'schedule_regions': schedule_regions,
        'schedules': schedules,
        'region_statistics': {
            'total_texts': region_tags['total_texts'],
            'region_counts': region_tags['region_counts']
        },
        'layer1_reference': {
            'entity_count': layer1_output.get('entity_count', {}),
            'bounding_box': layer1_output.get('bounding_box'),
            'units': layer1_output.get('units')
        }
    }
    
    return layer2_output
