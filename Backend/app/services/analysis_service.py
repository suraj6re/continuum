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
from app.ai.layer4_pipeline import run_layer4_pipeline
from app.ai.layer5_pipeline import run_layer5_pipeline
from app.ai.layer6_pipeline import run_layer6_pipeline

async def analyze_drawing(drawing_id: str) -> dict:
    """Analyze uploaded drawing using complete pipeline"""
    
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise ValueError("Drawing not found")
    
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
        
        drawing.layer2_processed = True
        drawing.layer2_data = layer2_output
        
        # Layer 3: Structural element detection
        layer3_output = run_layer3_pipeline(layer1_output, layer2_output)
        drawing.layer3_processed = True
        drawing.layer3_data = layer3_output
        
        # Layer 4: QTO
        layer4_output = run_layer4_pipeline(layer3_output)
        drawing.layer4_processed = True
        drawing.layer4_data = layer4_output
        
        # Layer 5: Canonical Model
        layer5_output = run_layer5_pipeline(layer1_output, layer2_output, layer3_output, layer4_output)
        drawing.layer5_processed = True
        drawing.layer5_data = layer5_output
        
        # Layer 6: Validation
        layer6_output = run_layer6_pipeline(layer4_output, layer3_output)
        drawing.layer6_processed = True
        drawing.layer6_data = layer6_output
        
        # Layers 7-10: Store empty data for now (frontend will use fallback)
        drawing.layer7_processed = False
        drawing.layer7_data = {}
        drawing.layer8_processed = False
        drawing.layer8_data = {}
        drawing.layer9_processed = False
        drawing.layer9_data = {}
        drawing.layer10_processed = False
        drawing.layer10_data = {}
        
        drawing.status = "analyzed"
        drawing.processed = True
        await drawing.save()
        
        return {
            'drawing_id': str(drawing.id),
            'status': 'success',
            'layers_processed': {
                'layer2': drawing.layer2_processed,
                'layer3': drawing.layer3_processed,
                'layer4': drawing.layer4_processed,
                'layer5': drawing.layer5_processed,
                'layer6': drawing.layer6_processed,
                'layer7': drawing.layer7_processed,
                'layer8': drawing.layer8_processed,
                'layer9': drawing.layer9_processed,
                'layer10': drawing.layer10_processed
            }
        }
    
    except Exception as e:
        drawing.status = "failed"
        drawing.processing_error = str(e)
        await drawing.save()
        raise ValueError(f"Analysis failed: {str(e)}")
