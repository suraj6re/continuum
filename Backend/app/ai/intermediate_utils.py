import json
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def save_intermediate_representation(data: Dict, file_path: str, output_dir: str = None) -> str:
    """Save intermediate representation as normalized_drawing.json (STEP 9)
    
    Args:
        data: Pipeline output dictionary
        file_path: Original file path
        output_dir: Directory to save JSON (defaults to same as file)
    
    Returns:
        Path to saved JSON file
    """
    # Determine output directory
    if output_dir is None:
        output_dir = Path(file_path).parent
    else:
        output_dir = Path(output_dir)
    
    # Create filename
    original_name = Path(file_path).stem
    json_filename = f"{original_name}_normalized_drawing.json"
    json_path = output_dir / json_filename
    
    # Add metadata
    output_data = {
        'metadata': {
            'original_file': Path(file_path).name,
            'processed_at': datetime.now().isoformat(),
            'pipeline_version': '1.0'
        },
        **data
    }
    
    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    return str(json_path)

def extract_scale_candidates(text_entities: List[Dict]) -> List[Dict]:
    """Extract scale information from text entities (STEP 10)
    
    For now: Extract text containing "Scale" and store candidate values.
    Do NOT apply scale yet unless explicit dimension given.
    
    Args:
        text_entities: List of text entities with text, position, layer
    
    Returns:
        List of scale candidates with text, position, parsed_value
    """
    scale_candidates = []
    
    # Patterns to match scale text
    scale_patterns = [
        r'scale[:\s]+(\d+[\./:]?\d*)',  # "Scale: 1:100" or "Scale 1/100"
        r'(\d+)\s*[:/]\s*(\d+)',         # "1:100" or "1/100"
        r'1\s*=\s*(\d+)',                # "1 = 100"
    ]
    
    for text_entity in text_entities:
        text = text_entity.get('text', '').lower()
        
        # Check if text contains "scale"
        if 'scale' in text:
            # Try to extract scale value
            for pattern in scale_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    scale_candidates.append({
                        'text': text_entity.get('text', ''),
                        'position': text_entity.get('position', [0, 0]),
                        'layer': text_entity.get('layer', '0'),
                        'parsed_value': match.group(0),
                        'match_groups': match.groups()
                    })
                    break
    
    return scale_candidates
