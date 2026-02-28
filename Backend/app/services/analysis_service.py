from app.models.drawing import Drawing
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_boundary import load_geometry_and_compute_extents
from app.ai.layer2_text_clustering import cluster_text_dbscan
from app.ai.layer2_title_block import identify_title_block
from app.ai.layer2_legend import detect_legend_region
from app.ai.layer2_schedule import detect_schedule_tables
from app.ai.layer2_region_tagging import tag_regions
from app.ai.layer2_output import build_layer2_output
from app.ai.layer3_pipeline import run_layer3_pipeline

async def analyze_drawing(drawing_id: str) -> dict:
    """
    Analyze uploaded drawing using complete 3-layer pipeline
    """
    
    # Get drawing from database
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise ValueError("Drawing not found")
    
    # Update status
    drawing.status = "analyzing"
    await drawing.save()
    
    try:
        # Layer 1: Geometry extraction
        layer1_output = route_preprocessing(drawing.file_path, drawing.file_type)
        
        # Layer 2: Semantic understanding
        text_entities = layer1_output.get('text', [])
        all_lines, extents = load_geometry_and_compute_extents(layer1_output)
        sheet_border = layer1_output.get('sheet_border')
        
        if len(text_entities) >= 4:
            labels, params = cluster_text_dbscan(text_entities)
            title_block = identify_title_block(text_entities, labels)
            legend_info = detect_legend_region(text_entities, labels, layer1_output)
            tables = detect_schedule_tables(layer1_output, text_entities)
            region_tags = tag_regions(text_entities, title_block, legend_info, tables, sheet_border)
            layer2_output = build_layer2_output(sheet_border, title_block, legend_info, 
                                                tables, region_tags, layer1_output)
        else:
            layer2_output = {'drawing_region': {'bbox': sheet_border}}
        
        # Layer 3: Structural element detection
        layer3_output = run_layer3_pipeline(layer1_output, layer2_output)
        
        # Update drawing with results
        drawing.status = "analyzed"
        await drawing.save()
        
        return {
            'drawing_id': str(drawing.id),
            'status': 'success',
            'layer3_output': layer3_output
        }
    
    except Exception as e:
        drawing.status = "failed"
        await drawing.save()
        raise ValueError(f"Analysis failed: {str(e)}")
